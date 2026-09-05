from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.beams import BeamError, beam_axes, build_beams, build_bixel_grid


class BeamAxisTests(unittest.TestCase):
    def test_gantry_zero_is_anterior(self) -> None:
        axis, u_axis, v_axis = beam_axes(0.0)
        # LPS: +y is posterior, so an anterior source travels in +y.
        self.assertTrue(np.allclose(axis, [0.0, 1.0, 0.0], atol=1e-9))
        self.assertTrue(np.allclose(u_axis, [1.0, 0.0, 0.0], atol=1e-9))
        self.assertTrue(np.allclose(v_axis, [0.0, 0.0, 1.0], atol=1e-9))

    def test_gantry_ninety_is_patient_left(self) -> None:
        axis, _, _ = beam_axes(90.0)
        self.assertTrue(np.allclose(axis, [-1.0, 0.0, 0.0], atol=1e-9))

    def test_axes_are_orthonormal(self) -> None:
        for angle in (0.0, 37.5, 90.0, 200.0, 359.0):
            axis, u_axis, v_axis = beam_axes(angle)
            for vector in (axis, u_axis, v_axis):
                self.assertAlmostEqual(float(np.linalg.norm(vector)), 1.0, places=12)
            self.assertAlmostEqual(float(axis @ u_axis), 0.0, places=12)
            self.assertAlmostEqual(float(axis @ v_axis), 0.0, places=12)
            self.assertAlmostEqual(float(u_axis @ v_axis), 0.0, places=12)


class BeamProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        points = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        self.beam = build_beams([0.0], [0.0, 0.0, 0.0], points, 5.0, 10.0)[0]

    def test_source_sits_at_sad_from_isocentre(self) -> None:
        self.assertAlmostEqual(float(np.linalg.norm(self.beam.source)), self.beam.sad_mm, places=6)
        self.assertTrue(np.allclose(self.beam.source, [0.0, -1000.0, 0.0], atol=1e-6))

    def test_isocentre_projects_to_the_origin_at_sad(self) -> None:
        u, v, distance = self.beam.project(np.array([[0.0, 0.0, 0.0]], dtype=np.float32))
        self.assertAlmostEqual(float(u[0]), 0.0, places=4)
        self.assertAlmostEqual(float(v[0]), 0.0, places=4)
        self.assertAlmostEqual(float(distance[0]), 1000.0, places=3)

    def test_divergence_scales_lateral_offset_back_to_isocentre(self) -> None:
        # A point at half the source-axis distance, offset 5 mm laterally,
        # projects to 10 mm in the isocentre plane.
        point = np.array([[5.0, -500.0, 0.0]], dtype=np.float32)
        u, _, distance = self.beam.project(point)
        self.assertAlmostEqual(float(distance[0]), 500.0, places=3)
        self.assertAlmostEqual(float(u[0]), 10.0, places=3)

    def test_points_behind_the_source_stay_finite(self) -> None:
        u, v, distance = self.beam.project(np.array([[0.0, -2000.0, 0.0]], dtype=np.float32))
        self.assertTrue(np.all(np.isfinite(u)) and np.all(np.isfinite(v)))
        self.assertGreater(float(distance[0]), 0.0)


class BixelGridTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(3)
        self.points = rng.uniform(-20.0, 20.0, size=(400, 3)).astype(np.float32)

    def test_grid_covers_the_target_projection_plus_margin(self) -> None:
        beam = build_bixel_grid(0, 0.0, [0, 0, 0], self.points, bixel_width_mm=5.0, margin_mm=10.0)
        u, v, _ = beam.project(self.points)
        u_centers, v_centers = beam.bixels.u_centers(), beam.bixels.v_centers()
        self.assertLessEqual(u_centers[0], float(u.min()) - 10.0 + 5.0)
        self.assertGreaterEqual(u_centers[-1], float(u.max()) + 10.0 - 5.0)
        self.assertLessEqual(v_centers[0], float(v.min()) - 10.0 + 5.0)
        self.assertGreaterEqual(v_centers[-1], float(v.max()) + 10.0 - 5.0)

    def test_a_wider_margin_never_shrinks_the_field(self) -> None:
        narrow = build_bixel_grid(0, 0.0, [0, 0, 0], self.points, 5.0, 0.0).bixels
        wide = build_bixel_grid(0, 0.0, [0, 0, 0], self.points, 5.0, 20.0).bixels
        self.assertGreaterEqual(wide.n_u, narrow.n_u)
        self.assertGreaterEqual(wide.n_v, narrow.n_v)

    def test_rejects_out_of_range_bixel_width(self) -> None:
        for width in (0.5, 100.0):
            with self.assertRaises(BeamError):
                build_bixel_grid(0, 0.0, [0, 0, 0], self.points, width, 10.0)

    def test_rejects_duplicate_and_missing_angles(self) -> None:
        with self.assertRaises(BeamError):
            build_beams([0.0, 360.0], [0, 0, 0], self.points, 5.0, 10.0)
        with self.assertRaises(BeamError):
            build_beams([], [0, 0, 0], self.points, 5.0, 10.0)

    def test_rejects_too_many_beams(self) -> None:
        with self.assertRaises(BeamError):
            build_beams(list(range(0, 360, 20)), [0, 0, 0], self.points, 5.0, 10.0)

    def test_rejects_empty_target(self) -> None:
        with self.assertRaises(BeamError):
            build_bixel_grid(0, 0.0, [0, 0, 0], np.zeros((0, 3), dtype=np.float32), 5.0, 10.0)


if __name__ == "__main__":
    unittest.main()
