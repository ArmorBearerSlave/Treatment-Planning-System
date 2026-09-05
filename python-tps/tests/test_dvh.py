from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.dvh import compute_dvh, compute_dvh_set


class UniformDoseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dose = np.full(1000, 60.0, dtype=np.float32)
        self.dvh = compute_dvh(
            self.dose, np.arange(1000), "PTV", voxel_volume_cm3=0.001, reference_dose_gy=60.0
        )

    def test_scalar_metrics(self) -> None:
        for key in ("meanGy", "minGy", "maxGy", "D50Gy", "D95Gy", "D98Gy", "D2Gy"):
            self.assertAlmostEqual(self.dvh.metrics[key], 60.0, delta=0.15, msg=key)

    def test_volume_is_voxel_counted(self) -> None:
        self.assertAlmostEqual(self.dvh.volume_cm3, 1.0, places=6)

    def test_full_coverage_at_the_prescription(self) -> None:
        self.assertAlmostEqual(self.dvh.metrics["V95pct"], 1.0, places=3)

    def test_uniform_dose_is_perfectly_homogeneous(self) -> None:
        self.assertLess(self.dvh.metrics["homogeneityIndex"], 0.01)


class RampDoseTests(unittest.TestCase):
    """A linear ramp from 0 to 100 Gy has analytically known Dx and Vx."""

    def setUp(self) -> None:
        self.dose = np.linspace(0.0, 100.0, 10001, dtype=np.float32)
        self.dvh = compute_dvh(
            self.dose,
            np.arange(self.dose.size),
            "RAMP",
            voxel_volume_cm3=1.0,
            bins=4096,
            reference_dose_gy=100.0,
        )

    def test_dx_matches_the_analytic_quantiles(self) -> None:
        for fraction, expected in ((0.02, 98.0), (0.50, 50.0), (0.95, 5.0), (0.98, 2.0)):
            self.assertAlmostEqual(
                self.dvh.dose_at_volume_fraction(fraction), expected, delta=0.4, msg=str(fraction)
            )

    def test_vx_matches_the_analytic_fractions(self) -> None:
        for dose_gy, expected in ((0.0, 1.0), (25.0, 0.75), (50.0, 0.50), (90.0, 0.10)):
            self.assertAlmostEqual(
                self.dvh.volume_fraction_at_dose(dose_gy), expected, delta=0.01, msg=str(dose_gy)
            )

    def test_curve_is_monotonically_non_increasing(self) -> None:
        self.assertTrue(np.all(np.diff(self.dvh.volume_fraction) <= 1e-9))

    def test_curve_starts_at_full_volume(self) -> None:
        self.assertAlmostEqual(float(self.dvh.volume_fraction[0]), 1.0, places=6)


class DvhSetTests(unittest.TestCase):
    def test_structures_share_one_dose_scale(self) -> None:
        dose = np.concatenate([np.full(100, 60.0), np.full(100, 10.0)]).astype(np.float32)
        dvhs = compute_dvh_set(
            dose,
            {"PTV": np.arange(100), "OAR": np.arange(100, 200)},
            voxel_volume_cm3=0.1,
            reference_dose_gy=60.0,
            targets=("PTV",),
        )
        self.assertTrue(np.allclose(dvhs["PTV"].dose_bins_gy, dvhs["OAR"].dose_bins_gy))
        self.assertAlmostEqual(dvhs["OAR"].metrics["meanGy"], 10.0, delta=0.1)
        # Reference-relative metrics only make sense for a target.
        self.assertIn("V95pct", dvhs["PTV"].metrics)
        self.assertNotIn("V95pct", dvhs["OAR"].metrics)

    def test_serialisation_includes_a_downsampled_curve(self) -> None:
        dose = np.linspace(0.0, 50.0, 500, dtype=np.float32)
        dvh = compute_dvh(dose, np.arange(500), "S", 0.5, bins=512)
        payload = dvh.to_dict(curve_points=32)
        self.assertLessEqual(len(payload["curve"]["doseGy"]), 40)
        self.assertEqual(len(payload["curve"]["doseGy"]), len(payload["curve"]["volumeFraction"]))
        self.assertEqual(payload["structure"], "S")


class DvhValidationTests(unittest.TestCase):
    def test_rejects_an_empty_structure(self) -> None:
        with self.assertRaises(ValueError):
            compute_dvh(np.zeros(10, dtype=np.float32), np.array([], dtype=np.int64), "E", 1.0)

    def test_rejects_too_few_bins(self) -> None:
        with self.assertRaises(ValueError):
            compute_dvh(np.zeros(10, dtype=np.float32), np.arange(10), "S", 1.0, bins=1)

    def test_rejects_an_out_of_range_volume_fraction(self) -> None:
        dvh = compute_dvh(np.ones(10, dtype=np.float32), np.arange(10), "S", 1.0)
        with self.assertRaises(ValueError):
            dvh.dose_at_volume_fraction(1.5)


if __name__ == "__main__":
    unittest.main()
