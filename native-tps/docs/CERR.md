# Desktop CERR integration

The **CERR analysis** workspace runs the installed CERR library in a separate MATLAB process on this Mac. It transfers the selected synthetic native CT, exact truth-label masks and an explicitly selected dose into an analysis `planC`, calls CERR `getDVH` and `doseHist`, and compares the returned statistics with native voxel statistics.

## Use

1. In **Workspace**, choose the CT case and a dose result, such as a matRad proposal. Alternatively choose **Case simulation reference dose** in CERR when the case contains one.
2. Open **CERR analysis**. Confirm the MATLAB executable, CERR root and histogram bin width.
3. Click **Prepare CT + labels + dose**, review the frozen case, dose description and settings, then **Run CERR analysis**.
4. Inspect CERR mean dose and CERR-minus-native mean, D95 and volume differences. The maximum sampled-dose difference is also reported. There is no automatic clinical pass threshold.
5. **Record analysis in audit trail** binds the report hash, source hash, dose hash, request and job location to an audit event. This does not alter a proposal's review status. **Show analysis files** opens the output folder for export; **Open latest analysis** restores the most recently prepared local job. For another job, enter its folder or `job.json` path and click **Open saved path**. Both paths validate the frozen inputs and report.

Checked installation:

- MATLAB: `/Applications/MATLAB_R2025b.app/bin/matlab`
- CERR: `/Users/ericbrass/Documents/medical-physics-mbse/CERR/CERR-master`
- Local jobs: `~/Library/Application Support/GovernedTPS/cerr-jobs/<UUID>/`

Each job contains canonical `source.json`, `dose.json`, `request.json`, a frozen `tps_cerr_analyze.m`, `job.json`, `matlab.log`, a submission marker and exit code. Successful jobs add `planC.mat` and `report.json`. Separate MATLAB processes avoid sharing matRad's session path. Existing library files are not modified. An already-submitted job cannot be resubmitted; prepare a new snapshot to retry.

## Geometry and measurements

The initial bridge accepts synthetic cases on matching CT/label/dose grids with identity LPS direction, at least two voxels on each axis and at most four million voxels. Dose must be nonnegative Gy. It neither normalizes nor rescales the supplied dose; the selected source's provenance determines whether it represents a course or another explicit basis. No MR is required or generated.

Native x-fast XYZ arrays become MATLAB YXZ arrays with reversed slices. LPS millimetres map to CERR research coordinates `[L, -P, -S]` centimetres. Scan and dose axis vectors and every CT/dose voxel are checked after reversing this conversion. CT values remain HU with CERR CTOffset zero. Dose remains Gy. Structures use exact label-mask row runs with physical slice thickness; no polygon interpolation is introduced.

CERR uses `ROISampleRate=1` and its existing `getDoseAt` interpolation. Volume is in cubic centimetres. Mean dose uses returned sample-volume weights. D95 uses nearest rank `ceil(0.05*N)` on ascending sampled dose, matching the native definition for equal-volume voxels. It is calculated from raw samples rather than histogram bins. Differential histograms retain CERR's bin-centre convention. The reported maximum difference compares sorted CERR samples with sorted source-dose samples within each structure; it is not a spatial gamma analysis.

The reader rejects changed source/dose/request identities, clinical-release claims, missing or duplicate nonempty structures, nonfinite values, sample-count mismatches, invalid bin centres and inconsistent histogram/structure volumes. Source, dose, request and adapter files are hashed. Reports record MATLAB version and fingerprints of the bridge, `getDVH` and `doseHist`; these function hashes are not a fingerprint of every CERR dependency. The desktop also checks the reported bridge fingerprint against the frozen job.

## Verification

The asymmetric CT-only fixture has dimensions 12×14×10, spacing 2×3×4 mm and six nonempty structures. Real MATLAB R2025b/CERR execution passed CT/dose voxel round trips and sampled all six structures. Native verification matched every structure's sample count and volume. Using the five-fraction matRad fixture, the maximum sampled-dose discrepancy was approximately **0.000104 Gy**; mean and D95 differences are retained in the report. This verifies adapter software on the fixture, not dose accuracy or clinical commissioning.

From `native-tps`, with the existing matRad geometry fixture:

```sh
swift run tps-check --cerr-input build/matrad-geometry-001/source.json build/matrad-geometry-001/result.json build/cerr-check-new
cp scripts/cerr/tps_cerr_analyze.m build/cerr-check-new/
/Applications/MATLAB_R2025b.app/bin/matlab -batch "addpath(fullfile(pwd,'build/cerr-check-new')); tps_cerr_analyze(fullfile(pwd,'build/cerr-check-new'),'/Users/ericbrass/Documents/medical-physics-mbse/CERR/CERR-master');"
swift run tps-check --validate-cerr build/cerr-check-new
swift test
```

The CLI preparation command is a software-verification helper for an existing matRad fixture; the desktop supports any valid selected dose proposal or simulation reference. CLI folders omit the desktop job manifest and are validated with the CLI. Use a new folder on each run.

The desktop was also exercised from the selected matRad proposal through preparation, MATLAB execution, six-row comparison display audit recording, and saved-report reopening in the final build (job `E1C0964E-5E2D-4AF7-A4AB-F9C0E0356A84`). That four-beam, one-fraction fixture had a maximum sampled-dose discrepancy of approximately 0.001942 Gy.

Four CERR unit tests cover constant-dose comparisons and serialization, changed dose/request provenance, clinical-release rejection, missing/duplicate structures, invalid histogram volumes, nonfinite metrics, counts, grid/units and histogram limits. The full suite has 42 passing tests; the desktop Xcode build passes.

## Scope

This is an analysis integration for native synthetic cases. It does not yet import CT/RTSTRUCT/RTDOSE DICOM directly, generate contour polygons, drive CERR's GUI, perform radiomics/outcome inference, or provide iPad MATLAB execution. The `planC.mat` contains scans, doses and raster structures needed for the tested analysis functions; broader CERR editing/export functions may require additional metadata, contours or uniformization. Do not describe this container as a validated DICOM-export plan.

CERR samples the supplied dose; it does not provide a new transport calculation or an independent physical dose reference. No clinical approval, treatment authorization or model-training acceptance is inferred. Full Spark cohort data has not been transferred or tested through this bridge.

The maintained source is `scripts/cerr/tps_cerr_analyze.m`. After editing it, run `python3 scripts/generate_cerr_bridge.py` to update the embedded Swift copy. Regenerate the Xcode project when adding app/test files.

Upstream: [CERR repository](https://github.com/cerr/CERR).
