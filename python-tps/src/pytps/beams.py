"""Beam geometry and bixel (beamlet) grids.

Only coplanar photon beams on a fixed isocentre are modelled: gantry rotation
in the axial plane, couch and collimator at zero. Angles follow IEC 61217 for a
head-first supine orientation, mapped into LPS world coordinates:

* gantry 0 deg  - source anterior to the patient, beam travelling posteriorly.
* gantry 90 deg - source on the patient's left, beam travelling to the right.

For gantry angle ``phi``::

    source    = isocentre + SAD * ( sin phi, -cos phi, 0 )
    beam axis = ( -sin phi,  cos phi, 0 )            (source -> isocentre)
    u axis    = (  cos phi,  sin phi, 0 )            (in-plane lateral)
    v axis    = (  0, 0, 1 )                          (patient superior)

Lateral positions ``(u, v)`` are always reported **projected back to the
isocentre plane**, so a bixel keeps one coordinate pair at every depth and the
beam divergence is carried by an explicit inverse-square factor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

DEFAULT_SAD_MM = 1000.0
MIN_BIXEL_WIDTH_MM = 2.0
MAX_BIXEL_WIDTH_MM = 30.0
MAX_BEAMS = 12


class BeamError(ValueError):
    """Raised for a beam arrangement this engine will not model."""


def beam_axes(gantry_deg: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(beam_axis, u_axis, v_axis)`` unit vectors in LPS."""
    phi = np.deg2rad(float(gantry_deg))
    sin_phi, cos_phi = float(np.sin(phi)), float(np.cos(phi))
    beam_axis = np.array([-sin_phi, cos_phi, 0.0], dtype=np.float64)
    u_axis = np.array([cos_phi, sin_phi, 0.0], dtype=np.float64)
    v_axis = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    return beam_axis, u_axis, v_axis


@dataclass(frozen=True)
class BixelGrid:
    """A regular lattice of beamlet centres in the isocentre plane (mm)."""

    u_start: float
    v_start: float
    width: float
    n_u: int
    n_v: int

    @property
    def count(self) -> int:
        return self.n_u * self.n_v

    def u_centers(self) -> np.ndarray:
        return self.u_start + self.width * np.arange(self.n_u, dtype=np.float64)

    def v_centers(self) -> np.ndarray:
        return self.v_start + self.width * np.arange(self.n_v, dtype=np.float64)

    def to_dict(self) -> dict[str, Any]:
        return {
            "uStartMM": self.u_start,
            "vStartMM": self.v_start,
            "widthMM": self.width,
            "nU": self.n_u,
            "nV": self.n_v,
            "count": self.count,
        }


@dataclass(frozen=True)
class Beam:
    """One coplanar photon beam and its bixel grid."""

    index: int
    gantry_deg: float
    isocenter: tuple[float, float, float]
    sad_mm: float
    bixels: BixelGrid

    @property
    def axes(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return beam_axes(self.gantry_deg)

    @property
    def source(self) -> np.ndarray:
        phi = np.deg2rad(self.gantry_deg)
        offset = np.array([np.sin(phi), -np.cos(phi), 0.0], dtype=np.float64)
        return np.asarray(self.isocenter, dtype=np.float64) + self.sad_mm * offset

    def project(self, points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Project world points into ``(u_iso, v_iso, distance_from_source)``.

        ``points`` is ``(..., 3)`` in LPS mm. Points at or behind the source
        plane are pushed to a small positive distance so the inverse-square
        factor stays finite; they carry no dose because their radiological
        depth is zero.
        """
        beam_axis, u_axis, v_axis = self.axes
        relative = np.asarray(points, dtype=np.float32) - self.source.astype(np.float32)
        distance = relative @ beam_axis.astype(np.float32)
        distance = np.maximum(distance, np.float32(1.0))
        scale = np.float32(self.sad_mm) / distance
        u_iso = (relative @ u_axis.astype(np.float32)) * scale
        v_iso = (relative @ v_axis.astype(np.float32)) * scale
        return u_iso, v_iso, distance

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "gantryDeg": self.gantry_deg,
            "couchDeg": 0.0,
            "collimatorDeg": 0.0,
            "isocenterMM": list(self.isocenter),
            "sadMM": self.sad_mm,
            "sourceMM": [round(float(value), 4) for value in self.source],
            "bixels": self.bixels.to_dict(),
        }


def build_bixel_grid(
    beam_index: int,
    gantry_deg: float,
    isocenter: Sequence[float],
    target_points: np.ndarray,
    bixel_width_mm: float,
    margin_mm: float,
    sad_mm: float = DEFAULT_SAD_MM,
) -> Beam:
    """Size a bixel grid so it covers the target projection plus a margin."""
    if not MIN_BIXEL_WIDTH_MM <= bixel_width_mm <= MAX_BIXEL_WIDTH_MM:
        raise BeamError(
            f"bixel width {bixel_width_mm} mm is outside the supported "
            f"{MIN_BIXEL_WIDTH_MM}-{MAX_BIXEL_WIDTH_MM} mm range"
        )
    if margin_mm < 0.0:
        raise BeamError("field margin must be >= 0 mm")
    if sad_mm <= 0.0:
        raise BeamError("source-axis distance must be > 0 mm")
    target_points = np.asarray(target_points, dtype=np.float32)
    if target_points.ndim != 2 or target_points.shape[1] != 3 or target_points.shape[0] == 0:
        raise BeamError("target_points must be a non-empty (N, 3) array of world points")

    probe = Beam(
        index=beam_index,
        gantry_deg=float(gantry_deg),
        isocenter=tuple(float(value) for value in isocenter),
        sad_mm=float(sad_mm),
        bixels=BixelGrid(0.0, 0.0, float(bixel_width_mm), 1, 1),
    )
    u_iso, v_iso, _ = probe.project(target_points)

    def axis_extent(values: np.ndarray) -> tuple[float, int]:
        low = float(values.min()) - margin_mm
        high = float(values.max()) + margin_mm
        count = max(1, int(np.ceil((high - low) / bixel_width_mm)) + 1)
        center = 0.5 * (low + high)
        start = center - 0.5 * (count - 1) * bixel_width_mm
        return start, count

    u_start, n_u = axis_extent(u_iso)
    v_start, n_v = axis_extent(v_iso)
    return Beam(
        index=beam_index,
        gantry_deg=float(gantry_deg),
        isocenter=probe.isocenter,
        sad_mm=float(sad_mm),
        bixels=BixelGrid(u_start, v_start, float(bixel_width_mm), n_u, n_v),
    )


def build_beams(
    gantry_angles: Sequence[float],
    isocenter: Sequence[float],
    target_points: np.ndarray,
    bixel_width_mm: float,
    margin_mm: float,
    sad_mm: float = DEFAULT_SAD_MM,
) -> list[Beam]:
    angles = [float(angle) for angle in gantry_angles]
    if not angles:
        raise BeamError("at least one gantry angle is required")
    if len(angles) > MAX_BEAMS:
        raise BeamError(f"at most {MAX_BEAMS} beams are supported, got {len(angles)}")
    normalized = [angle % 360.0 for angle in angles]
    if len(set(round(angle, 6) for angle in normalized)) != len(normalized):
        raise BeamError(f"duplicate gantry angles are not allowed: {angles}")
    return [
        build_bixel_grid(index, angle, isocenter, target_points, bixel_width_mm, margin_mm, sad_mm)
        for index, angle in enumerate(normalized)
    ]
