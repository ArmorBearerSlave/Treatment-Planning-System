# pytps — Python treatment-planning research engine

A self-contained photon planning engine: CT and structures in, a pencil-beam
dose-influence matrix, constrained fluence optimisation, DVHs, and a signed-by-
digest plan artifact out. The engine runs on **numpy alone** — no scipy, no
torch, no DICOM library, no MATLAB.

It also bridges to two established open research codes, so its results can be
held against something it did not write: **matRad** for an independent dose
engine and optimiser, and **CERR** for an independent dose-volume measurement.
Both are optional, both are used from wherever they are already installed, and
both need MATLAB. See [External research codes](#external-research-codes).

> **Nonclinical.** This is not a commissioned dose authority. It has no measured
> beam model, no CT-density calibration, no absolute output calibration, no
> deliverability model, and no approval or verification evidence. It cannot
> produce a deliverable plan and must not inform any decision about a patient.
> Every artifact it writes carries `clinicalUsePermitted: false`.

## Relationship to the rest of this repository

`python-tps/` is **independent**. It shares no code, build, dependency, or
configuration with:

- `native-tps/` — the SwiftUI/Xcode macOS research workstation.
- `app/cornerstone-tps/` — the Cornerstone3D browser application and its
  Python microservices.

Nothing here imports from those trees and nothing there imports from here. The
only overlap is deliberate and one-directional: `pytps` can *read* the
`PhantomCase` JSON contract that the rest of the repository already writes, so
the same synthetic case can be planned by more than one implementation. That is
a file-format dependency, not a code dependency.

The parent repository's controlled Stage A baseline under `spec/`, `overleaf/`
and `mps/` is not modified, realized, or claimed by this prototype.

## Install and run

```sh
cd python-tps
python3 -m pip install numpy            # the only dependency
export PYTHONPATH=src                   # or: python3 -m pip install -e .
python3 -m pytps selftest
```

## Five-minute workflow

```sh
# 1. Build a deterministic synthetic pelvis phantom (no external data needed).
python3 -m pytps phantom --out work/case.npz

# 2. Look at what it contains, with content digests.
python3 -m pytps inspect work/case.npz

# 3. Write a starter request, then edit the objectives by hand.
python3 -m pytps template --case work/case.npz --out work/request.json

# 4. Plan: beams, influence matrix, optimisation, DVHs, artifact.
python3 -m pytps plan --case work/case.npz --request work/request.json \
                      --out work/plan --verbose

# 5. Re-check the artifact against its inputs.
python3 -m pytps verify work/plan --case work/case.npz
```

`plan` exits non-zero if the optimiser did not converge, so a script cannot
quietly build on a half-solved plan.

A single command works too, using placeholder objectives:

```sh
python3 -m pytps plan --case work/case.npz --target PROSTATE \
                      --prescription 60 --fractions 20 --out work/plan
```

## External research codes

```sh
python3 -m pytps tools                                     # what is installed

python3 -m pytps matrad  --case work/case.npz --request work/request.json \
                         --out work/plan-matrad            # plan with matRad
python3 -m pytps cerr    --plan work/plan --case work/case.npz
                                                           # cross-check DVHs with CERR
python3 -m pytps compare --reference work/plan --evaluation work/plan-matrad \
                         --case work/case.npz              # two plans
python3 -m pytps engines --case work/case.npz --target PROSTATE \
                         --prescription 60 --fractions 20 --angles 0
                                                           # two dose engines
```

A matRad run produces an ordinary plan artifact with `provider: matrad`, so
`verify`, `report` and `compare` work on it unchanged, and it is scored by the
same DVH code as a plan computed here.

Every bridge run is a job folder: inputs and the exact `.m` adapter are frozen
and hashed before MATLAB starts, MATLAB starts from a restored default path so
another checkout cannot shadow the recorded one, and a result that does not
bind back to those hashes is refused. The folder — including `matlab.log` and
`plan.mat`/`planC.mat` — survives the run.

`compare` and `engines` answer different questions, and conflating them is the
easy mistake. `compare` puts two independently optimised plans side by side,
where a difference mixes the dose engines with the two optimisers choosing
different fluence. `engines` has both codes compute the *same* uniform open
field with nothing optimised, which isolates the dose engines.

Measured on this machine (matRad 3.1.0, MATLAB R2025b, CERR): the two engines
agree to 80.1 % at 3 %/3 mm gamma on one open field; CERR reproduces every DVH
metric on both engines' doses to within 1.0 × 10⁻⁶ Gy with voxel-exact
sampling; and on a full plan, matRad reaches a better value of the shared
objective (233.5 against 377.7), which is the dose model rather than the
solver. Details and the full verification record are in `docs/EXTERNAL.md`.

## The plan artifact

`plan --out DIR` writes four files:

| file | contents |
| --- | --- |
| `plan.json` | the whole record: case summary, frozen request, beams, influence-matrix statistics, optimiser trace, DVH curves and metrics, provenance, warnings |
| `request.json` | the frozen request alone, reloadable and digest-stable |
| `dose.npz` | the dose volume `(nx, ny, nz)` in total-course Gy, plus bixel weights and the grid |
| `report.txt` | the human-readable report, including its limitations section |

`verify` recomputes every digest in `plan.json`, and with `--case` also checks
that the artifact was computed from the case you are holding. It is a local
integrity check: it is not an approval and says nothing about dose accuracy.

## Dose convention

Everything — objectives, DVHs, reported metrics — is **total-course physical
Gy**. The fraction count is recorded and used only to derive a per-fraction
figure for the report; it does not enter the optimisation. There is no
biological model and no fractionation correction.

The absolute scale exists only because the optimiser matches the requested
prescription. There is no independent output calibration, so a Gy value here is
a self-consistent research quantity, not delivered dose.

## What is modelled

| | |
| --- | --- |
| Geometry | axis-aligned LPS grids, identity direction cosines; oblique data is rejected, not resampled |
| Beams | coplanar photons, IEC gantry angles, couch and collimator fixed at 0, up to 12 beams |
| Transport | pencil beam: ray-traced radiological depth, exponential attenuation with build-up, inverse square, depth-dependent Gaussian lateral spread integrated across each bixel |
| Heterogeneity | first order, along the ray, through a generic HU-to-density curve |
| Optimisation | convex quadratic objectives (target dose, min, max, mean) under `w >= 0`, solved by preconditioned FISTA |
| Scoring | cumulative DVHs, `Dx`, `Vx`, mean/min/max, homogeneity index |
| Comparison | DVH deltas, voxel difference statistics, global gamma index, shared-objective evaluation |
| Bridges | matRad planning and forward dose, CERR dose-volume analysis, both via frozen and hashed MATLAB jobs |

## What is not modelled

Lateral electronic disequilibrium at density interfaces, head scatter,
contaminant electrons, beam hardening, backscatter, MLC sequencing and
transmission, deliverability, machine-specific beam data, couch and collimator
rotation, non-coplanar beams, motion, deformable registration, biological
models, DICOM RT import or export, and any approval workflow.

See `docs/DOSE_MODEL.md` for the equations, `docs/EXTERNAL.md` for the matRad
and CERR bridges, and `docs/LIMITATIONS.md` for the full list with the
consequence of each.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

226 tests, about eight seconds, and none of them needs MATLAB — the bridges are
exercised end to end against a stand-in that implements the job contract but
not the science. They are not only smoke tests: the dose engine is
checked against analytic expectations (radiological depth equals geometric path
in water; a low-density slab shortens downstream depth by exactly
`(1 - rho) * thickness`; the central axis follows `(1 - e^-bz) e^-uz` to within
5%; the build-up peak lands at the model `d_max`; dose follows inverse square;
penumbra widens with depth; the result is insensitive to bixel width). Every
objective gradient is checked against a finite difference, the optimiser is
checked against problems with known solutions, and the artifact tests confirm
that tampering with a saved dose is detected. The gamma index is checked
against cases with known answers, and the bridge tests cover a failed MATLAB
run, a non-converged optimisation, and a result whose digests do not bind.

## Performance

On the default 72x60x48 phantom with five beams and 6 mm bixels: influence
matrix about 3.4 million nonzeros in under a second, optimisation to
convergence in roughly a minute. Cost scales with `voxels x bixels x fill`.
`PencilBeamSettings.max_entries` stops a request that would exhaust memory and
says what to change.
