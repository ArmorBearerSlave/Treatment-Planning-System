from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.materials import DEFAULT_HU_TO_DENSITY, hu_to_density


class HounsfieldLookupTests(unittest.TestCase):
    def test_water_is_unit_density(self) -> None:
        self.assertAlmostEqual(float(hu_to_density(np.array([0.0]))[0]), 1.0, places=4)

    def test_air_is_near_zero(self) -> None:
        self.assertLess(float(hu_to_density(np.array([-1000.0]))[0]), 0.01)

    def test_monotone_non_decreasing(self) -> None:
        sampled = hu_to_density(np.linspace(-1200.0, 4000.0, 2000))
        self.assertTrue(np.all(np.diff(sampled) >= -1e-6))

    def test_clamped_outside_the_table(self) -> None:
        low = float(hu_to_density(np.array([-5000.0]))[0])
        high = float(hu_to_density(np.array([9000.0]))[0])
        self.assertAlmostEqual(low, DEFAULT_HU_TO_DENSITY[0][1], places=5)
        self.assertAlmostEqual(high, DEFAULT_HU_TO_DENSITY[-1][1], places=5)

    def test_rejects_non_monotone_table(self) -> None:
        with self.assertRaises(ValueError):
            hu_to_density(np.array([0.0]), table=((0.0, 1.0), (-10.0, 0.5)))


if __name__ == "__main__":
    unittest.main()
