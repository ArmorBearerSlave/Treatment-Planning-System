# matRad desktop planning

The **matRad planning** workspace runs photon dose calculation and fluence optimization using MATLAB on this Mac. It uses the existing matRad installation as a separate dependency. OpenTOPAS transport remains a separate Spark workflow; no automatic matRad-to-TOPAS beam conversion or validation is claimed.

## Using the application

1. Import a native synthetic CT case and select it in **Workspace**. This first adapter uses the case's supplied truth labels as planning structures. It does not automatically substitute AI contours or infer a target from a structure name.
2. Open **matRad planning**. The detected installation is MATLAB R2025b at `/Applications/MATLAB_R2025b.app/bin/matlab`, with matRad at `/Users/ericbrass/Documents/GitHub/matRad`. Both paths are editable. MATLAB must have a working license and an available supported optimizer.
3. Explicitly select the target label. Set total-course target Gy, fractions, target penalty, gantry angles and bixel width. Set each other structure's total-course overdose ceiling and penalty; zero penalty disables that objective. Defaults are research examples, not recommended clinical constraints.
4. **Prepare selected CT + objectives** validates and copies the source and request into a unique folder beneath `~/Library/Application Support/GovernedTPS/matrad-jobs/`. Review the frozen request, which is separate from subsequent form edits. Check the review box, then **Run dose calculation + optimization**.
5. Use **Refresh log** while MATLAB runs. A nonzero MATLAB exit or nonconverged optimizer produces no importable proposal. Source/request/bridge changes are rejected, as are repeated submissions to the same job. Keep the app open to receive completion automatically; **Open job…** can recover completed result files later. There is no scheduler, cancellation UI or automatic restart.
6. **Import dose proposal into Workspace** checks the result against the currently selected source case and frozen request. It displays dose overlays and DVHs and records an audit event. The result remains pending research review. It is explicitly labelled a matRad generic photon plan, rather than a learned model or transport reference.

**Show job files** reveals `source.json`, `request.json`, `job.json`, the exact adapter `.m`, `submitted.txt`, `matlab.log`, `exit-code.txt`, `plan.mat`, and (on successful convergence) `result.json`. matRad userdata generated during the job stays in its own folder. The existing matRad checkout and Spark batch folders are not edited.

## Scope and conventions

- First integration: Generic **photon** machine, physical dose, nominal scenario, coplanar beams, squared target-deviation and organ-overdose objectives. No MLC sequencing, DAO, deliverability check, biological optimization, proton/carbon planning, DICOM export, or learned-model training is enabled by this adapter.
- CT and labels must share an identity-direction LPS grid. Limits: four million voxels, nine beams, bixel width 5–30 mm. Oblique data is rejected. CT values are passed through matRad's default HU lookup table; this is not a scanner-specific calibration.
- Native storage is X-fastest XYZ. MATLAB cubes are YXZ. Explicit permutation is applied in each direction, retaining original LPS axis coordinates. Dose-grid axes and dimensions are checked against CT; there is no resampling.
- matRad divides total-course objectives by fraction count and produces physical per-fraction dose. The adapter multiplies by the requested fraction count exactly once and returns **physical-course-Gy**. No peak renormalization is applied.
- Successful fmincon exit flags (>0) and IPOPT statuses 0 or 1 are accepted. Other statuses preserve plan/log evidence but do not emit an importable dose. Convergence means numerical optimizer convergence, not satisfaction of every objective or clinical suitability.
- Generic machine, default HLUT, adapter and key matRad entrypoint SHA-256 digests, versions, optimizer status and normalization convention are captured. The artifact carries this planning evidence and the complete frozen request into research exports. These are local provenance records, not authenticated signatures or a fully frozen dependency environment. Do not execute untrusted job folders or MATLAB libraries.
- This adapter does not promote an optimized plan into ground truth. For dose-prediction training, distinguish optimized matRad targets from independently validated Monte Carlo reference dose. No MR acquisition, synthetic MR, or biological endpoint is created.

## Verification on 2026-09-05

Detected matRad `Cleve` v3.1.0 (`master-09944815`, checkout commit `09944815ff92b4fafc18d7882ad3d5cc732a5858`) and MATLAB 25.2 on Apple Silicon. The supplied IPOPT installation did not provide the required native Apple Silicon implementation; matRad selected the available MATLAB `fmincon` optimizer.

- Small CT-only phantom: dose calculation and fluence optimization converged.
- Asymmetric 12 × 14 × 10 fixture, spacing 2 × 3 × 4 mm: every CT index matched the saved MATLAB cube; every returned dose value matched the corresponding MATLAB dose multiplied by five fractions. `tps-check --validate-matrad` verified the source/request binding and computed six DVHs.
- Desktop job `E45FB619-E36A-46B1-84D7-53896494C088`: selected a target, froze a four-beam request, reviewed, launched MATLAB, loaded its converged dose, and imported it as a pending workspace proposal with DVHs. This was a software fixture, not a patient or model-performance study.
- Four targeted tests cover request round trips, invalid geometry/settings, changed source/request, wrong dose convention, nonconvergence, negative dose and clinical-release flags. Full native test suite: 38 tests passed. Xcode desktop build succeeded.

## Development and verification commands

From `native-tps`:

```sh
python3 scripts/generate_matrad_bridge.py
python3 scripts/generate_xcode_project.py
swift test
swift run tps-check --matrad-smoke-input build/matrad-new-fixture
```

The last command prepares an asymmetric input fixture but does not run MATLAB. Copy `scripts/matrad/tps_matrad_run.m` to that new job folder, then call `tps_matrad_run(jobFolder, matRadFolder)` in MATLAB. Validate the returned result with:

```sh
swift run tps-check --validate-matrad build/matrad-new-fixture
```

`scripts/matrad/tps_matrad_check_geometry.m` independently compares the asymmetric fixture with `plan.mat`, including five-fraction scaling. The embedded Swift adapter is generated from the `.m` source; regenerate it after edits.

The integration follows the installed API and the [official matRad repository](https://github.com/e0404/matRad). matRad is used under its own license; its implementation and machine files are not copied into this app.
