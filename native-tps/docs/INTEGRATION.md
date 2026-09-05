# Integration contracts

## Local Core ML image models

The app consumes a manifest JSON and adjacent `.mlmodel` file. This first
adapter accepts Core ML neural-network files; arbitrary PyTorch checkpoints,
ONNX files and `.mlpackage` ML Programs require an adapter extension/conversion.
No Core ML model is bundled. The model is SHA-256 checked before compilation.
Choose the manifest separately for each operation in **Local models**.

```json
{
  "schemaVersion": 1,
  "modelID": "research/pelvis-contour-v1",
  "version": "checkpoint-version",
  "operation": "contour",
  "modelFile": "contour.mlmodel",
  "modelSHA256": "REPLACE_WITH_64_CHARACTER_SHA256_OF_MODEL_FILE",
  "dimensions": [64, 64, 64],
  "inputOffset": 1000,
  "inputScale": 0.0004,
  "inputClip": [-1000, 1500],
  "outputScale": 1,
  "outputOffset": 0,
  "structures": [
    {"id": 1, "name": "Your actual class name", "color": [0.3, 0.8, 0.7]}
  ],
  "intendedUse": "synthetic-research-only"
}
```

The example is intentionally not a runnable model manifest until replaced with
real model metadata. Do not use the displayed normalization values without
matching training preprocessing.

Tensor contract:

- Spatial metadata dimensions are **[X,Y,Z]**; scalar storage is X-fastest.
- Core ML tensors are Float32 **[1,1,Z,Y,X]**.
- `image` is CT for contour/dose and MR signal for synthetic CT.
- Input transform is `(clip(value, low, high) + inputOffset) * inputScale`.
- Dose models also take `structures`, the raw phantom-truth integer label IDs
  in a Float32 tensor with the same shape. One-hot channel models need export
  wrappers; missing structures are never inferred from text.
- `output` must have exactly the same tensor shape. Output transform is
  `value * outputScale + outputOffset`.
- Contour output must already be an integer label map, not logits/probabilities;
  the manifest includes the exact class dictionary.
- Dose output is non-negative finite Gy; sCT output is finite HU.
- Grid resampling, patch stitching and native geometry restoration belong in
  the exported model/adapter and require independent tests. This app rejects
  changed or unsupported geometry instead of guessing a transform.
- Core ML compute units are `.all`, allowing the runtime to select supported
  CPU/GPU/Neural Engine paths; actual accelerator selection is not guaranteed.
  Float32 inputs/outputs do not imply Float32 internal arithmetic. The identity
  contract test observed Float16 rounding (maximum absolute difference about
  0.0624 on values up to 223). Real model validation must include the deployed
  accelerator and precision, not only the original training framework.

## Spark phantom adapter

### Supplied Docker launch template

The supplied runtime/anatomy locations and `linux/amd64` invocation are captured
in `config/spark-xcat2.example.json`, a multi-stage pipeline reference supplied
by the Spark project. It records base/lesion passes, sentinel labels, and DICOM/NPZ
converter contracts. It is not executable by the single-job native launcher.
`config/spark-xcat2-launcher.example.json` separately preserves the launcher schema
and copies the supplied image pin and mount paths.
`scripts/run_xcat2_container.py` implements this command as a subprocess argv
array, preserving both read-only input mounts and the per-job writable `/out`
mount. It does not execute a shell string.

Preview the normalized template on either machine without launching Docker:

```sh
python3 scripts/run_xcat2_container.py \
  --config config/spark-xcat2-launcher.example.json --print-template
```

Before enabling execution, copy the launcher example to `local-config.json` on
the Spark and complete:

- `image`: the supplied digest is populated; verify availability on the Spark.
- `xcat_arguments`: the verified argument array; explicitly `[]` only if no
  additional arguments are needed. No XCAT flags are guessed by this project.
- `supported_recipe`: the exact native recipe implemented by that parameter
  file/argument set. Until a real parameter mapper is supplied, other recipes
  are rejected rather than silently ignored.
- `converter_argv`: an absolute local converter command with `{raw_prefix}`,
  `{recipe}` and `{output}` placeholders. It must convert the actual XCAT
  output to the native case contract below and retain generator provenance.

The HTTP adapter's command file can then invoke this wrapper:

```json
["/absolute/path/to/python3", "/absolute/path/to/run_xcat2_container.py", "--config", "/absolute/path/to/local-config.json", "--recipe", "{recipe}", "--output", "{output}"]
```

Docker output uses a fresh request directory. On timeout the wrapper removes
only its uniquely named container. The current synchronous adapter allows 110
seconds for XCAT and at most 130 seconds total for generation/conversion, below
the outer adapter's 150-second limit. Use the existing batch workflow for long
simulations. Mounting `/anatomy` alone does not prove `general.samp.par` references
that directory; its anatomy references still need inspection on the Spark.

This launch template runs XCAT2 only. It does not supply an OpenTOPAS/nBio
invocation, a transport configuration, a paired MR generator or an output
converter. Those components remain explicit integration inputs.

### Service setup

XCAT2 and OpenTOPAS/nBio are installed on the user's DGX Spark. Their exact
runtime/anatomy paths, image digest, case-001 base/lesion arguments and pipeline
conversion contracts have been supplied. `scripts/convert_spark_case.py` converts
the Spark CT DICOM, native XCAT mask NPZ and OpenTOPAS dose array into a native
case JSON while recording the XCAT plan, parameter-file and image digests. The
existing source pipeline produces CT, labels and dose. MR is optional in the
native case contract. The converter emits no MR channel and no longer accepts
`--synthetic-mr`. CT-only cases support contour and dose workflows; synthetic-CT
inference/training requires usable MR input. Native import retains
`sourceNotes`; legacy placeholder MR remains blocked from synthetic-CT workflows.
The File menu can remove an explicitly marked placeholder from a case with no
derived artifacts, recording the previous and revised source hashes in the audit.
Lymph nodes are intentionally excluded. `scripts/spark_phantom_adapter.py`
is a runnable loopback-only wrapper around an explicitly configured local command.

