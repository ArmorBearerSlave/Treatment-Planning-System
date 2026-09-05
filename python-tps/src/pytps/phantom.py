"""Deterministic synthetic phantom generator.

The phantom is an analytic male-pelvis caricature: an elliptical soft-tissue
body, two femoral heads, and prostate/bladder/rectum structures. It exists so
that the planning pipeline is runnable and testable with no external data,
under an explicit synthetic-only flag. It is not derived from any patient, is
not anatomically validated, and must not be used to characterise clinical
performance.
"""

from __future__ import annotations

import numpy as np

from .case import PlanningCase, Structure
from .geometry import Grid

# Label values. 0 is outside the patient.
LABEL_BODY = 1
LABEL_PROSTATE = 2
LABEL_BLADDER = 3
LABEL_RECTUM = 4
LABEL_FEMUR_L = 5
LABEL_FEMUR_R = 6

STRUCTURES: tuple[Structure, ...] = (
    Structure(LABEL_BODY, "BODY", (0.85, 0.80, 0.70)),
    Structure(LABEL_PROSTATE, "PROSTATE", (1.00, 0.20, 0.20)),
    Structure(LABEL_BLADDER, "BLADDER", (1.00, 0.75, 0.20)),
    Structure(LABEL_RECTUM, "RECTUM", (0.40, 0.55, 1.00)),
    Structure(LABEL_FEMUR_L, "FEMUR_L", (0.60, 0.60, 0.90)),
    Structure(LABEL_FEMUR_R, "FEMUR_R", (0.60, 0.60, 0.90)),
)

HU_AIR = -1000.0
HU_SOFT_TISSUE = 35.0
HU_FAT = -90.0
HU_BONE = 450.0
HU_BLADDER = 10.0
HU_RECTUM_GAS = -350.0


def _ellipsoid(x, y, z, center, radii) -> np.ndarray:
    cx, cy, cz = center
    rx, ry, rz = radii
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1.0


def build_phantom_case(
    case_id: str = "PYTPS-PELVIS-001",
    dimensions: tuple[int, int, int] = (72, 60, 48),
    spacing: tuple[float, float, float] = (4.0, 4.0, 4.0),
    seed: int = 20260905,
    noise_hu: float = 8.0,
) -> PlanningCase:
    """Build the synthetic pelvis phantom centred on the world origin."""
    if noise_hu < 0.0:
        raise ValueError("noise_hu must be >= 0")
    nx, ny, nz = (int(value) for value in dimensions)
    sx, sy, sz = (float(value) for value in spacing)
    # Centre the field of view on the isocentre at the world origin.
    origin = (-0.5 * (nx - 1) * sx, -0.5 * (ny - 1) * sy, -0.5 * (nz - 1) * sz)
    grid = Grid(dimensions=(nx, ny, nz), spacing=(sx, sy, sz), origin=origin, frame_id=f"{case_id}-FRAME")
    x, y, z = grid.meshgrid_world(dtype=np.float32)

    span_x = 0.5 * (nx - 1) * sx
    span_y = 0.5 * (ny - 1) * sy
    span_z = 0.5 * (nz - 1) * sz

    body_rx = 0.86 * span_x
    body_ry = 0.72 * span_y
    body = ((x / body_rx) ** 2 + (y / body_ry) ** 2) <= 1.0
    body &= np.abs(z) <= 0.94 * span_z

    fat_rim = ((x / (0.90 * body_rx)) ** 2 + (y / (0.90 * body_ry)) ** 2) > 1.0

    # Structures, in millimetres relative to the isocentre.
    prostate = _ellipsoid(x, y, z, (0.0, 6.0, 0.0), (22.0, 20.0, 20.0))
    bladder = _ellipsoid(x, y, z, (0.0, -26.0, 14.0), (30.0, 22.0, 24.0))
    rectum = ((x / 16.0) ** 2 + ((y - 40.0) / 16.0) ** 2 <= 1.0) & (np.abs(z) <= 0.80 * span_z)
    femur_l = _ellipsoid(x, y, z, (0.62 * body_rx, 4.0, 0.0), (24.0, 24.0, 0.55 * span_z))
    femur_r = _ellipsoid(x, y, z, (-0.62 * body_rx, 4.0, 0.0), (24.0, 24.0, 0.55 * span_z))

    # Later assignments win, so the order below encodes label precedence.
    labels = np.zeros(grid.dimensions, dtype=np.int16)
    labels[body] = LABEL_BODY
    labels[body & femur_l] = LABEL_FEMUR_L
    labels[body & femur_r] = LABEL_FEMUR_R
    labels[body & bladder] = LABEL_BLADDER
    labels[body & rectum] = LABEL_RECTUM
    labels[body & prostate] = LABEL_PROSTATE

    ct = np.full(grid.dimensions, HU_AIR, dtype=np.float32)
    ct[body] = HU_SOFT_TISSUE
    ct[body & fat_rim] = HU_FAT
    ct[labels == LABEL_FEMUR_L] = HU_BONE
    ct[labels == LABEL_FEMUR_R] = HU_BONE
    ct[labels == LABEL_BLADDER] = HU_BLADDER
    ct[labels == LABEL_RECTUM] = HU_RECTUM_GAS
    ct[labels == LABEL_PROSTATE] = HU_SOFT_TISSUE + 10.0

    if noise_hu > 0.0:
        rng = np.random.default_rng(seed)
        ct[body] += rng.normal(0.0, noise_hu, size=int(np.count_nonzero(body))).astype(np.float32)

    present = {int(value) for value in np.unique(labels) if value != 0}
    missing = [structure.name for structure in STRUCTURES if structure.label not in present]
    if missing:
        raise ValueError(
            f"the requested grid is too small to contain {missing}; "
            "increase dimensions or reduce spacing"
        )

    return PlanningCase(
        case_id=case_id,
        grid=grid,
        ct_hu=ct,
        labels=labels,
        structures=list(STRUCTURES),
        name="Synthetic analytic pelvis phantom",
        synthetic_only=True,
        clinical_use_permitted=False,
        provenance={
            "generator": "pytps.phantom.build_phantom_case",
            "seed": int(seed),
            "noiseHU": float(noise_hu),
            "note": "Analytic geometry. Not patient-derived and not anatomically validated.",
        },
    )
