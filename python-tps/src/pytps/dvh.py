"""Dose-volume histograms and the metrics derived from them.

Doses are total-course physical Gy. Volumes come from voxel counting on the CT
grid; no sub-voxel surface reconstruction is performed, so small structures
carry a discretisation error of roughly one voxel layer. ``D2`` is reported in
place of a true point maximum because a single-voxel maximum is dominated by
grid noise, and both are shown.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

DEFAULT_BINS = 1024


def nearest_rank_dose(values: np.ndarray, volume_fraction: float) -> float:
    """``Dx`` by nearest rank on descending samples, with equal voxel volumes.

    This is the definition CERR's DVH tooling uses. :meth:`StructureDVH.
    dose_at_volume_fraction` instead interpolates a binned cumulative
    histogram. The two answer the same question and disagree by up to a bin
    width, so a comparison against an external tool has to state which one it
    used - :mod:`pytps.external.cerr` reports both.
    """
    samples = np.asarray(values, dtype=np.float64).reshape(-1)
    if samples.size == 0:
        raise ValueError("cannot take a dose percentile of an empty structure")
    if not 0.0 <= volume_fraction <= 1.0:
        raise ValueError("volume fraction must be between 0 and 1")
    ordered = np.sort(samples)[::-1]
    rank = max(1, int(np.ceil(volume_fraction * ordered.size)))
    return float(ordered[rank - 1])


@dataclass(frozen=True)
class StructureDVH:
    """A cumulative DVH plus scalar metrics for one structure."""

    structure: str
    voxels: int
    volume_cm3: float
    dose_bins_gy: np.ndarray
    volume_fraction: np.ndarray
    metrics: dict[str, float]

    def dose_at_volume_fraction(self, fraction: float) -> float:
        """Dose covering at least ``fraction`` of the volume (``Dx``)."""
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("volume fraction must be between 0 and 1")
        # volume_fraction is non-increasing in dose.
        below = np.flatnonzero(self.volume_fraction < fraction)
        if below.size == 0:
            return float(self.dose_bins_gy[-1])
        index = int(below[0])
        if index == 0:
            return float(self.dose_bins_gy[0])
        high_v, low_v = self.volume_fraction[index - 1], self.volume_fraction[index]
        high_d, low_d = self.dose_bins_gy[index - 1], self.dose_bins_gy[index]
        if high_v == low_v:
            return float(high_d)
        weight = (high_v - fraction) / (high_v - low_v)
        return float(high_d + weight * (low_d - high_d))

    def volume_fraction_at_dose(self, dose_gy: float) -> float:
        """Fraction of the volume receiving at least ``dose_gy`` (``Vx``)."""
        return float(np.interp(dose_gy, self.dose_bins_gy, self.volume_fraction, left=1.0, right=0.0))

    def to_dict(self, curve_points: int = 128) -> dict[str, Any]:
        stride = max(1, self.dose_bins_gy.size // max(1, curve_points))
        return {
            "structure": self.structure,
            "voxels": self.voxels,
            "volumeCm3": round(self.volume_cm3, 4),
            "metrics": {key: round(float(value), 4) for key, value in self.metrics.items()},
            "curve": {
                "doseGy": [round(float(value), 4) for value in self.dose_bins_gy[::stride]],
                "volumeFraction": [round(float(value), 6) for value in self.volume_fraction[::stride]],
            },
        }


def compute_dvh(
    dose: np.ndarray,
    mask_indices: np.ndarray,
    structure: str,
    voxel_volume_cm3: float,
    bins: int = DEFAULT_BINS,
    max_dose_gy: float | None = None,
    reference_dose_gy: float | None = None,
) -> StructureDVH:
    """Cumulative DVH for one structure."""
    indices = np.asarray(mask_indices, dtype=np.int64)
    if indices.size == 0:
        raise ValueError(f"structure {structure!r} contains no voxels")
    if bins < 2:
        raise ValueError("bins must be >= 2")
    values = np.asarray(dose, dtype=np.float32).reshape(-1)[indices]

    ceiling = float(max_dose_gy if max_dose_gy is not None else values.max())
    ceiling = max(ceiling * 1.02, 1e-6)
    edges = np.linspace(0.0, ceiling, bins + 1, dtype=np.float64)
    counts, _ = np.histogram(values, bins=edges)
    # Cumulative "at least this dose", evaluated at the bin's lower edge.
    cumulative = np.concatenate([[values.size], values.size - np.cumsum(counts)])
    fraction = cumulative.astype(np.float64) / float(values.size)

    metrics: dict[str, float] = {
        "meanGy": float(values.mean()),
        "minGy": float(values.min()),
        "maxGy": float(values.max()),
        "stdGy": float(values.std()),
    }
    dvh = StructureDVH(
        structure=structure,
        voxels=int(values.size),
        volume_cm3=float(values.size) * float(voxel_volume_cm3),
        dose_bins_gy=edges,
        volume_fraction=fraction,
        metrics=metrics,
    )
    for label, fraction_value in (("D2Gy", 0.02), ("D50Gy", 0.50), ("D95Gy", 0.95), ("D98Gy", 0.98)):
        dvh.metrics[label] = dvh.dose_at_volume_fraction(fraction_value)
    if reference_dose_gy and reference_dose_gy > 0.0:
        for percent in (95, 100, 107):
            level = reference_dose_gy * percent / 100.0
            dvh.metrics[f"V{percent}pct"] = dvh.volume_fraction_at_dose(level)
        dvh.metrics["homogeneityIndex"] = (
            (dvh.metrics["D2Gy"] - dvh.metrics["D98Gy"]) / dvh.metrics["D50Gy"]
            if dvh.metrics["D50Gy"] > 0.0
            else float("nan")
        )
    return dvh


def compute_dvh_set(
    dose: np.ndarray,
    structures: dict[str, np.ndarray],
    voxel_volume_cm3: float,
    bins: int = DEFAULT_BINS,
    reference_dose_gy: float | None = None,
    targets: Sequence[str] = (),
) -> dict[str, StructureDVH]:
    """DVHs for several structures on one shared dose scale."""
    ceiling = float(np.asarray(dose, dtype=np.float32).max())
    target_names = {name for name in targets}
    return {
        name: compute_dvh(
            dose,
            indices,
            name,
            voxel_volume_cm3,
            bins=bins,
            max_dose_gy=ceiling,
            reference_dose_gy=reference_dose_gy if name in target_names else None,
        )
        for name, indices in structures.items()
    }
