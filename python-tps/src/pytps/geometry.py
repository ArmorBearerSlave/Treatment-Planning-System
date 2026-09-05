"""Voxel-grid geometry.

Coordinate conventions
----------------------
* World coordinates are patient **LPS millimetres**: +x patient left,
  +y patient posterior, +z patient superior.
* A grid is axis-aligned. A non-identity direction cosine matrix is rejected
  rather than silently resampled, because this package does no oblique
  reformatting.
* In-memory arrays are indexed ``array[i, j, k]`` with ``i`` along x, ``j``
  along y, ``k`` along z, i.e. shape ``(nx, ny, nz)``.
* Serialised flat value lists are **X-fastest XYZ** so that a case written here
  can be read by the other implementations in this repository without a
  transposition convention argument. :func:`Grid.from_flat` and
  :func:`Grid.to_flat` are the only places that conversion happens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np

IDENTITY_DIRECTION: tuple[float, ...] = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
DIRECTION_TOLERANCE = 1e-6


class GeometryError(ValueError):
    """Raised when a grid or a pair of grids cannot be used as given."""


@dataclass(frozen=True)
class Grid:
    """An axis-aligned LPS voxel lattice."""

    dimensions: tuple[int, int, int]
    spacing: tuple[float, float, float]
    origin: tuple[float, float, float]
    frame_id: str = "PYTPS-FRAME-1"
    direction: tuple[float, ...] = field(default=IDENTITY_DIRECTION)

    def __post_init__(self) -> None:
        object.__setattr__(self, "dimensions", tuple(int(value) for value in self.dimensions))
        object.__setattr__(self, "spacing", tuple(float(value) for value in self.spacing))
        object.__setattr__(self, "origin", tuple(float(value) for value in self.origin))
        object.__setattr__(self, "direction", tuple(float(value) for value in self.direction))
        if len(self.dimensions) != 3 or len(self.spacing) != 3 or len(self.origin) != 3:
            raise GeometryError("dimensions, spacing and origin each need three components")
        if any(value < 1 for value in self.dimensions):
            raise GeometryError(f"every dimension must be >= 1, got {self.dimensions}")
        if any(not np.isfinite(value) or value <= 0.0 for value in self.spacing):
            raise GeometryError(f"every spacing must be finite and > 0 mm, got {self.spacing}")
        if any(not np.isfinite(value) for value in self.origin):
            raise GeometryError(f"origin must be finite, got {self.origin}")
        if len(self.direction) != 9:
            raise GeometryError("direction must be nine row-major cosines")
        drift = float(np.max(np.abs(np.asarray(self.direction) - np.asarray(IDENTITY_DIRECTION))))
        if drift > DIRECTION_TOLERANCE:
            raise GeometryError(
                "only identity-direction LPS grids are supported; this grid is oblique "
                f"(max deviation {drift:.3e}). Resample it before planning."
            )

    # -- basic properties -------------------------------------------------
    @property
    def voxel_count(self) -> int:
        nx, ny, nz = self.dimensions
        return nx * ny * nz

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.dimensions

    @property
    def voxel_volume_mm3(self) -> float:
        sx, sy, sz = self.spacing
        return sx * sy * sz

    @property
    def voxel_volume_cm3(self) -> float:
        return self.voxel_volume_mm3 / 1000.0

    def axis_coordinates(self, axis: int) -> np.ndarray:
        """Voxel-centre world coordinates along one axis, in mm."""
        if axis not in (0, 1, 2):
            raise GeometryError(f"axis must be 0, 1 or 2, got {axis}")
        return self.origin[axis] + self.spacing[axis] * np.arange(self.dimensions[axis], dtype=np.float64)

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        """Outer corners of the voxel-centre lattice (mm)."""
        low = np.array([self.axis_coordinates(a)[0] for a in range(3)], dtype=np.float64)
        high = np.array([self.axis_coordinates(a)[-1] for a in range(3)], dtype=np.float64)
        return low, high

    def center(self) -> np.ndarray:
        low, high = self.bounds()
        return 0.5 * (low + high)

    def meshgrid_world(self, dtype: Any = np.float32) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Broadcast voxel-centre coordinates as three ``(nx, ny, nz)`` arrays."""
        xs, ys, zs = (self.axis_coordinates(a).astype(dtype) for a in range(3))
        return np.meshgrid(xs, ys, zs, indexing="ij", copy=False)

    def world_to_index(self, points: np.ndarray) -> np.ndarray:
        """Continuous (fractional) voxel indices for ``(..., 3)`` world points."""
        points = np.asarray(points, dtype=np.float64)
        if points.shape[-1] != 3:
            raise GeometryError("points must have a trailing axis of length 3")
        return (points - np.asarray(self.origin)) / np.asarray(self.spacing)

    def index_to_world(self, indices: np.ndarray) -> np.ndarray:
        indices = np.asarray(indices, dtype=np.float64)
        if indices.shape[-1] != 3:
            raise GeometryError("indices must have a trailing axis of length 3")
        return np.asarray(self.origin) + indices * np.asarray(self.spacing)

    # -- array/flat conversion -------------------------------------------
    def empty(self, dtype: Any = np.float32) -> np.ndarray:
        return np.zeros(self.dimensions, dtype=dtype)

    def from_flat(self, values: Iterable[float], dtype: Any = np.float32) -> np.ndarray:
        """X-fastest XYZ flat list -> ``(nx, ny, nz)`` array."""
        nx, ny, nz = self.dimensions
        flat = np.asarray(values, dtype=dtype).reshape(-1)
        if flat.size != self.voxel_count:
            raise GeometryError(f"expected {self.voxel_count} values for {self.dimensions}, got {flat.size}")
        return np.ascontiguousarray(flat.reshape(nz, ny, nx).transpose(2, 1, 0))

    def to_flat(self, array: np.ndarray) -> np.ndarray:
        """``(nx, ny, nz)`` array -> X-fastest XYZ flat array."""
        array = np.asarray(array)
        if tuple(array.shape) != self.dimensions:
            raise GeometryError(f"expected array of shape {self.dimensions}, got {array.shape}")
        return np.ascontiguousarray(array.transpose(2, 1, 0)).reshape(-1)

    def check_same_geometry(self, other: "Grid", what: str) -> None:
        if self.dimensions != other.dimensions:
            raise GeometryError(f"{what}: dimensions differ ({self.dimensions} vs {other.dimensions})")
        if not np.allclose(self.spacing, other.spacing, rtol=0.0, atol=1e-6):
            raise GeometryError(f"{what}: spacing differs ({self.spacing} vs {other.spacing})")
        if not np.allclose(self.origin, other.origin, rtol=0.0, atol=1e-4):
            raise GeometryError(f"{what}: origin differs ({self.origin} vs {other.origin})")

    # -- serialisation ----------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "dimensions": list(self.dimensions),
            "spacing": list(self.spacing),
            "origin": list(self.origin),
            "direction": list(self.direction),
            "frameID": self.frame_id,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Grid":
        missing = [key for key in ("dimensions", "spacing", "origin") if key not in payload]
        if missing:
            raise GeometryError(f"grid payload is missing {missing}")
        return cls(
            dimensions=tuple(payload["dimensions"]),
            spacing=tuple(payload["spacing"]),
            origin=tuple(payload["origin"]),
            frame_id=str(payload.get("frameID") or payload.get("frame_id") or "PYTPS-FRAME-1"),
            direction=tuple(payload.get("direction", IDENTITY_DIRECTION)),
        )


