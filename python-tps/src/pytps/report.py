"""Human-readable plan reports.

The report always leads and closes with the nonclinical boundary. Numbers are
printed with the units and the dose convention attached, because a dose figure
without its convention is the single easiest thing to misread here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from . import ENGINE_ID, INTENDED_USE

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .plan import PlanResult

BANNER = "=" * 78
RULE = "-" * 78


def _table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    columns = [len(header) for header in headers]
    text_rows = [[("" if cell is None else str(cell)) for cell in row] for row in rows]
    for row in text_rows:
        for index, cell in enumerate(row):
            columns[index] = max(columns[index], len(cell))
    lines = ["  ".join(header.ljust(columns[index]) for index, header in enumerate(headers)).rstrip()]
    lines.append("  ".join("-" * width for width in columns))
    for row in text_rows:
        lines.append(
            "  ".join(
                cell.ljust(columns[index]) if index == 0 else cell.rjust(columns[index])
                for index, cell in enumerate(row)
            ).rstrip()
        )
    return "\n".join(lines)


def render_report(result: "PlanResult") -> str:
    request = result.request
    case = result.case
    lines: list[str] = [
        BANNER,
        "NONCLINICAL RESEARCH PLAN - NOT FOR PATIENT USE",
        INTENDED_USE,
        BANNER,
        "",
        f"Plan ID     : {result.provenance['planID']}",
        f"Label       : {request.plan_label}",
        f"Engine      : {ENGINE_ID}",
        f"Generated   : {result.provenance['generatedUTC']}",
        f"Case        : {case.case_id}  ({case.name})" if case.name else f"Case        : {case.case_id}",
        f"Grid        : {case.grid.dimensions} voxels at {case.grid.spacing} mm, "
        f"{case.grid.voxel_count:,} total",
        f"Status      : research proposal, pending review; not approved, not verified",
        "",
        RULE,
        "PRESCRIPTION",
        RULE,
        f"Target                : {request.target}",
        f"Course prescription   : {request.prescription_gy:.4g} Gy in {request.fractions} fractions",
        f"Per-fraction (derived): {request.dose_per_fraction_gy:.4g} Gy",
        f"Dose convention       : total-course physical Gy (no biological model)",
        f"Isocentre (LPS mm)    : {tuple(round(value, 2) for value in (request.isocenter or ()))}",
        "",
        RULE,
        "BEAMS",
        RULE,
        _table(
            ["#", "gantry deg", "bixels", "field u x v (mm)"],
            [
                [
                    beam.index,
                    f"{beam.gantry_deg:g}",
                    beam.bixels.count,
                    f"{beam.bixels.n_u * beam.bixels.width:g} x {beam.bixels.n_v * beam.bixels.width:g}",
                ]
                for beam in result.beams
            ],
        ),
        "",
        f"Couch and collimator are fixed at 0 deg. Bixel width {request.bixel_width_mm:g} mm, "
        f"field margin {request.field_margin_mm:g} mm, SAD {request.sad_mm:g} mm.",
        "",
        RULE,
        "DOSE ENGINE AND OPTIMISATION",
        RULE,
        f"Kernel          : {request.kernel.to_dict()['model']}",
        f"                  mu {request.kernel.mu_per_mm:g}/mm, build-up {request.kernel.buildup_per_mm:g}/mm "
        f"(d_max ~{request.kernel.dmax_mm():.1f} mm in water)",
        f"Influence matrix: {result.influence.nnz:,} nonzeros over "
        f"{result.influence.n_voxels:,} voxels x {result.influence.n_bixels:,} bixels "
        f"({result.influence.density:.4%} fill)",
        f"Optimiser       : {request.optimizer.to_dict()['algorithm']}",
        f"                  {result.optimization.iterations} iterations, "
        f"objective {result.optimization.objective:.6g}, "
        f"{'converged' if result.optimization.converged else 'NOT CONVERGED'} "
        f"({result.optimization.reason})",
        f"Active bixels   : {int((result.optimization.weights > 0).sum()):,} of "
        f"{result.optimization.weights.size:,}",
        "",
        RULE,
        "OBJECTIVES (total-course Gy)",
        RULE,
        _table(
            ["structure", "type", "dose Gy", "weight"],
            [
                [
                    objective.structure,
                    objective.kind(),
                    f"{objective.dose_gy:.4g}",
                    f"{objective.weight:g}",
                ]
                for objective in request.objectives
            ],
        ),
    ]
    if request.objectives_were_defaulted:
        lines += ["", "These objectives were generated as placeholders. They are not clinical constraints."]

    lines += ["", RULE, "DOSE-VOLUME METRICS (total-course Gy)", RULE]
    rows = []
    for name, dvh in result.dvhs.items():
        metrics = dvh.metrics
        rows.append(
            [
                name + (" *" if name == request.target else ""),
                f"{dvh.volume_cm3:.1f}",
                f"{metrics['meanGy']:.2f}",
                f"{metrics['D98Gy']:.2f}",
                f"{metrics['D50Gy']:.2f}",
                f"{metrics['D2Gy']:.2f}",
                f"{metrics['maxGy']:.2f}",
                f"{metrics['V95pct'] * 100:.1f}%" if "V95pct" in metrics else "",
            ]
        )
    lines.append(
        _table(["structure", "cm3", "mean", "D98", "D50", "D2", "max", "V95%"], rows)
    )
    lines += ["", "* target structure. Volumes are voxel-counted, not surface-reconstructed."]

    if result.warnings:
        lines += ["", RULE, "WARNINGS", RULE]
        lines += [f"- {warning}" for warning in result.warnings]

    lines += [
        "",
        RULE,
        "PROVENANCE",
        RULE,
        f"Engine source digest : {result.provenance['engineSource']['combined']}",
        f"Request digest       : {request.digest()}",
        f"CT digest            : {result.provenance['inputs']['caseCTDigest']}",
        f"Label digest         : {result.provenance['inputs']['caseLabelDigest']}",
        f"Environment          : Python {result.provenance['environment']['python']}, "
        f"numpy {result.provenance['environment']['numpy']}, "
        f"{result.provenance['environment']['platform']}",
        "",
        RULE,
        "LIMITATIONS",
        RULE,
        "- No commissioned beam model, measured CT-density calibration, or absolute output",
        "  calibration exists. Absolute Gy values follow only from the optimiser matching the",
        "  requested prescription, and are not delivered dose.",
        "- The kernel is a single-Gaussian pencil beam with a central-axis density correction.",
        "  Lateral electronic disequilibrium, head scatter, and beam hardening are not modelled.",
        "- No MLC sequencing, deliverability check, machine model, DICOM RT export, or plan",
        "  approval path exists. This plan cannot be delivered.",
        "- Optimiser convergence is a numerical statement about this objective function only.",
        "",
        BANNER,
        "NOT FOR CLINICAL USE. No approval, verification, or validation is claimed.",
        BANNER,
        "",
    ]
    return "\n".join(lines)
