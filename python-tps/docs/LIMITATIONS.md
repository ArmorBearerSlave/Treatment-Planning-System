# Limitations and intended use

`pytps` is a **nonclinical research and engineering tool**. It is not a medical
device, is not a commissioned treatment planning system, and produces no
clinically approved output.

It may be used only with synthetic or de-identified nonclinical data under an
authorised protocol. It reads no DICOM and holds no patient-identity model, on
purpose.

## Hard boundaries enforced in code

| boundary | where |
| --- | --- |
| A case flagged `clinicalUsePermitted: true` is refused on load | `case.PlanningCase.__post_init__`, `_load_phantom_case_json` |
| A case not flagged `syntheticOnly` is refused on load | `case._load_phantom_case_json` |
| Every plan artifact records `clinicalUsePermitted: false`, `approvalState: none`, `verificationState: not_verified` | `provenance.build_record` |
| Every report opens and closes with the nonclinical banner | `report.render_report` |
| Oblique grids are rejected rather than silently resampled | `geometry.Grid.__post_init__` |
| A non-converged optimisation is reported, warned about, and exits non-zero | `plan.run_plan`, `cli.command_plan` |
| Placeholder objectives are flagged as placeholders in the request, the report and the warnings | `plan.run_plan` |

## What the numbers do not mean

**A dose in Gy is not delivered dose.** There is no measured beam model, no
scanner-specific CT-density calibration, and no absolute output calibration.
The scale exists only because the optimiser matched the requested prescription.

**Optimiser convergence is not plan quality.** It means a convex objective
reached its minimum to a numerical tolerance. Whether that objective describes
a good plan is entirely a matter of the objectives someone wrote.

**`verify` is not approval.** It recomputes content digests. It proves an
artifact matches the inputs it claims, and nothing about dose accuracy, safety,
or clinical validity. Local digests are not authenticated signatures.

**DVH metrics are voxel-counted.** No sub-voxel surface reconstruction is done,
so a small structure carries roughly one voxel layer of discretisation error.
On the default 4 mm grid that is significant for a 36 cm3 target.

**The default objectives are placeholders.** The fractions of prescription in
`plan.default_objectives` were chosen so the synthetic phantom produces a
sensible-looking plan. They are not protocol constraints and were not derived
from any published dose-constraint set.

## Not implemented at all

Deliverability and MLC sequencing; machine and beam data; DICOM RT import or
export; couch or collimator rotation; non-coplanar beams; arc therapy; protons
or other particles; motion, 4D or deformable registration; biological models
(EUD, TCP, NTCP, BED); dose-volume constraints in the optimiser (only
quadratic penalties are available); plan comparison, approval, or signing
workflows; multi-user access control; audit trail beyond the per-artifact
provenance record.

## Before any study use

1. Replace the placeholder objectives with an explicit, reviewed set.
2. State the dose convention wherever a number leaves this tool.
3. Do not compare `pytps` dose against a Monte Carlo or measured reference
   without first characterising the pencil-beam error for that geometry — for
   heterogeneous sites it will be large.
4. Keep the plan artifact with the case it was computed from, and re-run
   `verify` before reusing either.
