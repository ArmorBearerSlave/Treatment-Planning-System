"""Pencil-beam photon dose engine and dose-influence matrix.

Model
-----
For a bixel ``b`` and a voxel ``i`` the engine evaluates

    D[i, b] = (SAD / r_i)^2 * T(z_i) * B(u_i - u_b; s_i) * B(v_i - v_b; s_i)

where ``r_i`` is the distance from the source, ``z_i`` the **radiological**
depth (the density-weighted path length from the source), ``u, v`` the lateral
coordinates projected onto the isocentre plane, and ``B`` the integral of a
unit Gaussian across the bixel's width. Integrating rather than sampling the
Gaussian is what makes the result independent of the bixel width: the bixel
weights over a full field sum to one whatever width is chosen.

    T(z) = (1 - exp(-beta z)) * exp(-mu z)          depth dose
    s(z) = sqrt(s0^2 + (a z)^2) * SAD / r           lateral spread, at isocentre

Radiological depth is ray-traced once per beam on a beam's-eye-view lattice by
cumulative integration of relative mass density along divergent rays, then
interpolated back onto the CT grid.

Scope and honesty
-----------------
This is a **single-Gaussian pencil beam with a central-axis density
correction**. It reproduces build-up, exponential attenuation, inverse-square
falloff, penumbra growth with depth, and first-order heterogeneity effects
along the ray. It does **not** model lateral electronic disequilibrium at
density interfaces, contaminant electrons, head scatter, MLC transmission,
backscatter, or beam hardening; it uses one generic 6 MV-like parameter set
rather than a commissioned beam model; and it carries no absolute output
calibration. Absolute dose values are only meaningful because the optimiser
scales fluence to the requested prescription. Treat the numbers as a
self-consistent research quantity, not as delivered dose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from .beams import Beam
from .case import PlanningCase
from .geometry import Grid, trilinear_sample
from .materials import AIR_DENSITY_THRESHOLD
from .special import gaussian_bar_integral

SQRT_2PI = float(np.sqrt(2.0 * np.pi))


@dataclass(frozen=True)
class PencilBeamSettings:
    """Generic photon kernel parameters. Not a commissioned beam model."""

    #: Effective linear attenuation coefficient in water, 1/mm.
    mu_per_mm: float = 0.0045
    #: Build-up rate, 1/mm. With the default mu this puts d_max near 15 mm.
    buildup_per_mm: float = 0.27
    #: Lateral spread at the surface (source size and penumbra), mm.
    sigma0_mm: float = 3.0
    #: Growth of lateral spread per mm of radiological depth.
    sigma_growth: float = 0.055
    #: Ray-marching step for the radiological-depth integration, mm.
    depth_step_mm: float = 2.5
    #: Lateral sample spacing of the beam's-eye-view lattice at isocentre, mm.
    lateral_step_mm: float = 4.0
    #: Gaussian truncation, in standard deviations.
    cutoff_sigmas: float = 3.0
    #: Influence entries below this fraction of the beam peak are dropped.
    kernel_threshold: float = 2.0e-4
    #: Hard guard on influence-matrix size.
    max_entries: int = 40_000_000
    #: Voxel chunk size for the scatter loop.
    chunk_size: int = 40_000

    def to_dict(self) -> dict[str, Any]:
        return {
            "muPerMM": self.mu_per_mm,
            "buildupPerMM": self.buildup_per_mm,
            "sigma0MM": self.sigma0_mm,
            "sigmaGrowth": self.sigma_growth,
            "depthStepMM": self.depth_step_mm,
            "lateralStepMM": self.lateral_step_mm,
            "cutoffSigmas": self.cutoff_sigmas,
            "kernelThreshold": self.kernel_threshold,
            "model": "single-Gaussian pencil beam, central-axis radiological depth",
            "commissioned": False,
            "absoluteCalibration": None,
        }

    def depth_dose(self, radiological_depth_mm: np.ndarray) -> np.ndarray:
        z = np.asarray(radiological_depth_mm, dtype=np.float32)
        return (1.0 - np.exp(-self.buildup_per_mm * z)) * np.exp(-self.mu_per_mm * z)

    def dmax_mm(self) -> float:
        """Depth of maximum dose in water for the current parameters."""
        beta, mu = self.buildup_per_mm, self.mu_per_mm
        return float(np.log((beta + mu) / mu) / beta)


class DoseInfluence:
    """Sparse voxel-by-bixel dose-influence matrix in coordinate form.

    Stored as parallel ``rows`` / ``cols`` / ``values`` arrays. ``bincount``
    gives both products without a sparse-matrix dependency, which keeps the
    package to numpy alone.
    """

    def __init__(
        self,
        rows: np.ndarray,
        cols: np.ndarray,
        values: np.ndarray,
        n_voxels: int,
        n_bixels: int,
        beams: Sequence[Beam],
        bixel_offsets: Sequence[int],
        settings: PencilBeamSettings,
    ) -> None:
        self.rows = np.ascontiguousarray(rows, dtype=np.int64)
        self.cols = np.ascontiguousarray(cols, dtype=np.int64)
        self.values = np.ascontiguousarray(values, dtype=np.float32)
        if not (self.rows.shape == self.cols.shape == self.values.shape):
            raise ValueError("rows, cols and values must have the same shape")
        self.n_voxels = int(n_voxels)
        self.n_bixels = int(n_bixels)
        self.beams = list(beams)
        self.bixel_offsets = list(int(value) for value in bixel_offsets)
        self.settings = settings

    @property
    def nnz(self) -> int:
        return int(self.values.size)

    @property
    def density(self) -> float:
        total = float(self.n_voxels) * float(self.n_bixels)
        return self.nnz / total if total else 0.0

    def dose(self, weights: np.ndarray) -> np.ndarray:
        """Flat voxel dose for bixel weights ``w`` (i.e. ``D @ w``)."""
        weights = np.asarray(weights, dtype=np.float32).reshape(-1)
        if weights.size != self.n_bixels:
            raise ValueError(f"expected {self.n_bixels} bixel weights, got {weights.size}")
        contributions = self.values * weights[self.cols]
        return np.bincount(self.rows, weights=contributions, minlength=self.n_voxels).astype(np.float32)

    def transpose_dot(self, voxel_values: np.ndarray) -> np.ndarray:
        """Bixel-space gradient for a voxel-space vector (i.e. ``D.T @ y``)."""
        voxel_values = np.asarray(voxel_values, dtype=np.float32).reshape(-1)
        if voxel_values.size != self.n_voxels:
            raise ValueError(f"expected {self.n_voxels} voxel values, got {voxel_values.size}")
        contributions = self.values * voxel_values[self.rows]
        return np.bincount(self.cols, weights=contributions, minlength=self.n_bixels).astype(np.float32)

    def column_norms(self) -> np.ndarray:
        """Euclidean norm of each bixel's dose column, ``||D[:, b]||``.

        Field-edge bixels have much smaller columns than central ones, which is
        the main source of ill-conditioning; the optimiser uses these norms as
        a diagonal preconditioner.
        """
        squares = np.bincount(
            self.cols, weights=self.values.astype(np.float64) ** 2, minlength=self.n_bixels
        )
        return np.sqrt(squares).astype(np.float32)

    def spectral_norm_squared(
        self, iterations: int = 24, seed: int = 7, scale: np.ndarray | None = None
    ) -> float:
        """Power iteration for the largest eigenvalue of ``(D S).T (D S)``.

        ``scale`` is the diagonal of ``S``; ``None`` means the identity.
        """
        rng = np.random.default_rng(seed)
        vector = rng.random(self.n_bixels).astype(np.float32)
        norm = float(np.linalg.norm(vector))
        if norm == 0.0:
            return 0.0
        vector /= norm
        eigenvalue = 0.0
        for _ in range(int(iterations)):
            scaled = vector if scale is None else vector * scale
            product = self.transpose_dot(self.dose(scaled))
            if scale is not None:
                product = product * scale
            eigenvalue = float(np.linalg.norm(product))
            if eigenvalue <= 0.0:
                return 0.0
            vector = product / np.float32(eigenvalue)
        return eigenvalue

    def to_dict(self) -> dict[str, Any]:
        return {
            "voxels": self.n_voxels,
            "bixels": self.n_bixels,
            "nonzeros": self.nnz,
            "fill": round(self.density, 6),
            "beams": [beam.to_dict() for beam in self.beams],
            "kernel": self.settings.to_dict(),
        }


@dataclass
class BeamGeometryFields:
    """Per-voxel beam-frame quantities for one beam, on the scoring subset."""

    u_iso: np.ndarray
    v_iso: np.ndarray
    distance: np.ndarray
    radiological_depth: np.ndarray
    stats: dict[str, float] = field(default_factory=dict)


def radiological_depth_field(
    beam: Beam,
    grid: Grid,
    density: np.ndarray,
    u_iso: np.ndarray,
    v_iso: np.ndarray,
    distance: np.ndarray,
    settings: PencilBeamSettings,
) -> np.ndarray:
    """Radiological depth (mm of water-equivalent) at each scoring voxel.

    A beam's-eye-view lattice is marched from the source outwards. Because the
    lattice depth axis is the distance along the ray, the path increment is the
    step size itself, with no obliquity correction needed.
    """
    step = float(settings.depth_step_mm)
    lateral = float(settings.lateral_step_mm)
    if step <= 0.0 or lateral <= 0.0:
        raise ValueError("depth_step_mm and lateral_step_mm must be > 0")

    pad = 2.0 * lateral
    u_low, u_high = float(u_iso.min()) - pad, float(u_iso.max()) + pad
    v_low, v_high = float(v_iso.min()) - pad, float(v_iso.max()) + pad
    n_u = max(2, int(np.ceil((u_high - u_low) / lateral)) + 1)
    n_v = max(2, int(np.ceil((v_high - v_low) / lateral)) + 1)

    d_low = max(step, float(distance.min()) - step)
    d_high = float(distance.max()) + step
    n_d = max(2, int(np.ceil((d_high - d_low) / step)) + 1)

    beam_axis, u_axis, v_axis = beam.axes
    source = beam.source
    u_samples = (u_low + lateral * np.arange(n_u, dtype=np.float64))[:, None]
    v_samples = (v_low + lateral * np.arange(n_v, dtype=np.float64))[None, :]
    origin = np.asarray(grid.origin, dtype=np.float64)
    spacing = np.asarray(grid.spacing, dtype=np.float64)

    depths = np.zeros((n_u, n_v, n_d), dtype=np.float32)
    running = np.zeros((n_u, n_v), dtype=np.float32)
    previous = np.zeros((n_u, n_v), dtype=np.float32)
    for index in range(n_d):
        d = d_low + step * index
        scale = d / beam.sad_mm
        points = (
            source[None, None, :]
            + d * beam_axis[None, None, :]
            + (u_samples * scale)[:, :, None] * u_axis[None, None, :]
            + (v_samples * scale)[:, :, None] * v_axis[None, None, :]
        )
        indices = (points - origin) / spacing
        rho = trilinear_sample(density, (indices[..., 0], indices[..., 1], indices[..., 2]), fill=0.0)
        # Trapezoidal accumulation along the ray.
        running = running + np.float32(0.5 * step) * (previous + rho)
        depths[:, :, index] = running
        previous = rho

    fi = (u_iso - np.float32(u_low)) / np.float32(lateral)
    fj = (v_iso - np.float32(v_low)) / np.float32(lateral)
    fk = (distance - np.float32(d_low)) / np.float32(step)
    return trilinear_sample(depths, (fi, fj, fk), fill=0.0)


def scoring_mask(case: PlanningCase) -> np.ndarray:
    """Voxels that can receive or matter for dose: patient tissue or a label."""
    return (case.density() > AIR_DENSITY_THRESHOLD) | (case.labels != 0)


def compute_influence(
    case: PlanningCase,
    beams: Sequence[Beam],
    settings: PencilBeamSettings | None = None,
    progress: Any = None,
) -> DoseInfluence:
    """Build the sparse dose-influence matrix for a case and beam set."""
    settings = settings or PencilBeamSettings()
    grid = case.grid
    density = case.density()
    mask = scoring_mask(case)
    voxel_indices = np.flatnonzero(mask.reshape(-1)).astype(np.int64)
    if voxel_indices.size == 0:
        raise ValueError("the case has no scoring voxels; check the CT and label volumes")

    x, y, z = grid.meshgrid_world(dtype=np.float32)
    points = np.stack(
        [x.reshape(-1)[voxel_indices], y.reshape(-1)[voxel_indices], z.reshape(-1)[voxel_indices]], axis=1
    )
    del x, y, z

    rows_out: list[np.ndarray] = []
    cols_out: list[np.ndarray] = []
    vals_out: list[np.ndarray] = []
    offsets: list[int] = []
    total_entries = 0
    running_offset = 0

    for beam in beams:
        offsets.append(running_offset)
        bixels = beam.bixels
        u_iso, v_iso, distance = beam.project(points)
        depth = radiological_depth_field(beam, grid, density, u_iso, v_iso, distance, settings)

        base = settings.depth_dose(depth) * (np.float32(beam.sad_mm) / distance) ** 2
        sigma_phys = np.sqrt(
            np.float32(settings.sigma0_mm) ** 2 + (np.float32(settings.sigma_growth) * depth) ** 2
        )
        sigma = (sigma_phys * np.float32(beam.sad_mm) / distance).astype(np.float32)

        live = base > 0.0
        if not np.any(live):
            running_offset += bixels.count
            continue

        width = np.float32(bixels.width)
        reach = settings.cutoff_sigmas * float(sigma[live].max()) + 0.5 * float(width)
        half_window = int(np.clip(int(np.ceil(reach / float(width))), 1, 8))
        offsets_1d = np.arange(-half_window, half_window + 1, dtype=np.int64)

        # The bixel weights are bounded by one, so the peak entry is bounded by
        # the largest depth-dose-times-inverse-square factor in the field.
        threshold = np.float32(settings.kernel_threshold * float(base.max()))

        candidates = np.flatnonzero(live)
        for start in range(0, candidates.size, settings.chunk_size):
            chunk = candidates[start : start + settings.chunk_size]
            cu = u_iso[chunk]
            cv = v_iso[chunk]
            cs = sigma[chunk][:, None]
            cbase = base[chunk]

            ju = np.rint((cu - np.float32(bixels.u_start)) / width).astype(np.int64)[:, None] + offsets_1d
            jv = np.rint((cv - np.float32(bixels.v_start)) / width).astype(np.int64)[:, None] + offsets_1d
            valid_u = (ju >= 0) & (ju < bixels.n_u)
            valid_v = (jv >= 0) & (jv < bixels.n_v)

            delta_u = cu[:, None] - (np.float32(bixels.u_start) + ju.astype(np.float32) * width)
            delta_v = cv[:, None] - (np.float32(bixels.v_start) + jv.astype(np.float32) * width)
            gu = np.where(valid_u, gaussian_bar_integral(delta_u, cs, float(width)), np.float32(0.0))
            gv = np.where(valid_v, gaussian_bar_integral(delta_v, cs, float(width)), np.float32(0.0))

            block = cbase[:, None, None] * gu[:, :, None] * gv[:, None, :]
            keep = block > threshold
            if not np.any(keep):
                continue
            kept_rows = np.broadcast_to(voxel_indices[chunk][:, None, None], block.shape)[keep]
            kept_cols = (
                np.broadcast_to(ju[:, :, None] * bixels.n_v + jv[:, None, :], block.shape)[keep] + running_offset
            )
            rows_out.append(kept_rows.astype(np.int64))
            cols_out.append(kept_cols.astype(np.int64))
            vals_out.append(block[keep].astype(np.float32))
            total_entries += int(kept_rows.size)
            if total_entries > settings.max_entries:
                raise MemoryError(
                    f"dose-influence matrix exceeded {settings.max_entries:,} entries. "
                    "Use a coarser CT grid, a wider bixel, fewer beams, or raise "
                    "PencilBeamSettings.max_entries deliberately."
                )

        running_offset += bixels.count
        if progress is not None:
            progress(
                f"beam {beam.index} (gantry {beam.gantry_deg:g} deg): "
                f"{bixels.count} bixels, {total_entries:,} influence entries so far"
            )

    if not rows_out:
        raise ValueError(
            "no dose influence was produced. The beams may miss the patient, or the "
            "kernel threshold may be too high."
        )
    return DoseInfluence(
        rows=np.concatenate(rows_out),
        cols=np.concatenate(cols_out),
        values=np.concatenate(vals_out),
        n_voxels=int(grid.voxel_count),
        n_bixels=running_offset,
        beams=list(beams),
        bixel_offsets=offsets,
        settings=settings,
    )
