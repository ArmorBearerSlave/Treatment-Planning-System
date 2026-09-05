"""Comparing two dose distributions on the same case.

Used to hold this package's pencil-beam engine against matRad's, but it is
provider-agnostic: it compares any two doses on one grid.

Three views, because they fail differently:

* **Dose-volume metrics.** What a planner looks at. Insensitive to where a
  difference is, so two very different distributions can share a DVH.
* **Voxel difference statistics.** Sensitive to everything, including a
  sub-voxel shift that nobody would care about clinically.
* **Gamma index.** The standard compromise: a difference is acceptable if the
  dose matches within a tolerance *or* the same dose is found within a small
  distance.

None of the three establishes that either distribution is correct. Two
pencil-beam codes can agree closely and share the same approximation error
against a Monte Carlo reference; agreement is consistency, not accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from .case import PlanningCase
from .geometry import Grid, trilinear_sample
from .plan import PlanRequest, structure_voxels

#: Metrics compared for every structure, as (label, volume fraction or None).
COMPARED_METRICS: tuple[tuple[str, float | None], ...] = (
    ("meanGy", None),
    ("D98Gy", 0.98),
    ("D95Gy", 0.95),
    ("D50Gy", 0.50),
    ("D2Gy", 0.02),
    ("maxGy", 0.0),
)

MAX_GAMMA_WORK = 4_000_000_000


class ComparisonError(ValueError):
    """Raised when two doses cannot be compared as asked."""


def normalize_to_isocenter(
    grid: Grid,
    dose: np.ndarray,
    isocenter: Sequence[float],
    radius_mm: float = 10.0,
) -> np.ndarray:
    """Scale a dose so the mean value in a small sphere at the isocentre is 1.

    Neither engine has an absolute output calibration, so an uncalibrated dose
    can only be compared in relative terms. Normalising to a small volume
    rather than to a single voxel or to the global maximum keeps the reference
    insensitive to grid noise and to a stray hot voxel.
    """
    dose = np.asarray(dose, dtype=np.float32).reshape(grid.dimensions)
    if radius_mm <= 0.0:
        raise ComparisonError("normalisation radius must be > 0 mm")
    x, y, z = grid.meshgrid_world(dtype=np.float32)
    centre = np.asarray(isocenter, dtype=np.float32)
    inside = ((x - centre[0]) ** 2 + (y - centre[1]) ** 2 + (z - centre[2]) ** 2) <= radius_mm ** 2
    if not np.any(inside):
        raise ComparisonError(
            f"no voxel lies within {radius_mm:g} mm of the isocentre {tuple(centre)}; "
            "widen the radius or check the isocentre"
        )
    reference = float(dose[inside].mean())
    if reference <= 0.0:
        raise ComparisonError("the dose at the isocentre is zero, so it cannot be normalised there")
    return (dose / np.float32(reference)).reshape(-1)


@dataclass
class GammaResult:
    """A gamma-index evaluation of one dose against another."""

    dose_percent: float
    distance_mm: float
    threshold_percent: float
    normalization: str
    pass_rate: float
    evaluated_voxels: int
    mean_gamma: float
    max_gamma: float
    search_step_mm: float
    offsets: int

    @property
    def criterion(self) -> str:
        return f"{self.dose_percent:g}%/{self.distance_mm:g}mm"

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion": self.criterion,
            "normalization": self.normalization,
            "thresholdPercentOfMax": self.threshold_percent,
            "passRate": round(self.pass_rate, 6),
            "evaluatedVoxels": self.evaluated_voxels,
            "meanGamma": round(self.mean_gamma, 4),
            "maxGamma": round(self.max_gamma, 4),
            "searchStepMM": self.search_step_mm,
            "searchOffsets": self.offsets,
            "note": (
                "Gamma is evaluated at reference voxels, searching the evaluation dose by "
                "trilinear interpolation. It measures consistency between two distributions, "
                "not the accuracy of either."
            ),
        }


#: Largest search lattice that may be built, before the sphere is cut out.
MAX_SEARCH_OFFSETS = 2_000_000


def _search_offsets(spacing: Sequence[float], distance_mm: float, step_mm: float) -> np.ndarray:
    """Offsets in mm on a cubic lattice, inside the distance-to-agreement sphere."""
    if step_mm <= 0.0:
        raise ComparisonError("gamma search step must be > 0 mm")
    reach = int(np.floor(distance_mm / step_mm))
    # Check the size before allocating: a fine step against a large distance
    # criterion asks for a lattice that would exhaust memory.
    lattice = (2 * reach + 1) ** 3
    if lattice > MAX_SEARCH_OFFSETS:
        raise ComparisonError(
            f"a {distance_mm:g} mm search at a {step_mm:g} mm step needs a {lattice:,} point "
            f"lattice, over the {MAX_SEARCH_OFFSETS:,} limit. Raise step_mm or lower distance_mm."
        )
    axis = np.arange(-reach, reach + 1, dtype=np.float64) * step_mm
    dx, dy, dz = np.meshgrid(axis, axis, axis, indexing="ij")
    offsets = np.stack([dx.reshape(-1), dy.reshape(-1), dz.reshape(-1)], axis=1)
    radius = np.linalg.norm(offsets, axis=1)
    return offsets[radius <= distance_mm + 1e-9]


def gamma_index(
    grid: Grid,
    reference: np.ndarray,
    evaluation: np.ndarray,
    dose_percent: float = 3.0,
    distance_mm: float = 3.0,
    threshold_percent: float = 10.0,
    step_mm: float | None = None,
) -> GammaResult:
    """Global gamma index of ``evaluation`` against ``reference``.

    The dose criterion is a percentage of the reference maximum (global gamma),
    and only reference voxels above ``threshold_percent`` of that maximum are
    evaluated. The evaluation dose is searched on a sub-voxel lattice inside the
    distance-to-agreement sphere, so a grid coarser than the distance criterion
    does not silently collapse gamma into a plain dose difference.
    """
    reference = np.asarray(reference, dtype=np.float32).reshape(grid.dimensions)
    evaluation = np.asarray(evaluation, dtype=np.float32).reshape(grid.dimensions)
    if dose_percent <= 0.0 or distance_mm <= 0.0:
        raise ComparisonError("gamma dose and distance criteria must both be > 0")
    if not 0.0 <= threshold_percent < 100.0:
        raise ComparisonError("gamma threshold must be in [0, 100) percent of the maximum")

    peak = float(reference.max())
    if peak <= 0.0:
        raise ComparisonError("the reference dose is everywhere zero")
    dose_tolerance = dose_percent / 100.0 * peak
    cutoff = threshold_percent / 100.0 * peak

    selected = np.flatnonzero((reference.reshape(-1) >= cutoff))
    if selected.size == 0:
        raise ComparisonError("no reference voxel is above the gamma dose threshold")

    if step_mm is None:
        step_mm = min(float(min(grid.spacing)) / 2.0, distance_mm / 3.0)
    offsets = _search_offsets(grid.spacing, distance_mm, step_mm)
    work = int(offsets.shape[0]) * int(selected.size)
    if work > MAX_GAMMA_WORK:
        raise ComparisonError(
            f"this gamma evaluation needs {work:,} interpolations. Raise the search step "
            "(step_mm), raise the dose threshold, or use a coarser grid."
        )

    x, y, z = grid.meshgrid_world(dtype=np.float32)
    points = np.stack(
        [x.reshape(-1)[selected], y.reshape(-1)[selected], z.reshape(-1)[selected]], axis=1
    )
    del x, y, z
    reference_values = reference.reshape(-1)[selected].astype(np.float32)

    origin = np.asarray(grid.origin, dtype=np.float32)
    spacing = np.asarray(grid.spacing, dtype=np.float32)
    best = np.full(selected.size, np.inf, dtype=np.float32)
    for offset in offsets:
        distance_term = float(np.linalg.norm(offset) / distance_mm) ** 2
        if distance_term >= 1.0 and np.all(best <= 1.0):
            continue
        indices = (points + offset.astype(np.float32) - origin) / spacing
        sampled = trilinear_sample(
            evaluation, (indices[:, 0], indices[:, 1], indices[:, 2]), fill=0.0
        )
        dose_term = ((sampled - reference_values) / np.float32(dose_tolerance)) ** 2
        np.minimum(best, dose_term + np.float32(distance_term), out=best)

    gamma = np.sqrt(best)
    return GammaResult(
        dose_percent=float(dose_percent),
        distance_mm=float(distance_mm),
        threshold_percent=float(threshold_percent),
        normalization=f"global, {dose_percent:g}% of the reference maximum ({peak:.4g} Gy)",
        pass_rate=float(np.count_nonzero(gamma <= 1.0)) / float(gamma.size),
        evaluated_voxels=int(gamma.size),
        mean_gamma=float(gamma.mean()),
        max_gamma=float(gamma.max()),
        search_step_mm=float(step_mm),
        offsets=int(offsets.shape[0]),
    )


def _metric(values: np.ndarray, fraction: float | None) -> float:
    from .dvh import nearest_rank_dose

    if fraction is None:
        return float(values.mean())
    if fraction == 0.0:
        return float(values.max())
    return nearest_rank_dose(values, fraction)


@dataclass
class DoseComparison:
    """Two doses on one case, measured three ways."""

    case_id: str
    reference_label: str
    evaluation_label: str
    structures: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)
    difference: dict[str, float] = field(default_factory=dict)
    gamma: GammaResult | None = None
    warnings: list[str] = field(default_factory=list)
    #: "plans" compares two independently optimised plans; "engines" compares
    #: two calculations of the same open field. The distinction matters for
    #: how the numbers may be read.
    kind: str = "plans"
    objective_values: dict[str, float] | None = None

    def worst_structure_difference_gy(self) -> tuple[str, str, float]:
        worst = ("", "", 0.0)
        for structure, metrics in self.structures.items():
            for name, row in metrics.items():
                if abs(row["difference"]) > abs(worst[2]):
                    worst = (structure, name, row["difference"])
        return worst

    def to_dict(self) -> dict[str, Any]:
        structure, metric, value = self.worst_structure_difference_gy()
        return {
            "caseID": self.case_id,
            "kind": self.kind,
            "reference": self.reference_label,
            "evaluation": self.evaluation_label,
            "doseUnits": "total-course physical Gy" if self.kind == "plans" else "normalised to the isocentre",
            "objectiveValues": self.objective_values,
            "structures": {
                name: {
                    key: {inner: round(float(number), 4) for inner, number in row.items()}
                    for key, row in metrics.items()
                }
                for name, metrics in self.structures.items()
            },
            "worstStructureMetric": {
                "structure": structure,
                "metric": metric,
                "differenceGy": round(value, 4),
            },
            "voxelDifference": {key: round(float(value), 6) for key, value in self.difference.items()},
            "gamma": self.gamma.to_dict() if self.gamma else None,
            "warnings": self.warnings,
            "note": (
                "Consistency between two research dose engines. Neither is a commissioned or "
                "measured reference, so agreement is not evidence of accuracy."
            ),
        }


def compare_doses(
    case: PlanningCase,
    reference: np.ndarray,
    evaluation: np.ndarray,
    reference_label: str = "reference",
    evaluation_label: str = "evaluation",
    request: PlanRequest | None = None,
    gamma_criteria: tuple[float, float] | None = (3.0, 3.0),
    gamma_threshold_percent: float = 10.0,
    kind: str = "plans",
) -> DoseComparison:
    """Compare two doses computed on the same case.

    ``kind`` says what is being compared, because the same numbers mean
    different things. ``"engines"`` compares two calculations of one open
    field, so a difference is a dose-engine difference. ``"plans"`` compares
    two independently optimised plans, where a difference mixes the dose
    engines with the two optimisers having chosen different fluence - and a
    gamma index cannot separate the two.
    """
    if kind not in {"plans", "engines"}:
        raise ComparisonError(f"comparison kind must be 'plans' or 'engines', got {kind!r}")
    grid = case.grid
    reference = np.asarray(reference, dtype=np.float32).reshape(-1)
    evaluation = np.asarray(evaluation, dtype=np.float32).reshape(-1)
    if reference.size != grid.voxel_count or evaluation.size != grid.voxel_count:
        raise ComparisonError(
            f"both doses must have {grid.voxel_count} voxels; got {reference.size} and {evaluation.size}"
        )

    comparison = DoseComparison(
        case_id=case.case_id,
        reference_label=reference_label,
        evaluation_label=evaluation_label,
        kind=kind,
    )
    if kind == "plans":
        comparison.warnings.append(
            "These are two independently optimised plans. A difference mixes the dose engines "
            "with the two optimisers choosing different fluence, and a gamma index cannot "
            "separate them. Use a forward-dose comparison (kind='engines') to isolate the engines."
        )
    for name, indices in structure_voxels(case).items():
        reference_values = reference[indices]
        evaluation_values = evaluation[indices]
        metrics: dict[str, dict[str, float]] = {}
        for label, fraction in COMPARED_METRICS:
            left = _metric(reference_values, fraction)
            right = _metric(evaluation_values, fraction)
            metrics[label] = {"reference": left, "evaluation": right, "difference": right - left}
        if request is not None and name == request.target:
            level = request.prescription_gy * 0.95
            left = float(np.count_nonzero(reference_values >= level)) / float(indices.size)
            right = float(np.count_nonzero(evaluation_values >= level)) / float(indices.size)
            metrics["V95pct"] = {"reference": left, "evaluation": right, "difference": right - left}
        comparison.structures[name] = metrics

    delta = evaluation - reference
    peak = float(reference.max())
    inside = reference >= 0.1 * peak if peak > 0.0 else np.ones(reference.shape, dtype=bool)
    comparison.difference = {
        "maxAbsoluteGy": float(np.abs(delta).max()),
        "meanAbsoluteGy": float(np.abs(delta).mean()),
        "rootMeanSquareGy": float(np.sqrt(np.mean(delta.astype(np.float64) ** 2))),
        "meanAbsoluteAbove10pctGy": float(np.abs(delta[inside]).mean()) if np.any(inside) else 0.0,
        "referenceMaxGy": peak,
        "evaluationMaxGy": float(evaluation.max()),
    }

    if request is not None and request.objectives:
        from .objectives import ObjectiveSet

        try:
            voxels = structure_voxels(case)
            objective_set = ObjectiveSet(
                list(request.objectives),
                {name: voxels[name] for name in {item.structure for item in request.objectives}},
            )
        except (KeyError, ValueError):
            comparison.objective_values = None
        else:
            # The objective is a function of dose, so it can be evaluated on
            # either distribution. This says which plan better satisfies what
            # was actually asked for, in the units of the objective itself.
            comparison.objective_values = {
                reference_label: objective_set.value(reference),
                evaluation_label: objective_set.value(evaluation),
            }

    if gamma_criteria is not None:
        dose_percent, distance_mm = gamma_criteria
        comparison.gamma = gamma_index(
            grid,
            reference,
            evaluation,
            dose_percent=dose_percent,
            distance_mm=distance_mm,
            threshold_percent=gamma_threshold_percent,
        )
        coarsest = float(max(grid.spacing))
        if coarsest > distance_mm:
            # The search step is always finer than the criterion, but the dose
            # between voxels is interpolated rather than known. When the voxels
            # are further apart than the distance criterion, that interpolation
            # is doing the work and the gamma result is only indicative.
            comparison.warnings.append(
                f"Voxels are {coarsest:g} mm apart against a {distance_mm:g} mm distance "
                "criterion, so the distance term is resolved by interpolation between voxels "
                "rather than by measured structure. Read this gamma result as indicative."
            )
    return comparison
