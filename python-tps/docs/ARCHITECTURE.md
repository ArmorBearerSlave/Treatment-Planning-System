# Architecture

One-way module graph, from data to artifact. Nothing lower imports anything
higher.

```
geometry     Grid: LPS lattice, X-fastest serialisation, trilinear sampling
materials    HU -> relative mass density
special      erf and the bixel-integrated Gaussian (no scipy)
   |
case         PlanningCase: CT + labels + structures; .npz and PhantomCase JSON
phantom      deterministic analytic pelvis phantom
beams        IEC gantry geometry, projection to the isocentre plane, bixel grids
   |
dose         radiological depth field, pencil-beam kernel, sparse influence matrix
objectives   quadratic penalties, values, gradients, curvature bounds
   |
optimize     preconditioned projected FISTA
dvh          cumulative histograms, Dx / Vx / HI
provenance   content digests, engine and environment record
   |
plan         PlanRequest, run_plan, PlanResult, the artifact
compare      DVH deltas, difference statistics, gamma index
report       the text report
   |
external/    bridges to separately installed research codes
  matlab       locating and running a batch MATLAB process
  jobs         frozen, hashed job folders and result binding
  matrad       matRad planning and forward dose
  cerr         CERR dose-volume analysis and reconciliation
   |
cli          argparse front end
```

`matlab/` holds the MATLAB adapters (`pytps_matrad_plan.m`,
`pytps_cerr_analyze.m` and three helpers). They are data as far as Python is
concerned: copied into each job folder and hashed, so a job records the exact
adapter that ran.

## Design decisions worth knowing

**numpy only.** The sparse matrix is coordinate arrays plus `np.bincount`; the
error function is a rational approximation; the solver is hand-written FISTA.
This keeps the engine installable anywhere numpy is, and keeps the whole
numerical path readable in one repository.

**Everything that affects a result is in the request.** `PlanRequest.to_dict`
emits kernel and optimiser *overrides* alongside their descriptive blocks, so a
saved request reloads to exactly the settings that produced the plan and its
digest survives the round trip. That property is asserted in
`tests/test_plan.py`.

**Failures are refusals, not silent corrections.** Oblique geometry, mismatched
grids, unknown objective types, unknown setting names, empty structures,
duplicate gantry angles, non-Hounsfield CT units and clinical-use flags all
raise with a message that says what to change. The influence matrix has an
explicit entry budget rather than an out-of-memory crash.

**The scoring set is separate from the objective set.** Objectives bind to the
structures they name; DVHs are computed for every structure in the case. A
structure with no objective is still reported.

**A plan is a plan, whoever computed the dose.** `PlanResult` carries a
`provider`. A dose from matRad becomes the same artifact type as one computed
here, scored by the same DVH code, so `verify`, `report` and `compare` do not
need to know where it came from — and any difference between two plans is a
difference in dose, never in scoring.

**External results must bind to their inputs.** A bridge freezes and hashes
everything before MATLAB starts, and refuses a result that does not carry those
hashes back. That is what makes an imported dose traceable to the case and
request it was actually computed from.

**State lives in dataclasses, not in the engine.** `PencilBeamSettings`,
`OptimizerSettings`, `PlanRequest` and `Beam` are frozen. `run_plan` takes a
case and a request and returns a `PlanResult`; nothing is mutated in place, so
two runs from the same inputs give identical output.

## Extending it

- **A new objective**: subclass `Objective`, implement `kind` and `residual`
  (or override `evaluate`/`gradient` as `MeanDose` does), and add it to
  `OBJECTIVE_TYPES`. Add a finite-difference gradient test.
- **A different kernel**: `PencilBeamSettings.depth_dose` and the sigma model in
  `compute_influence` are the two places the physics lives. The tests in
  `tests/test_dose.py` state the analytic properties any replacement must keep.
- **Another case format**: add a loader branch to `PlanningCase.load`. Keep the
  synthetic-only and clinical-use refusals.
- **A new solver**: `optimize_fluence` needs only `influence.dose`,
  `influence.transpose_dot` and `objectives.value_and_gradient`.
- **Another external code**: write a `.m` adapter following the job contract in
  `external/jobs.py`, and a module that exports a job, runs it through
  `MatlabRunner`, and binds the result. `tests/fake_matlab.py` shows the
  contract from the other side and lets the new bridge be tested without the
  tool installed.
