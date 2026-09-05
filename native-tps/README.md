# Governed TPS — native macOS research workstation

A separate SwiftUI/Xcode application for building governed, local AI workflows
around contouring, dose prediction, synthetic CT, and synthetic training data.
All implementation, build settings, tests, and adapter documentation live in
this folder. It imports no code, policies, specifications or dependencies from
the existing browser TPS. The parent repository's controlled baseline is not
modified or claimed as realized by this prototype.

**Status:** runnable research foundation, not a complete or commissioned TPS.
Only synthetic data is supported. There is no clinical approval, prescription,
beam optimization, machine delivery, or DICOM RTPLAN export path.

## Open in Xcode

1. Open `GovernedTPS.xcodeproj`.
2. Select the **GovernedTPS** scheme and **My Mac** destination.
3. Press **⌘R** to run; **⌘U** runs the core tests.

Requires macOS 14+ and Swift 6. Built with Xcode 26.3 on Apple silicon. No
third-party Swift packages, signing team, cloud API key, or image-model download
is required to run the fixture workflow. The development app is unsandboxed;
distribution signing, entitlements and authenticated operator identity are
separate work.

```sh
swift test
swift run tps-check build/smoke
xcodebuild -project GovernedTPS.xcodeproj -scheme GovernedTPS \
  -destination 'platform=macOS,arch=arm64' -derivedDataPath build/DerivedData \
  CODE_SIGNING_ALLOWED=NO build
```

The checked-in project can be reproduced with
`python3 scripts/generate_xcode_project.py`. Regenerate it after adding app or
test Swift source files. The core is discovered automatically by SwiftPM.

## Working workflow

1. **Workspace:** create an analytic synthetic phantom or import a native case
   JSON. View three voxel planes, adjust CT window/level, browse axial slices,
   and overlay phantom truth outlines.
2. **Model Predict:** run contour, dose or synthetic-CT operations. The built-in
   analytic fixture runs without model weights. Real compatible models use
   **Core ML on this Mac** and the manifests chosen in **Local models**.
3. **Agent workbench:** choose a professional workflow assistant, write a task,
   compile a proposal using local Ollama, inspect the operations, then confirm
   execution. Outputs enter the same review queue as manual model runs.
4. **Review & evidence:** inspect outputs, enter a local reviewer name and note,
   and accept for research or reject. Reviews bind to artifact digests.
5. **Phantom lab:** configure reproducible recipes and an XCAT2/OpenTOPAS-nBio
   adapter on the DGX Spark; export reviewed research bundles for dataset work.

Results autosave atomically to `~/Library/Application Support/GovernedTPS/workspace.json`.
The app validates the workspace on load; a corrupt file is reported rather than
silently replaced on startup. Use **File → Save workspace copy** for portable
snapshots. Model manifests and runtime endpoint selections are currently
session configuration and must be reselected after restart.

## Compute placement and selected models

**Mac:** app, Core ML image inference, and Ollama language inference.
**DGX Spark:** licensed XCAT2 generation and OpenTOPAS/nBio simulations only.
Language inference rejects non-loopback endpoints and cloud-labelled model tags.
The Spark adapter should be reached through an SSH tunnel.

On the inspected Mac, 128 GiB memory and existing `qwen3-coder:30b` and `qwen3:4b`
installations were detected. The default is **Qwen3 Coder 30B** for bounded
workflow/tool orchestration; **Qwen3 4B** is the smaller fallback. These choices
do not imply clinical reasoning competence. Qwen3.5 9B and 35B-A3B are documented
upgrade candidates to benchmark, not automatically downloaded replacements.
See [model selection](docs/MODELS.md) for rationale, sources and evaluation gates.

## Implemented vs. external integration

| Capability | This build |
|---|---|
| Native macOS UI | SwiftUI workstation, agents, phantoms, model registry, review/audit |
| Image display | Actual voxel slices, spatial metadata checks, overlays, cumulative DVH |
| Input format | Versioned synthetic JSON volume bundle; no DICOM/NIfTI parser |
| Image-model execution | Core ML loader, checksum pinning, explicit tensor/normalization contract |
| Trained weights | Not bundled; user-supplied exports must match the contract |
| Offline fixture | Reproducible analytic CT/MR/labels; heuristic contour, dose, sCT outputs |
| Local LLM | Live Ollama structured-output client and role-scoped execution |
| Governance | Typed operations, human confirmation, review hash binding, local audit chain |
| Phantom generator | Mac HTTP client and configurable Spark-side subprocess adapter |
| XCAT2/nBio engine connection | Actual host/paths/command and licensed engine remain to be configured |
| nBio integration | Transport-dose and biological-score evidence carried separately in source cases |
| Training data | Anatomy-grouped NPZ converter; predictions cannot become ground truth |
| Training / clinical validation | Not performed; no model promotion or clinical-release function |

## Tests and integration contracts

- [Architecture and invariants](docs/ARCHITECTURE.md)
- [Core ML, phantom and dataset contracts](docs/INTEGRATION.md)
- [Model decisions and primary sources](docs/MODELS.md)
- [Verification record](docs/VERIFICATION.md)

```sh
python3 -m unittest discover -s tests_python -v
python3 scripts/prepare_dataset.py build/smoke/research-bundle.json \
  --task contour --allow-fixture --output build/contour-smoke
swift run tps-check --llm-model qwen3-coder:30b
```

An optional untrained Core ML identity-network integration test exercises the
actual Apple runtime without downloading trained weights:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install coremltools
.venv/bin/python scripts/create_coreml_fixture.py --output build/coreml-fixture
swift run tps-check --coreml-fixture build/coreml-fixture/manifest.json
```

The test accepts only identity values or their IEEE Float16-rounded equivalents,
because accelerators may use reduced internal precision despite Float32 IO.
The generated network is labelled `isFixture: true` and has no predictive value.

The dataset converter requires NumPy, independently of the native app. Fixture
data is rejected by default; `--allow-fixture` permits pipeline tests, not model
validation. Dose training always requires separately identified transport
reference dose, even when fixtures are permitted.

No changes, commits, deployments, or approval records are made in the parent
application by this project. Third-party models and XCAT2 remain subject to
their own licenses. The parent repository's licensing notice remains applicable.

## iPad field review

A separate touch-first iPad prototype is in [iPad/README.md](iPad/README.md).
Open `iPad/GovernedTPSiPad.xcodeproj` for CT review, slice-bound Pencil markup,
offline notes and compact review handoff. Mac inference and Spark simulation
remain in their existing environments.
