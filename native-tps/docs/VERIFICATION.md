# Verification record — 2026-09-04

This records engineering checks of the native prototype. It is not clinical
validation, independent plan QA, commissioned model evidence or a release approval.

| Check | Result | Evidence / limits |
|---|---|---|
| Swift package build and tests | PASS, 26 tests | Geometry, finite values, units, source/result identity, role restrictions, review binding, export rules, audit integrity, persistence, endpoint rejection |
| Xcode app build | PASS | `GovernedTPS` scheme, macOS arm64, Xcode 26.3, unsigned development build |
| Xcode test action | PASS, 26 tests | Shared scheme discovers and runs `TPSCoreTests` |
| Python dataset/adapter tests | PASS, 10 tests | Reject invalid recipes, NaNs, geometry mismatch, default fixture use and prediction-as-dose-truth |
| Synthetic integration runner | PASS | Generated case → three analytic outputs → test research reviews → bundle → six DVHs → save/load validation |
| Live local Ollama | PASS | Installed `qwen3-coder:30b` produced `inspect, contour` for a request explicitly prohibiting dose prediction |
| Actual Core ML runtime | PASS | Tiny untrained identity network compiled and predicted; preserved voxel order and fixture marker with exact-or-Float16-rounded values |
| Native GUI | PASS, sampled | App launches; analytic phantom, dose overlay and voxel-derived DVHs render; saved case/result restore after relaunch |
| Dataset conversion | PASS | Contour and MR→CT fixture NPZ datasets produced after native bundle validation; dataset approval stays pending |
| Existing repository isolation | PASS | Work performed only in `native-tps/`; no existing browser app or controlled specification edits |

The identity network reported maximum absolute rounding difference 0.06236267.
The integration assertion checks each output against either its exact input or
that input's IEEE Float16-rounded value (within 0.0001), not an arbitrary broad
error tolerance. This confirms the small fixture contract only, not precision
or accuracy of future 3D inference models.

The live language-model check initially exposed a schema-grammar incompatibility
in the installed runtime. The wire schema now uses basic JSON object/enum/array
constraints; Swift enforces maximum lengths, action count, uniqueness and role
scope independently. The live corrected request passed. This is one smoke
prompt, not a task benchmark or proof of general negation reliability.

## Reproduce

```sh
swift test
xcodebuild -project GovernedTPS.xcodeproj -scheme GovernedTPS \
  -destination 'platform=macOS,arch=arm64' -derivedDataPath build/DerivedData \
  CODE_SIGNING_ALLOWED=NO test
python3 -m unittest discover -s tests_python -v
swift run tps-check build/smoke
swift run tps-check --llm-model qwen3-coder:30b
.venv/bin/python scripts/create_coreml_fixture.py --output build/coreml-fixture
swift run tps-check --coreml-fixture build/coreml-fixture/manifest.json
```

Build logs, `.xcresult` bundles, generated fixtures, virtual environment and test
datasets are ignored build products under this folder. Coremltools 9.0 was
installed only in `native-tps/.venv` to generate the untrained fixture; on this
Python 3.14 environment its Python native-prediction extension is unavailable,
so compilation/prediction were performed through the actual Swift Core ML
runtime, not through Python. No trained model weights were downloaded.

## Not verified or not implemented

- Actual XCAT2/OpenTOPAS-nBio execution on the Spark: host/command not supplied.
- Trained dose, contour or synthetic-CT checkpoints: not supplied or evaluated.
- Clinical DICOM import/export, anatomical world-plane resampling, machine/beam
  modeling, optimization, physical dose authority or treatment delivery.
- Independent clinical/scientific assessment, authenticated signatures,
  external audit anchoring, model/dataset promotion, multi-user use or deployment.
- Full UI automation coverage, large-volume performance, long-running Spark jobs,
  cross-machine deployment, Intel builds, or every supported Core ML accelerator.

Configuration URLs and selected model manifests are session-only in this build.
Local model tags are recorded in workflow audit entries; immutable LLM digest
pinning and runtime-version capture remain future reproducibility work. The
Core ML image model file is SHA-256 pinned and snapshotted before compilation.

## XCAT2 launch-template follow-up

The user-supplied Docker template is recorded in
`config/spark-xcat2.example.json` and implemented by
`scripts/run_xcat2_container.py`. Six additional tests check platform/mount
preservation, argv token boundaries, missing pins/arguments, unmapped recipe
changes, mount-option injection, and parameter-file traversal. Docker and XCAT2
execution remain unverified; the example deliberately has null fields for the
missing pinned image, arguments, supported recipe and converter.
