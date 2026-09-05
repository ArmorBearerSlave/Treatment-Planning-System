from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.dose import DoseInfluence, PencilBeamSettings
from pytps.objectives import MaxDose, ObjectiveSet, TargetDose
from pytps.optimize import OptimizerSettings, optimize_fluence, preconditioner


def influence_from_dense(matrix: np.ndarray) -> DoseInfluence:
    """Wrap a dense test matrix in the sparse influence container."""
    rows, cols = np.nonzero(matrix)
    return DoseInfluence(
        rows=rows,
        cols=cols,
        values=matrix[rows, cols],
        n_voxels=matrix.shape[0],
        n_bixels=matrix.shape[1],
        beams=[],
        bixel_offsets=[],
        settings=PencilBeamSettings(),
    )


class SolverTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(5)
        # 40 voxels: 0-9 target, 10-39 organ. Column scales differ by 100x so
        # the problem is genuinely ill-conditioned without preconditioning.
        matrix = rng.random((40, 12)).astype(np.float32) * 0.2
        matrix[:10, :6] += 1.0
        matrix[10:, 6:] += 1.0
        matrix *= np.linspace(0.01, 1.0, 12, dtype=np.float32)
        self.influence = influence_from_dense(matrix)
        self.objectives = ObjectiveSet(
            [TargetDose("PTV", 100.0, 60.0), MaxDose("OAR", 10.0, 20.0)],
            {"PTV": np.arange(10), "OAR": np.arange(10, 40)},
        )

    def test_converges_and_respects_nonnegativity(self) -> None:
        result = optimize_fluence(self.influence, self.objectives, 60.0)
        self.assertTrue(result.converged, msg=result.reason)
        self.assertGreaterEqual(float(result.weights.min()), 0.0)
        self.assertLess(result.objective, result.history[0])

    def test_objective_decreases_monotonically(self) -> None:
        result = optimize_fluence(self.influence, self.objectives, 60.0)
        history = np.asarray(result.history)
        self.assertTrue(np.all(np.diff(history) <= 1e-6 * np.abs(history[:-1]) + 1e-9))

    def test_preconditioning_makes_an_ill_conditioned_problem_tractable(self) -> None:
        """Both solve the same convex problem, so neither may end up worse.

        On this deliberately badly scaled matrix the unpreconditioned solver
        stalls far from the optimum within the same iteration budget.
        """
        budget = OptimizerSettings(max_iterations=6000, tolerance=1e-9, patience=20)
        plain = optimize_fluence(
            self.influence,
            self.objectives,
            60.0,
            OptimizerSettings(**{**budget.__dict__, "precondition": False}),
        )
        scaled = optimize_fluence(self.influence, self.objectives, 60.0, budget)
        self.assertLessEqual(scaled.objective, plain.objective + 1e-6)
        self.assertLess(scaled.objective, 0.1 * plain.objective)

    def test_reported_dose_matches_the_reported_weights(self) -> None:
        result = optimize_fluence(self.influence, self.objectives, 60.0)
        self.assertTrue(np.allclose(result.dose, self.influence.dose(result.weights), atol=1e-4))

    def test_result_is_deterministic(self) -> None:
        first = optimize_fluence(self.influence, self.objectives, 60.0)
        second = optimize_fluence(self.influence, self.objectives, 60.0)
        self.assertTrue(np.array_equal(first.weights, second.weights))
        self.assertEqual(first.iterations, second.iterations)

    def test_iteration_limit_is_reported_as_not_converged(self) -> None:
        result = optimize_fluence(
            self.influence, self.objectives, 60.0, OptimizerSettings(max_iterations=2)
        )
        self.assertFalse(result.converged)
        self.assertEqual(result.iterations, 2)
        self.assertIn("iteration limit", result.reason)


class ExactRecoveryTests(unittest.TestCase):
    """With an attainable target the optimiser must actually attain it."""

    def test_identity_problem_reaches_the_prescription(self) -> None:
        influence = influence_from_dense(np.eye(8, dtype=np.float32))
        objectives = ObjectiveSet([TargetDose("PTV", 1.0, 42.0)], {"PTV": np.arange(8)})
        result = optimize_fluence(influence, objectives, 42.0, OptimizerSettings(tolerance=1e-12))
        self.assertTrue(np.allclose(result.dose, 42.0, atol=1e-2))
        self.assertLess(result.objective, 1e-3)

    def test_a_bixel_that_cannot_help_is_driven_to_zero(self) -> None:
        # Bixel 1 only irradiates the organ, which has a hard ceiling of zero.
        matrix = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        influence = influence_from_dense(matrix)
        objectives = ObjectiveSet(
            [TargetDose("PTV", 1.0, 10.0), MaxDose("OAR", 100.0, 0.0)],
            {"PTV": np.array([0]), "OAR": np.array([1])},
        )
        result = optimize_fluence(influence, objectives, 10.0, OptimizerSettings(tolerance=1e-12))
        self.assertAlmostEqual(float(result.weights[1]), 0.0, places=4)
        self.assertAlmostEqual(float(result.dose[0]), 10.0, delta=0.05)


class PreconditionerTests(unittest.TestCase):
    def test_scaling_equalises_column_norms(self) -> None:
        matrix = np.diag(np.array([0.01, 1.0, 100.0], dtype=np.float32))
        influence = influence_from_dense(matrix)
        scale = preconditioner(influence, enabled=True)
        scaled_norms = influence.column_norms() * scale
        self.assertTrue(np.allclose(scaled_norms, scaled_norms[0], rtol=1e-5))

    def test_disabled_preconditioner_is_the_identity(self) -> None:
        influence = influence_from_dense(np.eye(3, dtype=np.float32))
        self.assertTrue(np.array_equal(preconditioner(influence, enabled=False), np.ones(3, dtype=np.float32)))

    def test_empty_columns_do_not_divide_by_zero(self) -> None:
        matrix = np.zeros((3, 3), dtype=np.float32)
        matrix[0, 0] = 1.0
        influence = influence_from_dense(matrix)
        scale = preconditioner(influence, enabled=True)
        self.assertTrue(np.all(np.isfinite(scale)))
        self.assertTrue(np.all(scale > 0.0))


class SettingsValidationTests(unittest.TestCase):
    def test_rejects_invalid_settings(self) -> None:
        for kwargs in (
            {"max_iterations": 0},
            {"max_backtracks": 0},
            {"backtrack": 1.0},
            {"tolerance": -1.0},
            {"patience": 0},
            {"step_growth": 0.5},
        ):
            with self.assertRaises(ValueError, msg=str(kwargs)):
                OptimizerSettings(**kwargs)


if __name__ == "__main__":
    unittest.main()
