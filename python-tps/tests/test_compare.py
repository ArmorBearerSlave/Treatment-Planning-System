"""Dose comparison: DVH deltas, difference statistics, and the gamma index."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.compare import (
    ComparisonError,
    compare_doses,
    gamma_index,
    normalize_to_isocenter,
)
from pytps.geometry import Grid
from pytps.objectives import MaxDose, TargetDose
from pytps.phantom import build_phantom_case
from pytps.plan import PlanRequest

SMALL = {"dimensions": (24, 20, 16), "spacing": (6.0, 6.0, 6.0), "noise_hu": 0.0}


def smooth_field(grid: Grid, peak: float = 60.0) -> np.ndarray:
    """A smooth blob, so a spatial shift changes the dose gradually."""
    x, y, z = grid.meshgrid_world(dtype=np.float32)
    radius = np.sqrt(x**2 + y**2 + z**2)
    return (peak * np.exp(-((radius / 30.0) ** 2))).astype(np.float32)


class GammaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = Grid((32, 32, 16), (2.0, 2.0, 2.0), (-31.0, -31.0, -15.0))
        self.reference = smooth_field(self.grid)

    def test_identical_doses_pass_everywhere(self) -> None:
        result = gamma_index(self.grid, self.reference, self.reference)
        self.assertAlmostEqual(result.pass_rate, 1.0, places=9)
        self.assertLess(result.mean_gamma, 1e-6)

    def test_a_difference_inside_the_dose_criterion_passes(self) -> None:
        offset = 0.02 * float(self.reference.max())
        result = gamma_index(self.grid, self.reference, self.reference + offset, dose_percent=3.0)
        self.assertAlmostEqual(result.pass_rate, 1.0, places=6)

    def test_a_uniform_offset_beyond_the_criterion_fails_everywhere(self) -> None:
        offset = 0.10 * float(self.reference.max())
        result = gamma_index(self.grid, self.reference, self.reference + offset, dose_percent=3.0)
        self.assertEqual(result.pass_rate, 0.0)
        # The distance term rescues part of the offset wherever the reference
        # has a gradient, so the mean sits below the 10/3 a flat field would
        # give, but every voxel still fails.
        self.assertGreater(result.mean_gamma, 1.0)
        self.assertLess(result.mean_gamma, 10.0 / 3.0 + 1e-6)

    def test_a_small_shift_is_rescued_by_the_distance_criterion(self) -> None:
        shifted = np.roll(self.reference, 1, axis=0)  # one 2 mm voxel
        forgiving = gamma_index(self.grid, self.reference, shifted, dose_percent=1.0, distance_mm=3.0)
        strict = gamma_index(self.grid, self.reference, shifted, dose_percent=1.0, distance_mm=0.5)
        self.assertGreater(forgiving.pass_rate, strict.pass_rate)
        # np.roll wraps at the grid edge, so a thin boundary layer legitimately
        # fails; everything else is rescued by the distance term.
        self.assertGreater(forgiving.pass_rate, 0.95)

    def test_the_threshold_excludes_low_dose_voxels(self) -> None:
        low = gamma_index(self.grid, self.reference, self.reference, threshold_percent=1.0)
        high = gamma_index(self.grid, self.reference, self.reference, threshold_percent=50.0)
        self.assertGreater(low.evaluated_voxels, high.evaluated_voxels)

    def test_the_search_lattice_covers_the_distance_sphere(self) -> None:
        result = gamma_index(self.grid, self.reference, self.reference, distance_mm=3.0, step_mm=1.0)
        self.assertEqual(result.offsets, 123)
        self.assertEqual(result.search_step_mm, 1.0)

    def test_invalid_criteria_are_rejected(self) -> None:
        for kwargs in (
            {"dose_percent": 0.0},
            {"distance_mm": 0.0},
            {"threshold_percent": 100.0},
            {"step_mm": 0.0},
        ):
            with self.assertRaises(ComparisonError, msg=str(kwargs)):
                gamma_index(self.grid, self.reference, self.reference, **kwargs)

    def test_an_empty_reference_is_rejected(self) -> None:
        with self.assertRaises(ComparisonError):
            gamma_index(self.grid, np.zeros(self.grid.dimensions, np.float32), self.reference)

    def test_an_oversized_search_lattice_is_refused_before_it_is_allocated(self) -> None:
        with self.assertRaises(ComparisonError) as caught:
            gamma_index(self.grid, self.reference, self.reference, distance_mm=50.0, step_mm=0.05)
        self.assertIn("lattice", str(caught.exception))


class NormalisationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = Grid((16, 16, 8), (4.0, 4.0, 4.0), (-30.0, -30.0, -14.0))

    def test_the_isocentre_becomes_unity(self) -> None:
        dose = np.full(self.grid.dimensions, 7.0, dtype=np.float32)
        normalized = normalize_to_isocenter(self.grid, dose, (0.0, 0.0, 0.0), radius_mm=10.0)
        self.assertAlmostEqual(float(normalized.mean()), 1.0, places=5)

    def test_two_scales_of_one_distribution_normalise_together(self) -> None:
        dose = smooth_field(self.grid)
        first = normalize_to_isocenter(self.grid, dose, (0.0, 0.0, 0.0))
        second = normalize_to_isocenter(self.grid, dose * 137.0, (0.0, 0.0, 0.0))
        self.assertTrue(np.allclose(first, second, rtol=1e-5))

    def test_a_zero_dose_at_the_isocentre_is_reported(self) -> None:
        with self.assertRaises(ComparisonError):
            normalize_to_isocenter(
                self.grid, np.zeros(self.grid.dimensions, np.float32), (0.0, 0.0, 0.0)
            )

    def test_an_isocentre_outside_the_grid_is_reported(self) -> None:
        dose = np.ones(self.grid.dimensions, dtype=np.float32)
        with self.assertRaises(ComparisonError) as caught:
            normalize_to_isocenter(self.grid, dose, (5000.0, 0.0, 0.0), radius_mm=1.0)
        self.assertIn("isocentre", str(caught.exception))


class CompareDosesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = build_phantom_case(**SMALL)
        self.request = PlanRequest(
            target="PROSTATE",
            prescription_gy=60.0,
            fractions=20,
            objectives=(TargetDose("PROSTATE", 100.0, 60.0), MaxDose("RECTUM", 20.0, 39.0)),
        )
        self.reference = np.zeros(self.case.grid.dimensions, dtype=np.float32)
        self.reference[self.case.labels != 0] = 10.0
        self.reference[self.case.mask("PROSTATE")] = 60.0

    def test_identical_doses_show_no_difference(self) -> None:
        comparison = compare_doses(
            self.case, self.reference, self.reference, request=self.request, gamma_criteria=None
        )
        structure, metric, value = comparison.worst_structure_difference_gy()
        self.assertAlmostEqual(value, 0.0, places=6)
        self.assertAlmostEqual(comparison.difference["maxAbsoluteGy"], 0.0, places=6)

    def test_structure_metrics_track_a_real_change(self) -> None:
        evaluation = self.reference.copy()
        evaluation[self.case.mask("PROSTATE")] = 54.0
        comparison = compare_doses(
            self.case, self.reference, evaluation, request=self.request, gamma_criteria=None
        )
        row = comparison.structures["PROSTATE"]["meanGy"]
        self.assertAlmostEqual(row["reference"], 60.0, places=3)
        self.assertAlmostEqual(row["evaluation"], 54.0, places=3)
        self.assertAlmostEqual(row["difference"], -6.0, places=3)
        self.assertAlmostEqual(comparison.structures["BLADDER"]["meanGy"]["difference"], 0.0, places=6)

    def test_target_coverage_is_compared_when_a_request_is_given(self) -> None:
        evaluation = self.reference.copy()
        evaluation[self.case.mask("PROSTATE")] = 40.0
        comparison = compare_doses(
            self.case, self.reference, evaluation, request=self.request, gamma_criteria=None
        )
        coverage = comparison.structures["PROSTATE"]["V95pct"]
        self.assertAlmostEqual(coverage["reference"], 1.0, places=6)
        self.assertAlmostEqual(coverage["evaluation"], 0.0, places=6)

    def test_the_shared_objective_is_evaluated_on_both_doses(self) -> None:
        """The objective is a function of dose, so it ranks the two plans."""
        worse = self.reference.copy()
        worse[self.case.mask("PROSTATE")] = 40.0
        comparison = compare_doses(
            self.case,
            self.reference,
            worse,
            reference_label="good",
            evaluation_label="cold",
            request=self.request,
            gamma_criteria=None,
        )
        self.assertIsNotNone(comparison.objective_values)
        self.assertLess(comparison.objective_values["good"], comparison.objective_values["cold"])

    def test_comparing_plans_warns_that_optimisers_are_confounded(self) -> None:
        comparison = compare_doses(
            self.case, self.reference, self.reference, gamma_criteria=None, kind="plans"
        )
        self.assertTrue(any("independently optimised" in item for item in comparison.warnings))

    def test_comparing_engines_carries_no_such_warning(self) -> None:
        comparison = compare_doses(
            self.case, self.reference, self.reference, gamma_criteria=None, kind="engines"
        )
        self.assertFalse(any("independently optimised" in item for item in comparison.warnings))
        self.assertEqual(comparison.to_dict()["doseUnits"], "normalised to the isocentre")

    def test_an_unknown_kind_is_rejected(self) -> None:
        with self.assertRaises(ComparisonError):
            compare_doses(self.case, self.reference, self.reference, kind="vibes")

    def test_mismatched_voxel_counts_are_rejected(self) -> None:
        with self.assertRaises(ComparisonError):
            compare_doses(self.case, self.reference, np.zeros(10, dtype=np.float32))

    def test_voxels_coarser_than_the_distance_criterion_are_flagged(self) -> None:
        """6 mm voxels against a 3 mm criterion: the distance term is interpolated."""
        comparison = compare_doses(
            self.case, self.reference, self.reference, gamma_criteria=(3.0, 3.0)
        )
        self.assertTrue(any("indicative" in item for item in comparison.warnings))

    def test_voxels_finer_than_the_criterion_are_not_flagged(self) -> None:
        comparison = compare_doses(
            self.case, self.reference, self.reference, gamma_criteria=(3.0, 10.0)
        )
        self.assertFalse(any("indicative" in item for item in comparison.warnings))

    def test_the_serialised_form_states_what_it_does_not_establish(self) -> None:
        payload = compare_doses(
            self.case, self.reference, self.reference, gamma_criteria=None
        ).to_dict()
        self.assertIn("not evidence of accuracy", payload["note"])


if __name__ == "__main__":
    unittest.main()