Example completed-case conversion on Spark:

```sh
python3 scripts/convert_spark_case.py \
  --case-id VCT-PROSTATE-001 \
  --ct-dir /spark/dicom/VCT-PROSTATE-001/CT/BASELINE \
  --masks /spark/masks/VCT-PROSTATE-001/masks.npz \
  --dose /spark/dose/VCT-PROSTATE-001/combined_dose.npy \
  --plan-json /spark/plans/VCT-PROSTATE-001.json \
  --parameter-file /spark/xcat/XCAT_latest/general.samp.par \
  --image-digest ubuntu@sha256:<pinned-digest> \
  --output /spark/native-cases/VCT-PROSTATE-001.json
```

On the Spark, prepare a JSON argv file resembling this (replace every path):

```json
["/absolute/path/to/your-phantom-wrapper", "--recipe", "{recipe}", "--output", "{output}"]
```

The wrapper must read the validated recipe and write a native case JSON. It is
responsible for actually invoking the licensed XCAT2 program, running the
appropriate OpenTOPAS/nBio jobs, converting coordinates/units, and recording
versions. The adapter does not accept executable paths or commands from HTTP
requests and never uses `shell=True`.

```sh
# On the Spark, after installing/configuring the wrapper:
python3 spark_phantom_adapter.py --command-file /path/to/local-command.json

# On the Mac, using your actual SSH host alias:
ssh -N -L 8105:127.0.0.1:8105 spark-wired
```

In Phantom lab, set `http://127.0.0.1:8105`. The app sends `POST /v1/phantoms`:

```json
{"anatomyID":"ANATOMY-001","seed":42,"bodyScale":1,"targetRadiusMM":18,"motionPhase":0,"nBioProfile":"your-reviewed-profile-id"}
```

These normalized recipe fields describe this prototype's contract, not native
XCAT or nBio parameter names. Your wrapper maps supported fields explicitly;
reject unsupported fields/profile IDs rather than passing free text to a shell
or simulation parameter file.

The version 1 adapter is synchronous and single-job, with a 150-second generator
timeout and 96 MB result limit. Large XCAT/nBio jobs should run in the existing
Spark batch workflow and have their completed case imported as JSON. A durable
asynchronous queue, progress, cancellation, authenticated job ownership and
large-array transport are future integration work. The app does not claim the
Spark is connected until a real response is received.

## Native synthetic case

`swift run tps-check build/smoke` writes a complete executable example to
`build/smoke/synthetic-case.json`. This generated fixture illustrates the wire
format without pretending to be XCAT/nBio output.

Top-level fields: `schemaVersion: 1`, UUID `id`, `name`, `generator`,
`generatorVersion`, `syntheticOnly: true`, `recipe`, `ct`, optional `mr`, `truth`,
`structures`, and optional `simulation`.

Volumes have `grid`, `modality`, `units`, and a flat `values` array. Grid fields
are `dimensions`, `spacing`, `origin`, `direction`, and `frameID`. Spacing/origin
are millimetres in LPS; the 3×3 row-major orthonormal right-handed direction
matrix maps scaled voxel XYZ into LPS. All case grids must agree exactly.
Valid units are CT `HU`, MR `a.u.`, dose `Gy`, labels `label`. Background is 0;
every positive label must exist in the structure dictionary.

CT and truth must share a grid; MR, when provided, must match it. Generators
without MR should omit `mr` entirely. Do not fabricate an MR channel to satisfy
import. JSON cases are limited to 8,388,608 voxels and 96 MB at the HTTP/import
boundary, so this is a small-volume prototype rather than production DICOM I/O.

Optional simulation evidence has:

```text
transportEngine          e.g. actual OpenTOPAS engine identity
transportVersion         exact installed version
nBioVersion              exact extension version
parameterFileSHA256      digest of the actual parameter bundle
histories                number of simulated histories, > 0
normalization            explicit history/fluence/prescription normalization description
referenceDose            separate, aligned physical dose volume in Gy
observations[]           scorer, region, value, units, standardError
```

Biological scorer measurements are stored as observations. There is no automatic
conversion to clinical RBE/TCP/NTCP or dose normalization. The fixture leaves
`simulation` absent and uses `nBioProfile: "unbound"`.

## Training-data handoff

The app exports a `ResearchBundle` containing source, reviewed artifacts, review
records, audit events, source hash, intended use and anatomy split. The Python
converter invokes the native `tps-check --validate-bundle` executable before
converting arrays, avoiding cross-language float-serialization differences in
hash verification. Neither that check nor the local audit is a digital signature.

```sh
swift build
python3 scripts/prepare_dataset.py /path/to/research-bundle.json \
  --task syntheticCT --output /path/to/new-dataset-directory
```

Outputs are NPZ arrays `image`, `target`, and `structures` in **Z,Y,X** order,
plus a dataset manifest with anatomy splits, recipe, geometry, structure map,
file digests, generator identity and optional biological observations. `contour`
pairs source CT with source truth; `syntheticCT` pairs source MR with source CT;
`predictDose` uses only separately recorded transport reference dose.

The output directory must be new. Analytic fixtures require explicit
`--allow-fixture`. No converter option allows a predicted artifact to replace a
transport reference dose. Dataset approval remains `pending`; no training,
evaluation or clinical model promotion is performed by this converter.
