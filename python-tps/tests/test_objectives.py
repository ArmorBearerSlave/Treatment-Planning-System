from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.objectives import (
    MaxDose,
    MeanDose,
    MinDose,
    ObjectiveError,
    ObjectiveSet,
    TargetDose,
    objective_from_dict,
)


class ObjectiveShapeTests(unittest.TestCase):
    def test_target_dose_penalises_both_directions(self) -> None:
        objective = TargetDose("PTV", weight=1.0, dose_gy=60.0)
        cold = objective.evaluate(np.array([55.0], dtype=np.float32), 1)
        hot = objective.evaluate(np.array([65.0], dtype=np.float32), 1)
        self.assertAlmostEqual(cold, 25.0, places=3)
        self.assertAlmostEqual(hot, 25.0, places=3)

    def test_max_dose_ignores_dose_below_the_ceiling(self) -> None:
        objective = MaxDose("OAR", weight=1.0, dose_gy=40.0)
        self.assertEqual(objective.evaluate(np.array([10.0], dtype=np.float32), 1), 0.0)
        self.assertAlmostEqual(objective.evaluate(np.array([45.0], dtype=np.float32), 1), 25.0, places=3)

    def test_min_dose_ignores_dose_above_the_floor(self) -> None:
        objective = MinDose("PTV", weight=1.0, dose_gy=57.0)
        self.assertEqual(objective.evaluate(np.array([60.0], dtype=np.float32), 1), 0.0)
        self.assertAlmostEqual(objective.evaluate(np.array([52.0], dtype=np.float32), 1), 25.0, places=3)

    def test_mean_dose_uses_the_structure_average(self) -> None:
        objective = MeanDose("OAR", weight=1.0, dose_gy=20.0)
        dose = np.array([10.0, 40.0], dtype=np.float32)  # mean 25
        self.assertAlmostEqual(objective.evaluate(dose, 2), 25.0, places=3)

    def test_normalisation_makes_weights_comparable(self) -> None:
        objective = TargetDose("PTV", weight=1.0, dose_gy=0.0)
        small = objective.evaluate(np.full(10, 2.0, dtype=np.float32), 10)
        large = objective.evaluate(np.full(1000, 2.0, dtype=np.float32), 1000)
        self.assertAlmostEqual(small, large, places=4)

    def test_rejects_negative_weight_and_dose(self) -> None:
        with self.assertRaises(ObjectiveError):
            TargetDose("PTV", weight=-1.0, dose_gy=60.0)
        with self.assertRaises(ObjectiveError):
            TargetDose("PTV", weight=1.0, dose_gy=-60.0)


class GradientTests(unittest.TestCase):
    """Every gradient is checked against a central finite difference."""

    def _check(self, objective, dose: np.ndarray) -> None:
        count = dose.size
        analytic = objective.gradient(dose, count).astype(np.float64)
        step = 1e-3
        numeric = np.zeros_like(analytic)
        for index in range(count):
            up, down = dose.astype(np.float64).copy(), dose.astype(np.float64).copy()
            up[index] += step
            down[index] -= step
            numeric[index] = (
                objective.evaluate(up.astype(np.float32), count)
                - objective.evaluate(down.astype(np.float32), count)
            ) / (2.0 * step)
        self.assertTrue(
            np.allclose(analytic, numeric, rtol=2e-3, atol=2e-3),
            msg=f"{objective.kind()}: analytic {analytic} vs numeric {numeric}",
        )

    def test_target_dose_gradient(self) -> None:
        self._check(TargetDose("PTV", 3.0, 60.0), np.array([50.0, 60.0, 70.0], dtype=np.float32))

    def test_max_dose_gradient(self) -> None:
        self._check(MaxDose("OAR", 2.0, 40.0), np.array([10.0, 50.0, 80.0], dtype=np.float32))

    def test_min_dose_gradient(self) -> None:
        self._check(MinDose("PTV", 2.0, 57.0), np.array([40.0, 60.0, 57.0], dtype=np.float32))

    def test_mean_dose_gradient(self) -> None:
        self._check(MeanDose("OAR", 5.0, 20.0), np.array([10.0, 30.0, 40.0], dtype=np.float32))


class ObjectiveSetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.indices = {"PTV": np.array([0, 1]), "OAR": np.array([2, 3])}

    def test_value_and_gradient_agree_with_finite_differences(self) -> None:
        objectives = ObjectiveSet(
            [TargetDose("PTV", 10.0, 60.0), MaxDose("OAR", 4.0, 20.0)], self.indices
        )
        dose = np.array([58.0, 62.0, 25.0, 10.0], dtype=np.float32)
        value, gradient = objectives.value_and_gradient(dose)
        self.assertAlmostEqual(value, objectives.value(dose), places=5)
        step = 1e-3
        for index in range(dose.size):
            up, down = dose.copy(), dose.copy()
            up[index] += step
            down[index] -= step
            numeric = (objectives.value(up) - objectives.value(down)) / (2.0 * step)
            self.assertAlmostEqual(float(gradient[index]), float(numeric), delta=2e-2)

    def test_zero_weight_objectives_are_disabled_not_dropped(self) -> None:
        objectives = ObjectiveSet(
            [TargetDose("PTV", 10.0, 60.0), MaxDose("OAR", 0.0, 20.0)], self.indices
        )
        self.assertEqual(len(objectives.objectives), 1)
        self.assertEqual(len(objectives.disabled), 1)
        rows = objectives.breakdown(np.array([60.0, 60.0, 99.0, 99.0], dtype=np.float32))
        self.assertTrue(any(row.get("note", "").startswith("disabled") for row in rows))

    def test_rejects_all_zero_weights(self) -> None:
        with self.assertRaises(ObjectiveError):
            ObjectiveSet([TargetDose("PTV", 0.0, 60.0)], self.indices)

    def test_rejects_unbound_or_empty_structures(self) -> None:
        with self.assertRaises(ObjectiveError):
            ObjectiveSet([TargetDose("MISSING", 1.0, 60.0)], self.indices)
        with self.assertRaises(ObjectiveError):
            ObjectiveSet([TargetDose("PTV", 1.0, 60.0)], {"PTV": np.array([], dtype=np.int64)})

    def test_curvature_bound_dominates_the_true_curvature(self) -> None:
        objectives = ObjectiveSet(
            [TargetDose("PTV", 10.0, 60.0), MaxDose("PTV", 4.0, 20.0)], {"PTV": np.array([0, 1])}
        )
        # Both objectives are active on PTV, so the bound must include both.
        self.assertAlmostEqual(objectives.max_voxel_curvature(4), 2 * 10.0 / 2 + 2 * 4.0 / 2, places=6)


class ObjectiveSerialisationTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        original = MaxDose("RECTUM", 20.0, 39.0)
        restored = objective_from_dict(original.to_dict())
        self.assertEqual(restored, original)

    def test_unknown_type_is_reported_with_the_supported_list(self) -> None:
        with self.assertRaises(ObjectiveError) as caught:
            objective_from_dict({"type": "dvh_constraint", "structure": "A", "doseGy": 1, "weight": 1})
        self.assertIn("target_dose", str(caught.exception))

    def test_missing_field_is_reported(self) -> None:
        with self.assertRaises(ObjectiveError):
            objective_from_dict({"type": "max_dose", "structure": "A"})


if __name__ == "__main__":
    unittest.main()
