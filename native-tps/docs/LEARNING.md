# Dataset selection, learning and reference evaluation

The completed training cohort is still being generated on DGX Spark. The local
DICOM interoperability cohort is not assumed to be that training cohort: its
manifests describe proxy contours and analytic dose. Native XCAT labels and
transport reference dose require their own provenance and calibration evidence.

## Mac workflow implemented

Open **Dataset & learning** and select a folder of completed native case JSONs.
CT and truth labels are required; MR is optional. Raw DICOM/RTSTRUCT/RTDOSE must
first be converted and validated. The app never treats predicted contours or a
proxy RTDOSE as validated native/transport truth automatically.

Provide `anatomy-groups.json` beside the cases, or fill the original anatomy ID
for each row in the app:

```json
{"schemaVersion":1,"groups":{"VCT-PROSTATE-001":"male_pt108","VCT-PROSTATE-002":"male_pt118"}}
```

These names illustrate the schema, not a verified mapping for the current cohort.
Keys may be native case UUIDs or names. `sourceNotes.anatomyGroupID` also works.
The converter's generated case ID alone is insufficient evidence of independent
anatomy. All motion, dose/energy, reconstruction and lesion variants derived from
one source anatomy must be assigned to the same group. Split before any patch,
slice, augmentation or normalization fitting. All downstream derivatives inherit
the source partition.

1. Inspect reference provenance and grouping, then confirm research suitability.
2. Choose seed and group fractions (default 70/15/15). **Freeze split** requires
   at least three groups and allocates at least one to each partition. With few
   groups the rounded realized percentages differ; the UI shows actual counts.
3. **Train + validate** fits a Gaussian CT+position contour baseline on the Mac
   CPU. It fits three variance floors and selects on validation macro-Dice only.
   No test voxel targets are loaded by the training function. Case inventory
   validation does inspect all files for structural validity before partitioning.
4. Save the experiment: case file digests, group assignment, seed, model parameters,
   training source hashes and validation metrics are retained. Files are rehashed
   before training/evaluation. Existing experiments are not overwritten by training.
Saved runs can be restored with **Open experiment**; training source and split
bindings are checked before reuse.

5. **Evaluate test** applies the frozen selected model to the held-out test groups
   and stores the final test results. That button is single-use in this experiment.
6. **Predict workspace case** creates a learned contour proposal with model digest
   in the normal review workflow. **Export report for iPad** creates a compact JSON.

The first learner is an interpretable statistical ML baseline, not a 3D U-Net.
Features are clipped CT HU and normalized voxel XYZ; class means/variances are
learned from a bounded deterministic voxel sample (about 100,000/case), with equal
class priors. Missing sampled training labels fail explicitly. Coordinate features
make domain/FOV changes a concern; the baseline establishes an initial comparison,
not clinical accuracy. All cases must use consistent label IDs and names.

Reference metrics implemented: per-organ Dice, predicted/reference volume in cc,
and centroid error in LPS mm. Background is excluded from mean Dice. Both-empty
labels yield null Dice and are omitted; false positive/negative presence yields
zero Dice; centroid is null if either region is absent. Means first aggregate
organs within case; validation selection then averages case means. No HD95,
surface-Dice, gamma or biological endpoint claims are made by these metrics.

## iPad

**Results** imports the exported evaluation report through Files. It shows group
counts, validation/test results and individual organ metrics. Training remains
on the Mac. Reports are observational, with an experiment hash for traceability;
they are not authenticated signatures or model-release certificates. Importing a
report does not change the active CT case or its Pencil markup.

## Next model/metric adapters

- Contours: task-specific 3D network; Dice plus surface-distance metrics, lesion
  centroid/size comparison to independently supplied XCAT parameters.
- Dose: CT + structures + beam/prescription conditioning; transport dose as target,
  per-ROI MAE/RMSE and DVH differences with explicit normalization and uncertainty.
  Analytic dose comparisons must be labeled analytic and kept distinct from MC.
- Synthetic CT: only when meaningful paired MR/CT exists; HU error and independent
  dose impact. Current CT-only data must not gain a fabricated MR input.
- Neural training: PyTorch MPS is a candidate for this Mac. It is not installed or
  invoked by the current statistical baseline. Core ML export requires checking
  the preprocessing, output label map and deployed precision against training.

Do not tune a model after examining its final test results and still call those
results independent. Creating a new experiment can reuse the same cohort; this
is not prevented globally. Record such reuse and reserve another independent
cohort for final claims. With only ten source anatomies, uncertainty is large even
if there are hundreds of variants; report anatomy-level confidence intervals and
consider grouped cross-validation for development. Neither is implemented yet.

## Verification

34 Swift tests passed, including split order invariance, grouping of variants,
missing-group rejection, perfect-reference metrics, empty-label handling and
prediction independence from target labels, and stable experiment hashing after save/reload. A six-case artificial CT-only smoke
run exercised fitting and held-out evaluation. This is software verification,
not a result on the unfinished DGX cohort. Mac and physical iPad builds passed.

Sources: [group-based evaluation](https://scikit-learn.org/1.1/modules/cross_validation.html),
[PyTorch MPS](https://docs.pytorch.org/docs/stable/notes/mps.html),
[MONAI Dice implementation](https://github.com/Project-MONAI/MONAI/blob/dev/monai/metrics/meandice.py).
