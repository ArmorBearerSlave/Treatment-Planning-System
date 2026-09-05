from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.special import ERF_MAX_ABS_ERROR, erf, gaussian_bar_integral


class ErrorFunctionTests(unittest.TestCase):
    def test_matches_the_standard_library(self) -> None:
        sample = np.linspace(-5.0, 5.0, 4001)
        reference = np.array([math.erf(float(value)) for value in sample])
        self.assertLess(float(np.abs(erf(sample) - reference).max()), ERF_MAX_ABS_ERROR)

    def test_is_odd_and_bounded(self) -> None:
        sample = np.linspace(0.0, 6.0, 501)
        self.assertLess(float(np.abs(erf(sample) + erf(-sample)).max()), ERF_MAX_ABS_ERROR)
        self.assertLessEqual(float(np.abs(erf(sample)).max()), 1.0 + ERF_MAX_ABS_ERROR)

    def test_known_values(self) -> None:
        self.assertAlmostEqual(float(erf(np.array([0.0]))[0]), 0.0, places=6)
        self.assertAlmostEqual(float(erf(np.array([10.0]))[0]), 1.0, places=6)


class GaussianBarIntegralTests(unittest.TestCase):
    def test_adjacent_bars_partition_unity(self) -> None:
        """The whole point of the integrated form: bar width must not matter."""
        sigma = np.float32(4.0)
        for width in (1.0, 4.0, 12.0, 25.0):
            centres = np.arange(-200.0, 200.0 + width, width, dtype=np.float32)
            for point in (0.0, 0.37 * width, 0.5 * width):
                delta = np.float32(point) - centres
                total = float(gaussian_bar_integral(delta, np.full(centres.shape, sigma), width).sum())
                self.assertAlmostEqual(total, 1.0, places=4, msg=f"width {width}, offset {point}")

    def test_matches_a_numerical_integral(self) -> None:
        sigma, width, delta = 3.0, 7.0, 2.0
        grid = np.linspace(delta - width / 2.0, delta + width / 2.0, 20001)
        density = np.exp(-0.5 * (grid / sigma) ** 2) / (sigma * math.sqrt(2.0 * math.pi))
        expected = float(np.trapezoid(density, grid))
        measured = float(gaussian_bar_integral(np.array([delta]), np.array([sigma]), width)[0])
        self.assertAlmostEqual(measured, expected, places=5)

    def test_never_exceeds_one(self) -> None:
        deltas = np.linspace(-50.0, 50.0, 1001)
        values = gaussian_bar_integral(deltas, np.full(deltas.shape, 0.5), 30.0)
        self.assertLessEqual(float(values.max()), 1.0 + 1e-5)
        self.assertGreaterEqual(float(values.min()), 0.0)


if __name__ == "__main__":
    unittest.main()
