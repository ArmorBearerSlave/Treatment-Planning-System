# External research codes: matRad and CERR

`pytps` computes dose and optimises fluence on its own. Two established open
research codes are bridged in so that its results can be held against
something it did not write.

| code | what it provides here | what it does not |
| --- | --- | --- |
| [matRad](https://github.com/e0404/matRad) | an independent photon dose engine and fluence optimiser | it is not a reference standard; its Generic machine is uncommissioned too |
| [CERR](https://github.com/cerr/CERR) | an independent dose-volume measurement and a geometry round trip | it does not recalculate dose or certify a plan |

Both are **MATLAB** codes. There is no MATLAB-free path for either: CERR ships
a `Python_packages` directory, but it contains only the surface-distance
package, not a Python planC implementation.

Neither is bundled, vendored, or modified. Each is used under its own licence
from wherever it is already installed, and neither checkout is written to —
matRad's per-run userdata is redirected into the job folder.

## Setting them up

Locations are resolved in this order: an explicit flag, an environment
variable, then discovery relative to the current user's home. Nothing
machine-specific is written into the source.

```sh
export PYTPS_MATLAB=/Applications/MATLAB_R2025b.app/bin/matlab
export PYTPS_MATRAD=~/path/to/matRad
export PYTPS_CERR=~/path/to/CERR

python3 -m pytps tools           # report what was found, without running it
python3 -m pytps tools --version # also start MATLAB and read its version
```

Discovery requires a marker file (`matRad_rc.m`, `getCERRPath.m`), so a
directory that merely has the right name is not accepted.

## How a bridge run works

Every run is a **job folder**. It is not a temporary directory: it is the
record of what was computed.

1. **Freeze.** The CT, the label map, the request and the exact `.m` adapter
   that will execute are written into the folder and SHA-256 hashed into
   `job.json`. The tool paths, versions and timeout are recorded.
2. **Run.** MATLAB starts in batch mode with `restoredefaultpath`, then only
   the job folder and the recorded library on its path — so another matRad or
   CERR checkout already on the user's saved MATLAB path cannot shadow the one
   the job recorded. The adapter re-hashes every frozen input before it does
   any work.
3. **Bind.** The result carries the digests of the inputs it was computed
   from. The importer refuses a result whose digests do not match, whose dose
   basis is not stated, or which claims clinical release.
4. **Keep.** The folder survives the run — inputs, adapter, `matlab.log`,
   `exit-code.txt`, `plan.mat` or `planC.mat`, and the result. A failure keeps
   everything except the result.

Volumes cross the boundary as **raw little-endian binary**, X-fastest XYZ, not
JSON: a 3.1 million voxel CT is 66 MB of JSON and loses bytes to decimal
round-tripping, against 12 MB of `float32` that MATLAB reads with one `fread`.

## matRad

```sh
python3 -m pytps matrad --case work/case.npz --request work/request.json \
                        --out work/plan-matrad
```

The result is an ordinary pytps plan artifact — same `plan.json`, `dose.npz`,
`report.txt`, same DVH code — with `provider: matrad` and an `external` block
holding the job provenance. `pytps verify` and `pytps compare` work on it
exactly as on a plan this package computed.

**The objectives are the same function.** matRad's squared dose objectives
evaluate `1/numel(dose) * sum(residual^2)` scaled by a penalty, which is
exactly the form `pytps.objectives` uses. Given identical weights and dose
levels the two codes minimise the same quantity. That is what makes the
comparison meaningful, and it is why `mean_dose` is **refused** rather than
mapped: matRad's mean-dose objective uses a different difference function, so
mapping it would make the comparison invalid rather than merely approximate.

**Fractions.** matRad divides objective doses by the fraction count internally
and returns per-fraction physical dose. The adapter multiplies back exactly
once and emits total-course physical Gy, matching this package's convention.

**Isocentre.** matRad computes its own target centre of gravity. The adapter
compares it against the requested isocentre and refuses the run if they differ
by more than the tolerance, so the two codes cannot silently plan shifted
geometries.

**Iterations.** matRad's default optimiser cap is 500, which a multi-beam
fluence problem often exceeds; matRad then stops without converging and this
bridge refuses to import the result. `--matrad-iterations` raises it, and the
default here is 3000.

## CERR

```sh
python3 -m pytps cerr --plan work/plan-pytps --case work/case.npz
```

The adapter rebuilds the CT, labels and dose inside a CERR `planC` — a
different coordinate convention, `[L, -P, -S]` in centimetres with reversed
slices — and then reads every axis and every voxel back out through CERR's own
accessors and compares them against what was sent. **Nothing is analysed until
that round trip is exact.** Structures are rasterised from the label masks as
exact row runs, so CERR analyses the same voxels, not a reconstructed polygon.

It then measures the dose with CERR's own `getDVH` sampling and `doseHist`
binning.

**Reconciling definitions.** CERR's `doseHist` bins; `pytps.dvh` interpolates a
cumulative histogram. An apparent disagreement is usually that, not a defect.
So the comparison recomputes this package's metrics with CERR's own nearest-rank
definition (`pytps.dvh.nearest_rank_dose`) and compares like with like. The
command exits 2 if a like-for-like metric disagrees.

## Comparing

Two different questions, and conflating them is the easiest mistake to make.

**Comparing two plans** — what a planner asks:

```sh
python3 -m pytps compare --reference work/plan-pytps \
                         --evaluation work/plan-matrad --case work/case.npz
```

This reports DVH deltas per structure, voxel difference statistics, a gamma
index, and the value of the shared objective function evaluated on both doses
(the objective is a function of dose, so it ranks the two plans on what was
actually asked for). But the two plans were optimised independently, so a
difference mixes the dose engines with the two optimisers having chosen
different fluence, and gamma cannot separate them. The command says so.

**Comparing two engines** — what an engineer asks:

```sh
python3 -m pytps engines --case work/case.npz --target PROSTATE \
                         --prescription 60 --fractions 20 --angles 0
```

Both codes compute the dose of the *same* uniform open field: every bixel at
weight one, nothing optimised, no fluence choice involved. Neither has an
absolute calibration, so both are normalised to their own mean dose in a 10 mm
sphere at the isocentre. What remains is the difference between two
pencil-beam implementations.

## Verification performed

On 2026-09-05, on this machine: MATLAB R2025b Update 3 (`MACA64`), matRad
`"Cleve" v3.1.0 (master-09944815)`, CERR at the checked-out revision recorded
in each job's provenance. IPOPT was not available for Apple silicon, so matRad
selected MATLAB's `fmincon`.

**matRad planning.** A 36 × 30 × 24 phantom at 8 mm, four beams, 12 mm bixels,
60 Gy in 20 fractions, placeholder objectives. matRad converged in 69 s over
140 bixels. Its isocentre differed from the requested target centroid by
2.2 × 10⁻⁵ mm. Target mean dose 59.81 Gy against a 60 Gy prescription.

Planning the same case with this package's engine and the same objectives gave
target mean 59.68 Gy (0.12 Gy apart) and D95 58.26 Gy against matRad's
58.07 Gy. Organs at risk diverged more — rectum D2 by 10 Gy, femoral head means
by 3–4 Gy — which is expected: the two optimisers minimise the same objective
through different dose models, and the objective constrains the target far more
tightly than anything else.

Evaluating the **shared objective function on both doses** gave 233.5 for the
matRad plan against 377.7 for this package's. Because the objective is a
function of dose, that is a fair comparison of what each plan achieved against
what was asked for, and matRad's plan is the better one by that measure. It is
not an optimiser failure here: this package's solver converged, improving by
0.012 % over its final hundred iterations. The gap is the dose model. A single
Gaussian gives a broader penumbra than matRad's photon kernel, so the fluence
this engine can predict simply cannot spare the rectum and femoral heads as
sharply while still covering the target. That is the clearest measurement so
far of what `docs/DOSE_MODEL.md` lists as approximation 3.

**Dose engines.** The same case, one anterior open field, uniform fluence. Both
codes generated **35 bixels**, so the field shaping agrees exactly. Normalised
to the isocentre, the mean absolute difference above 10 % of maximum was 0.069
(6.9 % of the isocentre dose), and the 3 %/3 mm global gamma pass rate was
80.1 % with mean gamma 0.72. On an 8 mm grid against a 3 mm distance criterion
this is indicative rather than precise, and the remaining difference is what it
should be: two different depth-dose parameterisations and two different lateral
kernels.

**CERR.** Run twice: once on this package's optimised dose and once on
matRad's, both on the same phantom. The geometry round trip was exact both
times. For all six structures CERR sampled exactly the same voxel counts, with
a maximum sampled-dose difference of 1.3 × 10⁻⁶ Gy, and every compared metric
(mean, min, max, D2, D50, D95, D98) agreed to within 1.0 × 10⁻⁶ Gy. That is an
independent confirmation of both the coordinate handling and the DVH code, and
it holds for a dose this package did not compute.

The sampled-dose tolerance scales with the dose rather than being a fixed
number, because the dose makes two float32 round trips through the job folder
and MATLAB's double arithmetic. A fixed 10⁻⁶ Gy threshold passed at a 61 Gy
maximum and reported a spurious geometry fault at 76 Gy; the tolerance is now
16 float32 epsilons of the dose maximum, which is 1.5 × 10⁻⁴ Gy at 76 Gy.

None of this is commissioning, validation, or approval. It is consistency
between research codes, recorded with the provenance to re-check it.

## What the bridges do not establish

- **Neither external code is a reference.** matRad's Generic photon machine is
  uncommissioned; agreement between two pencil-beam codes can reflect a shared
  approximation rather than accuracy. A real accuracy statement needs measured
  data or a validated Monte Carlo reference.
- **CERR agreement is about measurement, not dose.** It confirms that two
  implementations measure the same distribution the same way. It says nothing
  about whether that distribution is right.
- **Provenance is local.** Content digests bind a result to its inputs. They
  are not authenticated signatures, they do not freeze the dependency
  environment, and they are not an approval.
- **Nothing here is deliverable.** No MLC sequencing, no deliverability check,
  no machine model, no DICOM RT export, on either side of either bridge.
