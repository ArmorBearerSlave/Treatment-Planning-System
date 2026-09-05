from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.geometry import Grid, GeometryError, trilinear_sample


class GridValidationTests(unittest.TestCase):
    def test_rejects_oblique_direction(self) -> None:
        with self.assertRaises(GeometryError) as caught:
            Grid((4, 4, 4), (1, 1, 1), (0, 0, 0), direction=(0.7, 0.7, 0, -0.7, 0.7, 0, 0, 0, 1))
        self.assertIn("oblique", str(caught.exception))

    def test_rejects_nonpositive_spacing(self) -> None:
        with self.assertRaises(GeometryError):
            Grid((4, 4, 4), (1.0, 0.0, 1.0), (0, 0, 0))

    def test_rejects_empty_dimension(self) -> None:
        with self.assertRaises(GeometryError):
            Grid((4, 0, 4), (1, 1, 1), (0, 0, 0))

    def test_mismatched_geometry_is_reported(self) -> None:
        a = Grid((4, 4, 4), (1, 1, 1), (0, 0, 0))
        b = Grid((4, 4, 4), (1, 1, 2), (0, 0, 0))
        with self.assertRaises(GeometryError):
            a.check_same_geometry(b, "a vs b")


class GridLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = Grid((4, 3, 2), (1.0, 2.0, 3.0), (-10.0, 5.0, 0.0))

    def test_flat_layout_is_x_fastest(self) -> None:
        flat = np.arange(self.grid.voxel_count, dtype=np.float32)
        array = self.grid.from_flat(flat)
        self.assertEqual(array.shape, (4, 3, 2))
        self.assertEqual(array[1, 0, 0], 1.0)   # one step in x
        self.assertEqual(array[0, 1, 0], 4.0)   # one step in y is nx
        self.assertEqual(array[0, 0, 1], 12.0)  # one step in z is nx*ny

    def test_flat_round_trip(self) -> None:
        flat = np.arange(self.grid.voxel_count, dtype=np.float32)
        self.assertTrue(np.array_equal(self.grid.to_flat(self.grid.from_flat(flat)), flat))

    def test_flat_length_is_checked(self) -> None:
        with self.assertRaises(GeometryError):
            self.grid.from_flat(np.zeros(5, dtype=np.float32))

    def test_axis_coordinates_and_world_round_trip(self) -> None:
        self.assertTrue(np.allclose(self.grid.axis_coordinates(1), [5.0, 7.0, 9.0]))
        indices = np.array([[1.0, 2.0, 0.5]])
        world = self.grid.index_to_world(indices)
        self.assertTrue(np.allclose(world, [[-9.0, 9.0, 1.5]]))
        self.assertTrue(np.allclose(self.grid.world_to_index(world), indices))

    def test_voxel_volume(self) -> None:
        self.assertAlmostEqual(self.grid.voxel_volume_mm3, 6.0)
        self.assertAlmostEqual(self.grid.voxel_volume_cm3, 0.006)

    def test_serialisation_round_trip(self) -> None:
        restored = Grid.from_dict(self.grid.to_dict())
        self.assertEqual(restored, self.grid)


class TrilinearSampleTests(unittest.TestCase):
    def test_exact_at_voxel_centres(self) -> None:
        volume = np.arange(2 * 3 * 4, dtype=np.float32).reshape(2, 3, 4)
        i, j, k = np.meshgrid(np.arange(2), np.arange(3), np.arange(4), indexing="ij")
        sampled = trilinear_sample(volume, (i, j, k))
        self.assertTrue(np.allclose(sampled, volume))

    def test_linear_interpolation_midpoint(self) -> None:
        volume = np.zeros((2, 1, 1), dtype=np.float32)
        volume[0, 0, 0], volume[1, 0, 0] = 0.0, 10.0
        value = trilinear_sample(volume, (np.array([0.25]), np.array([0.0]), np.array([0.0])))
        self.assertAlmostEqual(float(value[0]), 2.5, places=5)

    def test_outside_the_lattice_returns_fill(self) -> None:
        volume = np.ones((2, 2, 2), dtype=np.float32)
        value = trilinear_sample(volume, (np.array([-3.0]), np.array([0.0]), np.array([0.0])), fill=-1.0)
        self.assertAlmostEqual(float(value[0]), -1.0)


if __name__ == "__main__":
    unittest.main()