def trilinear_sample(volume: np.ndarray, indices: Sequence[np.ndarray], fill: float = 0.0) -> np.ndarray:
    """Trilinearly sample ``volume`` at continuous index coordinates.

    ``indices`` is a triple of broadcastable arrays ``(i, j, k)`` in voxel-index
    space. Samples whose centre falls outside the lattice return ``fill``;
    samples inside are clamped at the boundary so that the last half-voxel does
    not produce an artificial edge.
    """
    volume = np.asarray(volume)
    if volume.ndim != 3:
        raise GeometryError("volume must be three-dimensional")
    fi, fj, fk = (np.asarray(value, dtype=np.float32) for value in indices)
    nx, ny, nz = volume.shape

    inside = (
        (fi >= -0.5) & (fi <= nx - 0.5) & (fj >= -0.5) & (fj <= ny - 0.5) & (fk >= -0.5) & (fk <= nz - 0.5)
    )
    ci = np.clip(fi, 0.0, nx - 1.0)
    cj = np.clip(fj, 0.0, ny - 1.0)
    ck = np.clip(fk, 0.0, nz - 1.0)

    i0 = np.floor(ci).astype(np.int64)
    j0 = np.floor(cj).astype(np.int64)
    k0 = np.floor(ck).astype(np.int64)
    i1 = np.minimum(i0 + 1, nx - 1)
    j1 = np.minimum(j0 + 1, ny - 1)
    k1 = np.minimum(k0 + 1, nz - 1)
    ti = (ci - i0).astype(np.float32)
    tj = (cj - j0).astype(np.float32)
    tk = (ck - k0).astype(np.float32)

    def corner(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
        return volume[a, b, c].astype(np.float32, copy=False)

    c00 = corner(i0, j0, k0) * (1 - tk) + corner(i0, j0, k1) * tk
    c01 = corner(i0, j1, k0) * (1 - tk) + corner(i0, j1, k1) * tk
    c10 = corner(i1, j0, k0) * (1 - tk) + corner(i1, j0, k1) * tk
    c11 = corner(i1, j1, k0) * (1 - tk) + corner(i1, j1, k1) * tk
    c0 = c00 * (1 - tj) + c01 * tj
    c1 = c10 * (1 - tj) + c11 * tj
    result = c0 * (1 - ti) + c1 * ti
    return np.where(inside, result, np.float32(fill))
