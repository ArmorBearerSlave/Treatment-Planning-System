"""Physics checks on the pencil-beam engine.

Each test states the analytic expectation it checks against, so a failure
identifies which modelled effect broke rather than only that a number moved.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.beams import build_bixel_grid
from pytps.case import PlanningCase, Structure
from pytps.dose import PencilBeamSettings, compute_influence, radiological_depth_field
from pytps.geometry import Grid

SETTINGS = PencilBeamSettings()


def water_case(
    dimensions: tuple[int, int, int] = (48, 60, 12),
    spacing: tuple[float, float, float] = (4.0, 4.0, 4.0),
    case_id: str = "WATER-BOX",
) -> PlanningCase:
    """A uniform water box centred on the world origin, labelled as one structure."""
    nx, ny, nz = dimensions
    sx, sy, sz = spacing
    origin = (-0.5 * (nx - 1) * sx, -0.5 * (ny - 1) * sy, -0.5 * (nz - 1) * sz)
    grid = Grid(dimensions, spacing, origin, frame_id="WATER")
    return PlanningCase(
        case_id=case_id,
        grid=grid,
        ct_hu=np.zeros(dimensions, dtype=np.float32),
        labels=np.ones(dimensions, dtype=np.int16),
        structures=[Structure(1, "WATER")],
    )


def broad_beam(case: PlanningCase, gantry_deg: float = 0.0, bixel_width_mm: float = 10.0):
    """One beam whose field covers the whole phantom cross-section."""
    span = 0.45 * min(
        case.grid.dimensions[0] * case.grid.spacing[0], case.grid.dimensions[2] * case.grid.spacing[2]
    )
    corners = np.array(
        [[u, 0.0, v] for u in (-span, span) for v in (-span, span)], dtype=np.float32
    )
    return build_bixel_grid(0, gantry_deg, [0.0, 0.0, 0.0], corners, bixel_width_mm, 20.0)


def central_axis_samples(case: PlanningCase, beam, dose: np.ndarray):
    """Dose along the central axis (x = z = 0) with the depth of each sample."""
    volume = dose.reshape(case.grid.dimensions)
    xs = case.grid.axis_coordinates(0)
    ys = case.grid.axis_coordinates(1)
    zs = case.grid.axis_coordinates(2)
    i = int(np.argmin(np.abs(xs)))
    k = int(np.argmin(np.abs(zs)))
    points = np.stack([np.full(ys.size, xs[i]), ys, np.full(ys.size, zs[k])], axis=1).astype(np.float32)
    _, _, distance = beam.project(points)
    return ys, np.asarray(distance, dtype=np.float64), volume[i, :, k].astype(np.float64)


class RadiologicalDepthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = water_case()
        self.beam = broad_beam(self.case)
        x, y, z = self.case.grid.meshgrid_world(dtype=np.float32)
        self.points = np.stack([x.reshape(-1), y.reshape(-1), z.reshape(-1)], axis=1)
        self.u, self.v, self.distance = self.beam.project(self.points)

    def _depth(self, density: np.ndarray) -> np.ndarray:
        return radiological_depth_field(
            self.beam, self.case.grid, density, self.u, self.v, self.distance, SETTINGS
        )

    def test_in_water_radiological_depth_equals_geometric_path(self) -> None:
        depth = self._depth(self.case.density()).reshape(self.case.grid.dimensions)
        ys = self.case.grid.axis_coordinates(1)
        centre = depth[depth.shape[0] // 2, :, depth.shape[2] // 2]
        # Compare increments so the entry-surface convention does not matter.
        for lower, upper in ((2, 6), (6, 12), (12, 20)):
            expected = float(ys[upper] - ys[lower])
            measured = float(centre[upper] - centre[lower])
            self.assertAlmostEqual(measured, expected, delta=0.75)

    def test_depth_increases_monotonically_along_the_beam(self) -> None:
        depth = self._depth(self.case.density()).reshape(self.case.grid.dimensions)
        centre = depth[depth.shape[0] // 2, :, depth.shape[2] // 2]
        self.assertTrue(np.all(np.diff(centre) >= -1e-3))

    def test_a_low_density_slab_shortens_downstream_depth(self) -> None:
        density = self.case.density().copy()
        ys = self.case.grid.axis_coordinates(1)
        slab = (ys >= -40.0) & (ys < 0.0)
        thickness = float(np.count_nonzero(slab) * self.case.grid.spacing[1])
        density[:, slab, :] = np.float32(0.25)

        water_depth = self._depth(self.case.density()).reshape(self.case.grid.dimensions)
        slab_depth = self._depth(density).reshape(self.case.grid.dimensions)
        downstream = ys > 20.0
        difference = (water_depth - slab_depth)[:, downstream, :]
        expected = (1.0 - 0.25) * thickness
        self.assertAlmostEqual(float(difference.mean()), expected, delta=0.15 * expected)


class DepthDoseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = water_case(dimensions=(48, 72, 12))
        self.beam = broad_beam(self.case)
        self.influence = compute_influence(self.case, [self.beam], SETTINGS)
        weights = np.ones(self.influence.n_bixels, dtype=np.float32)
        self.dose = self.influence.dose(weights)
        self.ys, self.distance, self.profile = central_axis_samples(self.case, self.beam, self.dose)

    def test_central_axis_follows_the_analytic_depth_dose(self) -> None:
        """After removing inverse-square, the profile must match (1-e^-bz) e^-uz."""
        entry = float(self.ys[0]) - 0.5 * self.case.grid.spacing[1]
        depth = self.ys - entry
        corrected = self.profile * (self.distance / self.beam.sad_mm) ** 2
        expected = SETTINGS.depth_dose(depth.astype(np.float32)).astype(np.float64)
        # Compare shapes, normalised past the build-up region.
        deep = depth > 40.0
        scale = float(corrected[deep].sum() / expected[deep].sum())
        relative = np.abs(corrected[deep] - scale * expected[deep]) / (scale * expected[deep])
        self.assertLess(float(relative.max()), 0.05)

    def test_build_up_peak_is_near_the_model_dmax(self) -> None:
        entry = float(self.ys[0]) - 0.5 * self.case.grid.spacing[1]
        depth = self.ys - entry
        corrected = self.profile * (self.distance / self.beam.sad_mm) ** 2
        peak_depth = float(depth[int(np.argmax(corrected))])
        self.assertLess(abs(peak_depth - SETTINGS.dmax_mm()), 1.5 * self.case.grid.spacing[1])

    def test_surface_dose_is_below_the_maximum(self) -> None:
        corrected = self.profile * (self.distance / self.beam.sad_mm) ** 2
        self.assertLess(corrected[0], 0.75 * corrected.max())

    def test_inverse_square_falloff_is_present(self) -> None:
        """With the depth dose flattened, the central axis must follow 1/r^2.

        The field is made much wider than the lateral spread so that Gaussian
        truncation at the field edge does not contaminate the central axis.
        """
        settings = PencilBeamSettings(mu_per_mm=0.0, buildup_per_mm=1e6)  # flat depth dose
        case = water_case(dimensions=(48, 24, 24), spacing=(8.0, 8.0, 8.0))
        beam = broad_beam(case, bixel_width_mm=20.0)
        influence = compute_influence(case, [beam], settings)
        dose = influence.dose(np.ones(influence.n_bixels, dtype=np.float32))
        _, distance, profile = central_axis_samples(case, beam, dose)
        interior = slice(3, -3)
        scaled = profile[interior] * distance[interior] ** 2
        spread = float(scaled.max() / scaled.min())
        self.assertLess(spread, 1.05)


class LateralSpreadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = water_case(dimensions=(64, 72, 12), spacing=(3.0, 4.0, 4.0))
        self.beam = broad_beam(self.case, bixel_width_mm=5.0)
        self.influence = compute_influence(self.case, [self.beam], SETTINGS)
        self.dose = self.influence.dose(
            np.ones(self.influence.n_bixels, dtype=np.float32)
        ).reshape(self.case.grid.dimensions)

    def _penumbra_width(self, row: np.ndarray, xs: np.ndarray) -> float:
        peak = float(row.max())
        high = xs[row >= 0.8 * peak]
        low = xs[row >= 0.2 * peak]
        return float((low.max() - low.min()) - (high.max() - high.min())) / 2.0

    def test_dose_falls_off_outside_the_field(self) -> None:
        xs = self.case.grid.axis_coordinates(0)
        row = self.dose[:, self.dose.shape[1] // 2, self.dose.shape[2] // 2]
        centre = float(row[np.argmin(np.abs(xs))])
        edge = float(row[0])
        self.assertLess(edge, 0.2 * centre)

    def test_penumbra_widens_with_depth(self) -> None:
        xs = self.case.grid.axis_coordinates(0)
        k = self.dose.shape[2] // 2
        shallow = self._penumbra_width(self.dose[:, 8, k], xs)
        deep = self._penumbra_width(self.dose[:, -8, k], xs)
        self.assertGreater(deep, shallow)


class InfluenceMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = water_case(dimensions=(32, 40, 8), spacing=(6.0, 6.0, 6.0))
        self.beam = broad_beam(self.case, bixel_width_mm=15.0)
        self.influence = compute_influence(self.case, [self.beam], SETTINGS)

    def test_dose_is_linear_in_the_weights(self) -> None:
        rng = np.random.default_rng(11)
        a = rng.random(self.influence.n_bixels).astype(np.float32)
        b = rng.random(self.influence.n_bixels).astype(np.float32)
        combined = self.influence.dose(2.0 * a + 3.0 * b)
        separate = 2.0 * self.influence.dose(a) + 3.0 * self.influence.dose(b)
        self.assertTrue(np.allclose(combined, separate, rtol=1e-4, atol=1e-6))

    def test_transpose_is_the_adjoint(self) -> None:
        rng = np.random.default_rng(12)
        weights = rng.random(self.influence.n_bixels).astype(np.float32)
        voxels = rng.random(self.influence.n_voxels).astype(np.float32)
        left = float(np.dot(self.influence.dose(weights), voxels))
        right = float(np.dot(weights, self.influence.transpose_dot(voxels)))
        self.assertAlmostEqual(left, right, delta=1e-3 * max(abs(left), 1.0))

    def test_nonnegative_weights_give_nonnegative_dose(self) -> None:
        rng = np.random.default_rng(13)
        dose = self.influence.dose(rng.random(self.influence.n_bixels).astype(np.float32))
        self.assertGreaterEqual(float(dose.min()), 0.0)

    def test_column_norms_match_a_direct_computation(self) -> None:
        norms = self.influence.column_norms()
        direct = np.zeros(self.influence.n_bixels)
        np.add.at(direct, self.influence.cols, self.influence.values.astype(np.float64) ** 2)
        self.assertTrue(np.allclose(norms, np.sqrt(direct), rtol=1e-5, atol=1e-6))

    def test_weight_length_is_checked(self) -> None:
        with self.assertRaises(ValueError):
            self.influence.dose(np.ones(3, dtype=np.float32))

    def test_entry_budget_is_enforced(self) -> None:
        with self.assertRaises(MemoryError):
            compute_influence(self.case, [self.beam], PencilBeamSettings(max_entries=100))


class KernelInvarianceTests(unittest.TestCase):
    """The bixel grid is a discretisation choice; the dose must not depend on it."""

    def test_dose_is_insensitive_to_bixel_width(self) -> None:
        case = water_case(dimensions=(48, 40, 16), spacing=(6.0, 6.0, 6.0))
        reference = None
        for width in (4.0, 8.0, 16.0, 24.0):
            beam = broad_beam(case, bixel_width_mm=width)
            influence = compute_influence(case, [beam], SETTINGS)
            dose = influence.dose(np.ones(influence.n_bixels, dtype=np.float32))
            _, _, profile = central_axis_samples(case, beam, dose)
            if reference is None:
                reference = profile
                continue
            live = reference > 0.1 * reference.max()
            deviation = float(np.abs(profile - reference)[live].max() / reference.max())
            self.assertLess(deviation, 0.03, msg=f"bixel width {width} mm deviates by {deviation:.2%}")


class GantryConsistencyTests(unittest.TestCase):
    def test_opposed_beams_mirror_each_other_in_a_symmetric_phantom(self) -> None:
        case = water_case(dimensions=(32, 32, 8), spacing=(6.0, 6.0, 6.0))
        settings = PencilBeamSettings()
        doses = []
        for angle in (0.0, 180.0):
            beam = broad_beam(case, gantry_deg=angle, bixel_width_mm=15.0)
            influence = compute_influence(case, [beam], settings)
            doses.append(
                influence.dose(np.ones(influence.n_bixels, dtype=np.float32)).reshape(case.grid.dimensions)
            )
        mirrored = doses[1][:, ::-1, :]
        peak = float(doses[0].max())
        self.assertLess(float(np.abs(doses[0] - mirrored).max()) / peak, 0.02)


if __name__ == "__main__":
    unittest.main()
