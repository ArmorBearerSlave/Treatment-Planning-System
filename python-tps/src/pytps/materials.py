"""CT number to relative mass density.

This is a *generic* piecewise-linear lookup in the style of the default tables
shipped by open planning codes. It is not a scanner-specific CT-density
calibration curve, and no institution has commissioned it. Any quantitative
use requires a measured calibration for the actual scanner and protocol.
"""

from __future__ import annotations

import numpy as np

# (HU, relative mass density to water)
DEFAULT_HU_TO_DENSITY: tuple[tuple[float, float], ...] = (
    (-1024.0, 0.00121),   # air
    (-1000.0, 0.00121),
    (-800.0, 0.20),       # lung, inflated
    (-400.0, 0.60),
    (-100.0, 0.93),       # adipose
    (0.0, 1.000),         # water
    (60.0, 1.06),         # soft tissue / muscle
    (300.0, 1.18),        # trabecular bone
    (1000.0, 1.61),       # cortical bone
    (2000.0, 2.10),
    (3071.0, 2.60),
)

#: Below this relative density a voxel is treated as outside the patient for
#: dose-scoring and beam-entry purposes.
AIR_DENSITY_THRESHOLD = 0.05


def hu_to_density(hu: np.ndarray, table: tuple[tuple[float, float], ...] = DEFAULT_HU_TO_DENSITY) -> np.ndarray:
    """Map Hounsfield units to relative mass density, clamped at both ends."""
    values = np.asarray(hu, dtype=np.float32)
    xp = np.asarray([point[0] for point in table], dtype=np.float64)
    fp = np.asarray([point[1] for point in table], dtype=np.float64)
    if np.any(np.diff(xp) <= 0):
        raise ValueError("HU lookup table must be strictly increasing in HU")
    return np.interp(values, xp, fp).astype(np.float32)


def table_digest_rows(table: tuple[tuple[float, float], ...] = DEFAULT_HU_TO_DENSITY) -> list[list[float]]:
    """The lookup table as plain rows, for recording in a plan's provenance."""
    return [[float(hu), float(density)] for hu, density in table]
