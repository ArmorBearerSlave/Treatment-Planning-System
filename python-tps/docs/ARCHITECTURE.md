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
report       the text report
cli          argparse front end
```

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
