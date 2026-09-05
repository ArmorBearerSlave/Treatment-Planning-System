"""Quadratic planning objectives.

Every objective is expressed in **total-course physical Gy** and is normalised
by the number of voxels in its structure, so that weights are comparable
between a 30 cm3 target and a 500 cm3 organ. Each objective reports both its
value and its voxel-space gradient; the optimiser chains that gradient through
the transpose of the dose-influence matrix.

These are dose-volume-free quadratic penalties. They are not clinical
constraints, are not derived from any protocol, and satisfying them says
nothing about clinical acceptability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import numpy as np


class ObjectiveError(ValueError):
    """Raised for an objective that cannot be evaluated as specified."""


@dataclass(frozen=True)
class Objective:
    """Base class: a penalty on the dose inside one structure."""

    structure: str
    weight: float
    dose_gy: float

    def __post_init__(self) -> None:
        if self.weight < 0.0 or not np.isfinite(self.weight):
            raise ObjectiveError(f"{self.kind()} on {self.structure!r}: weight must be finite and >= 0")
        if self.dose_gy < 0.0 or not np.isfinite(self.dose_gy):
            raise ObjectiveError(f"{self.kind()} on {self.structure!r}: dose must be finite and >= 0 Gy")

    @classmethod
    def kind(cls) -> str:
        raise NotImplementedError

    def residual(self, dose: np.ndarray) -> np.ndarray:
        """Signed, one- or two-sided residual in Gy for the selected voxels."""
        raise NotImplementedError

    def evaluate(self, dose: np.ndarray, count: int) -> float:
        residual = self.residual(dose)
        return float(self.weight) * float(np.dot(residual, residual)) / float(count)

    def gradient(self, dose: np.ndarray, count: int) -> np.ndarray:
        return (2.0 * float(self.weight) / float(count)) * self.residual(dose)

    def curvature(self, count: int) -> float:
        """Upper bound on the second derivative per voxel, for the step size."""
        return 2.0 * float(self.weight) / float(count)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.kind(),
            "structure": self.structure,
            "doseGy": float(self.dose_gy),
            "weight": float(self.weight),
        }


@dataclass(frozen=True)
class TargetDose(Objective):
    """Two-sided squared deviation from a prescribed dose."""

    @classmethod
    def kind(cls) -> str:
        return "target_dose"

    def residual(self, dose: np.ndarray) -> np.ndarray:
        return dose - np.float32(self.dose_gy)


@dataclass(frozen=True)
class MaxDose(Objective):
    """One-sided squared penalty above a ceiling."""

    @classmethod
    def kind(cls) -> str:
        return "max_dose"

    def residual(self, dose: np.ndarray) -> np.ndarray:
        return np.maximum(dose - np.float32(self.dose_gy), np.float32(0.0))


@dataclass(frozen=True)
class MinDose(Objective):
    """One-sided squared penalty below a floor."""

    @classmethod
    def kind(cls) -> str:
        return "min_dose"

    def residual(self, dose: np.ndarray) -> np.ndarray:
        return np.minimum(dose - np.float32(self.dose_gy), np.float32(0.0))


@dataclass(frozen=True)
class MeanDose(Objective):
    """One-sided squared penalty on the structure mean dose above a ceiling."""

    @classmethod
    def kind(cls) -> str:
        return "mean_dose"

    def residual(self, dose: np.ndarray) -> np.ndarray:  # pragma: no cover - unused
        raise ObjectiveError("mean_dose uses its own evaluate/gradient")

    def evaluate(self, dose: np.ndarray, count: int) -> float:
        excess = max(0.0, float(dose.mean()) - float(self.dose_gy))
        return float(self.weight) * excess * excess

    def gradient(self, dose: np.ndarray, count: int) -> np.ndarray:
        excess = max(0.0, float(dose.mean()) - float(self.dose_gy))
        scale = 2.0 * float(self.weight) * excess / float(count)
        return np.full(dose.shape, np.float32(scale), dtype=np.float32)

    def curvature(self, count: int) -> float:
        # The mean-dose Hessian is (2w/N^2) * ones(N, N); its operator norm is 2w/N.
        return 2.0 * float(self.weight) / float(count)


OBJECTIVE_TYPES: dict[str, type[Objective]] = {
    cls.kind(): cls for cls in (TargetDose, MaxDose, MinDose, MeanDose)
}


def objective_from_dict(payload: dict[str, Any]) -> Objective:
    kind = str(payload.get("type", "")).strip()
    if kind not in OBJECTIVE_TYPES:
        known = ", ".join(sorted(OBJECTIVE_TYPES))
        raise ObjectiveError(f"unknown objective type {kind!r}; supported types are: {known}")
    for key in ("structure", "doseGy", "weight"):
        if key not in payload:
            raise ObjectiveError(f"{kind} objective is missing {key!r}")
    return OBJECTIVE_TYPES[kind](
        structure=str(payload["structure"]),
        weight=float(payload["weight"]),
        dose_gy=float(payload["doseGy"]),
    )


class ObjectiveSet:
    """Objectives bound to concrete voxel-index sets for one case."""

    def __init__(self, objectives: Sequence[Objective], voxel_indices: dict[str, np.ndarray]) -> None:
        self.objectives = [item for item in objectives if item.weight > 0.0]
        self.disabled = [item for item in objectives if item.weight <= 0.0]
        self.voxel_indices = {name: np.asarray(idx, dtype=np.int64) for name, idx in voxel_indices.items()}
        if not self.objectives:
            raise ObjectiveError("every objective has zero weight; nothing would be optimised")
        for objective in self.objectives:
            indices = self.voxel_indices.get(objective.structure)
            if indices is None:
                raise ObjectiveError(f"no voxel set was bound for structure {objective.structure!r}")
            if indices.size == 0:
                raise ObjectiveError(f"structure {objective.structure!r} is empty in this case")

    def value(self, dose: np.ndarray) -> float:
        total = 0.0
        for objective in self.objectives:
            indices = self.voxel_indices[objective.structure]
            total += objective.evaluate(dose[indices], indices.size)
        return float(total)

    def value_and_gradient(self, dose: np.ndarray) -> tuple[float, np.ndarray]:
        total = 0.0
        gradient = np.zeros_like(dose, dtype=np.float32)
        for objective in self.objectives:
            indices = self.voxel_indices[objective.structure]
            selected = dose[indices]
            total += objective.evaluate(selected, indices.size)
            np.add.at(gradient, indices, objective.gradient(selected, indices.size).astype(np.float32))
        return float(total), gradient

    def breakdown(self, dose: np.ndarray) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for objective in self.objectives:
            indices = self.voxel_indices[objective.structure]
            rows.append({**objective.to_dict(), "value": round(objective.evaluate(dose[indices], indices.size), 6)})
        for objective in self.disabled:
            rows.append({**objective.to_dict(), "value": None, "note": "disabled (zero weight)"})
        return rows

    def max_voxel_curvature(self, n_voxels: int) -> float:
        """Largest total second derivative any single voxel can contribute."""
        accumulator = np.zeros(n_voxels, dtype=np.float64)
        for objective in self.objectives:
            indices = self.voxel_indices[objective.structure]
            accumulator[indices] += objective.curvature(indices.size)
        return float(accumulator.max()) if accumulator.size else 0.0

    def structures(self) -> list[str]:
        seen: list[str] = []
        for objective in self.objectives + self.disabled:
            if objective.structure not in seen:
                seen.append(objective.structure)
        return seen


def bind_objectives(objectives: Iterable[Objective], resolve: Any) -> dict[str, np.ndarray]:
    """Resolve each referenced structure name to a flat voxel-index array."""
    bound: dict[str, np.ndarray] = {}
    for objective in objectives:
        if objective.structure not in bound:
            bound[objective.structure] = resolve(objective.structure)
    return bound
