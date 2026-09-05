"""Plan requests, the planning run, and the plan artifact it writes.

Dose convention
---------------
Objectives and reported doses are **total-course physical Gy**. The fraction
count is recorded and used only to report a per-fraction dose; it does not
change the optimisation. There is no biological model, no fractionation
correction, and no absolute machine calibration: the dose scale is set solely
by the optimiser matching the requested prescription.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from . import ENGINE_ID, INTENDED_USE
from .beams import Beam, DEFAULT_SAD_MM, build_beams
from .case import PlanningCase
from .dose import DoseInfluence, PencilBeamSettings, compute_influence
from .dvh import StructureDVH, compute_dvh_set
from .objectives import MaxDose, Objective, ObjectiveSet, TargetDose, objective_from_dict
from .optimize import OptimizationResult, OptimizerSettings, optimize_fluence
from .provenance import build_record, sha256_array, sha256_file, sha256_json

REQUEST_VERSION = 1

#: Identifier for a dose this package computed itself.
PROVIDER_PYTPS = "pytps-pencilbeam"


class PlanRequestError(ValueError):
    """Raised for a plan request this engine will not accept."""


def _overrides(settings: Any, default: Any) -> dict[str, Any]:
    """Fields of a settings dataclass that differ from its defaults.

    Written into the request so that a saved request reloads to exactly the
    same settings, and so that its digest is stable across a round trip.
    """
    return {
        name: getattr(settings, name)
        for name in settings.__dataclass_fields__
        if getattr(settings, name) != getattr(default, name)
    }


@dataclass(frozen=True)
class PlanRequest:
    """A frozen, hashable statement of what was asked for."""

    target: str
    prescription_gy: float
    fractions: int
    gantry_angles: tuple[float, ...] = (0.0, 72.0, 144.0, 216.0, 288.0)
    bixel_width_mm: float = 6.0
    field_margin_mm: float = 10.0
    sad_mm: float = DEFAULT_SAD_MM
    isocenter: tuple[float, float, float] | None = None
    objectives: tuple[Objective, ...] = ()
    kernel: PencilBeamSettings = field(default_factory=PencilBeamSettings)
    optimizer: OptimizerSettings = field(default_factory=OptimizerSettings)
    plan_label: str = "unnamed research plan"
    objectives_were_defaulted: bool = False

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise PlanRequestError("a target structure name is required")
        if not np.isfinite(self.prescription_gy) or self.prescription_gy <= 0.0:
            raise PlanRequestError(f"prescription must be finite and > 0 Gy, got {self.prescription_gy}")
        if self.prescription_gy > 200.0:
            raise PlanRequestError(
                f"prescription {self.prescription_gy} Gy is outside the range this research engine accepts (<= 200 Gy)"
            )
        if self.fractions < 1:
            raise PlanRequestError(f"fractions must be >= 1, got {self.fractions}")
        if self.field_margin_mm < 0.0:
            raise PlanRequestError("field margin must be >= 0 mm")

    @property
    def dose_per_fraction_gy(self) -> float:
        return self.prescription_gy / float(self.fractions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "requestVersion": REQUEST_VERSION,
            "planLabel": self.plan_label,
            "target": self.target,
            "prescriptionGy": float(self.prescription_gy),
            "fractions": int(self.fractions),
            "dosePerFractionGy": round(self.dose_per_fraction_gy, 6),
            "doseConvention": "total-course physical Gy",
            "gantryAnglesDeg": [float(angle) for angle in self.gantry_angles],
            "bixelWidthMM": float(self.bixel_width_mm),
            "fieldMarginMM": float(self.field_margin_mm),
            "sadMM": float(self.sad_mm),
            "isocenterMM": list(self.isocenter) if self.isocenter is not None else None,
            "isocenterRule": "explicit" if self.isocenter is not None else "target centroid",
            "objectives": [objective.to_dict() for objective in self.objectives],
            "objectivesWereDefaulted": bool(self.objectives_were_defaulted),
            # The *Overrides blocks are what reloading reads; the descriptive
            # blocks below them are for humans and for the provenance record.
            "kernelOverrides": _overrides(self.kernel, PencilBeamSettings()),
            "optimizerOverrides": _overrides(self.optimizer, OptimizerSettings()),
            "kernel": self.kernel.to_dict(),
            "optimizer": self.optimizer.to_dict(),
        }

    def digest(self) -> str:
        return sha256_json(self.to_dict())

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PlanRequest":
        version = int(payload.get("requestVersion", REQUEST_VERSION))
        if version != REQUEST_VERSION:
            raise PlanRequestError(f"request version {version} is not supported (expected {REQUEST_VERSION})")
        for key in ("target", "prescriptionGy", "fractions"):
            if key not in payload:
                raise PlanRequestError(f"request is missing required field {key!r}")
        kernel_overrides = dict(payload.get("kernelOverrides", {}))
        optimizer_overrides = dict(payload.get("optimizerOverrides", {}))
        unknown_kernel = set(kernel_overrides) - set(PencilBeamSettings().__dataclass_fields__)
        if unknown_kernel:
            raise PlanRequestError(f"unknown kernel overrides: {sorted(unknown_kernel)}")
        unknown_optimizer = set(optimizer_overrides) - set(OptimizerSettings().__dataclass_fields__)
        if unknown_optimizer:
            raise PlanRequestError(f"unknown optimizer overrides: {sorted(unknown_optimizer)}")
        isocenter = payload.get("isocenterMM")
        objectives = tuple(objective_from_dict(item) for item in payload.get("objectives", []))
        return cls(
            target=str(payload["target"]),
            prescription_gy=float(payload["prescriptionGy"]),
            fractions=int(payload["fractions"]),
            gantry_angles=tuple(float(angle) for angle in payload.get("gantryAnglesDeg", (0, 72, 144, 216, 288))),
            bixel_width_mm=float(payload.get("bixelWidthMM", 6.0)),
            field_margin_mm=float(payload.get("fieldMarginMM", 10.0)),
            sad_mm=float(payload.get("sadMM", DEFAULT_SAD_MM)),
            isocenter=tuple(float(value) for value in isocenter) if isocenter else None,
            objectives=objectives,
            kernel=replace(PencilBeamSettings(), **kernel_overrides),
            optimizer=replace(OptimizerSettings(), **optimizer_overrides),
            plan_label=str(payload.get("planLabel", "unnamed research plan")),
            objectives_were_defaulted=bool(payload.get("objectivesWereDefaulted", False)),
        )

    @classmethod
    def load(cls, path: str | Path) -> "PlanRequest":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def default_objectives(case: PlanningCase, target: str, prescription_gy: float) -> tuple[Objective, ...]:
    """A conservative example objective set: target coverage plus organ ceilings.

    These fractions of prescription are *research placeholders chosen for this
    synthetic phantom*. They are not protocol constraints and must be replaced
    with an explicit, reviewed objective set for any real study.
    """
    objectives: list[Objective] = [TargetDose(structure=target, weight=100.0, dose_gy=prescription_gy)]
    ceilings = {"BLADDER": 0.70, "RECTUM": 0.65, "FEMUR_L": 0.45, "FEMUR_R": 0.45, "BODY": 1.05}
    for structure in case.structures:
        if structure.name == target:
            continue
        fraction = ceilings.get(structure.name.upper())
        if fraction is None:
            continue
        weight = 5.0 if structure.name.upper() == "BODY" else 20.0
        objectives.append(
            MaxDose(structure=structure.name, weight=weight, dose_gy=prescription_gy * fraction)
        )
    return tuple(objectives)


def target_centroid(case: PlanningCase, target: str) -> tuple[float, float, float]:
    mask = case.mask(target)
    count = int(np.count_nonzero(mask))
    if count == 0:
        raise PlanRequestError(f"target structure {target!r} is empty in case {case.case_id}")
    x, y, z = case.grid.meshgrid_world(dtype=np.float32)
    return (float(x[mask].mean()), float(y[mask].mean()), float(z[mask].mean()))


def structure_voxels(case: PlanningCase) -> dict[str, np.ndarray]:
    """Flat voxel indices for every non-empty structure in a case."""
    flat_labels = case.labels.reshape(-1)
    found = {
        structure.name: np.flatnonzero(flat_labels == np.int16(structure.label)).astype(np.int64)
        for structure in case.structures
    }
    return {name: indices for name, indices in found.items() if indices.size > 0}


def evaluate_dose(
    case: PlanningCase, request: PlanRequest, dose: np.ndarray
) -> tuple[dict[str, StructureDVH], list[str]]:
    """Score any dose on a case: DVHs for every structure, plus coverage warnings.

    Shared by the internal engine and by every external bridge, so a matRad
    dose and a pytps dose are measured by exactly the same code. Any difference
    between two plans is then a difference in dose, not in scoring.
    """
    dvhs = compute_dvh_set(
        dose,
        structure_voxels(case),
        case.grid.voxel_volume_cm3,
        reference_dose_gy=request.prescription_gy,
        targets=(request.target,),
    )
    warnings: list[str] = []
    target_dvh = dvhs.get(request.target)
    if target_dvh is not None:
        coverage = target_dvh.metrics.get("V95pct", 0.0)
        if coverage < 0.95:
            warnings.append(
                f"Target V95% is {coverage:.1%}. This objective set and beam arrangement did not "
                "produce uniform target coverage."
            )
    return dvhs, warnings


def plan_provenance(
    case: PlanningCase, request: PlanRequest, case_path: str | Path | None = None
) -> dict[str, Any]:
    """The provenance block every plan artifact carries, whoever computed the dose."""
    inputs: dict[str, Any] = {
        "caseID": case.case_id,
        "caseCTDigest": sha256_array(case.ct_hu),
        "caseLabelDigest": sha256_array(case.labels),
        "caseProvenance": case.provenance,
        "requestDigest": request.digest(),
        "huToDensityTable": "pytps.materials.DEFAULT_HU_TO_DENSITY (generic, not scanner-specific)",
    }
    if case_path is not None and Path(case_path).exists():
        inputs["caseFile"] = Path(case_path).name
        inputs["caseFileDigest"] = sha256_file(case_path)
    record = build_record(inputs)
    record["planID"] = sha256_json(
        {"case": inputs["caseCTDigest"], "request": request.digest(), "time": record["generatedUTC"]}
    )[:32]
    return record


def build_plan_beams(case: PlanningCase, request: PlanRequest) -> tuple[list[Beam], tuple[float, float, float]]:
    """Beam set and isocentre for a request, as the planner would build them."""
    isocenter = request.isocenter or target_centroid(case, request.target)
    target_mask = case.mask(request.target)
    x, y, z = case.grid.meshgrid_world(dtype=np.float32)
    target_points = np.stack([x[target_mask], y[target_mask], z[target_mask]], axis=1)
    del x, y, z
    beams = build_beams(
        request.gantry_angles,
        isocenter,
        target_points,
        request.bixel_width_mm,
        request.field_margin_mm,
        request.sad_mm,
    )
    return beams, tuple(float(value) for value in isocenter)


def forward_dose(case: PlanningCase, request: PlanRequest) -> tuple[np.ndarray, list[Beam]]:
    """Dose of a uniform open field: every bixel at weight one, nothing optimised.

    The scale is arbitrary. This exists so the dose engine can be compared
    against another code's engine without the two optimisers being part of the
    comparison.
    """
    beams, _ = build_plan_beams(case, request)
    influence = compute_influence(case, beams, request.kernel)
    dose = influence.dose(np.ones(influence.n_bixels, dtype=np.float32))
    return dose, beams


@dataclass
class PlanResult:
    """Everything a planning run produced, ready to write to disk."""

    case: PlanningCase
    request: PlanRequest
    beams: list[Beam]
    dose: np.ndarray
    dvhs: dict[str, StructureDVH]
    provenance: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    #: Which engine produced the dose. An externally computed plan carries the
    #: bridge's identifier here and leaves the two fields below unset.
    provider: str = PROVIDER_PYTPS
    influence: DoseInfluence | None = None
    optimization: OptimizationResult | None = None
    #: Provenance of the external run, when the dose did not come from pytps.
    external: dict[str, Any] | None = None
    weights: np.ndarray | None = None

    def __post_init__(self) -> None:
        if self.provider == PROVIDER_PYTPS and (self.influence is None or self.optimization is None):
            raise ValueError("a pytps plan must carry its influence matrix and optimisation result")
        if self.provider != PROVIDER_PYTPS and self.external is None:
            raise ValueError(f"an externally computed plan ({self.provider}) must carry its external record")

    @property
    def dose_volume(self) -> np.ndarray:
        return self.dose.reshape(self.case.grid.dimensions)

    @property
    def bixel_weights(self) -> np.ndarray | None:
        if self.optimization is not None:
            return self.optimization.weights
        return self.weights

    @property
    def converged(self) -> bool:
        """Whether the optimisation that produced this dose converged."""
        if self.optimization is not None:
            return self.optimization.converged
        return bool((self.external or {}).get("optimizerConverged", False))

    def summary(self) -> dict[str, Any]:
        target = self.request.target
        target_dvh = self.dvhs.get(target)
        return {
            "planID": self.provenance["planID"],
            "engine": ENGINE_ID,
            "planLabel": self.request.plan_label,
            "case": self.case.summary(),
            "request": self.request.to_dict(),
            "requestDigest": self.request.digest(),
            "provider": self.provider,
            "beams": [beam.to_dict() for beam in self.beams],
            "influence": self.influence.to_dict() if self.influence is not None else None,
            "optimization": self.optimization.to_dict() if self.optimization is not None else None,
            "external": self.external,
            "dose": {
                "units": "total-course physical Gy",
                "maxGy": round(float(self.dose.max()), 4),
                "targetMeanGy": round(float(target_dvh.metrics["meanGy"]), 4) if target_dvh else None,
                "targetD95Gy": round(float(target_dvh.metrics["D95Gy"]), 4) if target_dvh else None,
                "digest": sha256_array(self.dose),
                "absoluteCalibration": None,
            },
            "dvh": {name: dvh.to_dict() for name, dvh in self.dvhs.items()},
            "provenance": self.provenance,
            "warnings": self.warnings,
            "intendedUse": INTENDED_USE,
            "clinicalUsePermitted": False,
            "status": "research proposal, pending review; not approved and not verified",
        }

    def save(self, directory: str | Path) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        summary = self.summary()
        (directory / "plan.json").write_text(
            json.dumps(summary, indent=2, sort_keys=False) + "\n", encoding="utf-8"
        )
        (directory / "request.json").write_text(
            json.dumps(self.request.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        weights = self.bixel_weights
        np.savez_compressed(
            directory / "dose.npz",
            dose=self.dose_volume,
            weights=np.zeros(0, dtype=np.float32) if weights is None else weights,
            grid=np.asarray(json.dumps(self.case.grid.to_dict())),
            units=np.asarray("total-course physical Gy"),
        )
        from .report import render_report  # local import keeps the module graph acyclic

        (directory / "report.txt").write_text(render_report(self), encoding="utf-8")
        return directory


def run_plan(
    case: PlanningCase,
    request: PlanRequest,
    case_path: str | Path | None = None,
    progress: Callable[[str], None] | None = None,
) -> PlanResult:
    """Build beams, compute the influence matrix, optimise, and score."""
    def announce(message: str) -> None:
        if progress is not None:
            progress(message)

    warnings: list[str] = []
    known = {structure.name for structure in case.structures}
    if request.target not in known:
        raise PlanRequestError(
            f"target {request.target!r} is not a structure in case {case.case_id}. "
            f"Available: {', '.join(sorted(known)) or '(none)'}"
        )

    objectives = request.objectives
    if not objectives:
        objectives = default_objectives(case, request.target, request.prescription_gy)
        request = replace(request, objectives=objectives, objectives_were_defaulted=True)
        warnings.append(
            "No objectives were supplied; a placeholder set was generated. "
            "Placeholder objectives are not clinical constraints."
        )
    missing = sorted({objective.structure for objective in objectives} - known)
    if missing:
        raise PlanRequestError(f"objectives reference structures not in the case: {missing}")

    isocenter = request.isocenter or target_centroid(case, request.target)
    if request.isocenter is None:
        request = replace(request, isocenter=tuple(round(value, 4) for value in isocenter))
    announce(f"isocentre at {tuple(round(value, 2) for value in isocenter)} mm (LPS)")

    target_mask = case.mask(request.target)
    x, y, z = case.grid.meshgrid_world(dtype=np.float32)
    target_points = np.stack([x[target_mask], y[target_mask], z[target_mask]], axis=1)
    del x, y, z

    beams = build_beams(
        request.gantry_angles,
        isocenter,
        target_points,
        request.bixel_width_mm,
        request.field_margin_mm,
        request.sad_mm,
    )
    announce(f"{len(beams)} beams, {sum(beam.bixels.count for beam in beams)} bixels")

    influence = compute_influence(case, beams, request.kernel, progress=progress)
    announce(f"influence matrix: {influence.nnz:,} nonzeros, fill {influence.density:.5%}")

    flat_labels = case.labels.reshape(-1)
    voxel_indices = {
        name: np.flatnonzero(flat_labels == np.int16(case.structure_by_name(name).label)).astype(np.int64)
        for name in {objective.structure for objective in objectives}
    }
    objective_set = ObjectiveSet(objectives, voxel_indices)

    optimization = optimize_fluence(
        influence, objective_set, request.prescription_gy, request.optimizer, progress=progress
    )
    if not optimization.converged:
        warnings.append(
            f"The optimiser stopped without meeting its tolerance: {optimization.reason}. "
            "Treat the dose as a non-converged intermediate."
        )
    announce(f"optimisation finished after {optimization.iterations} iterations: {optimization.reason}")

    dose = optimization.dose
    dvhs, scoring_warnings = evaluate_dose(case, request, dose)
    warnings.extend(scoring_warnings)
    provenance = plan_provenance(case, request, case_path)

    return PlanResult(
        case=case,
        request=request,
        beams=beams,
        influence=influence,
        optimization=optimization,
        dose=dose,
        dvhs=dvhs,
        provenance=provenance,
        warnings=warnings,
    )
