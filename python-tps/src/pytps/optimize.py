"""Fluence optimisation.

The problem is

    minimise   F(w) = sum_c f_c( D w )      subject to   w >= 0

with ``f_c`` the quadratic penalties in :mod:`pytps.objectives` and ``D`` the
sparse dose-influence matrix. It is convex, so a projected accelerated
first-order method converges to a global minimum of *this* objective. That is
a numerical statement only: it says nothing about whether the resulting dose
distribution is clinically sensible.

The solver is FISTA with adaptive restart and a backtracking line search, so it
needs only matrix-vector products and therefore no scipy dependency.

Preconditioning
---------------
Bixels at the edge of a field deposit far less dose than central ones, so the
raw problem is badly scaled and plain FISTA crawls. The solver therefore works
in scaled variables ``w = S v`` with ``S = diag(1 / ||D[:, b]||)``. Because
``S`` is positive and diagonal, ``w >= 0`` and ``v >= 0`` are the same
constraint, so the projection is unchanged and the solution is identical - only
the path to it is shorter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from .dose import DoseInfluence
from .objectives import ObjectiveSet


@dataclass(frozen=True)
class OptimizerSettings:
    max_iterations: int = 2000
    #: Stop when the relative objective decrease stays below this for `patience` steps.
    tolerance: float = 1e-6
    patience: int = 8
    #: Backtracking factor applied when a trial step increases the objective.
    backtrack: float = 0.5
    max_backtracks: int = 24
    #: Multiplicative step growth attempted after an accepted step.
    step_growth: float = 1.10
    #: Diagonal column-norm preconditioning.
    precondition: bool = True
    seed: int = 7

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        if self.max_backtracks < 1:
            raise ValueError("max_backtracks must be >= 1")
        if not 0.0 < self.backtrack < 1.0:
            raise ValueError("backtrack must be strictly between 0 and 1")
        if self.step_growth < 1.0:
            raise ValueError("step_growth must be >= 1")
        if self.tolerance < 0.0:
            raise ValueError("tolerance must be >= 0")
        if self.patience < 1:
            raise ValueError("patience must be >= 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": "FISTA with adaptive restart, nonnegativity projection, backtracking",
            "preconditioner": "column-norm diagonal" if self.precondition else "none",
            "maxIterations": self.max_iterations,
            "tolerance": self.tolerance,
            "patience": self.patience,
        }


@dataclass
class OptimizationResult:
    weights: np.ndarray
    dose: np.ndarray
    objective: float
    iterations: int
    converged: bool
    reason: str
    history: list[float] = field(default_factory=list)
    step_size: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "objective": round(float(self.objective), 8),
            "iterations": int(self.iterations),
            "converged": bool(self.converged),
            "stopReason": self.reason,
            "finalStepSize": float(self.step_size),
            "activeBixels": int(np.count_nonzero(self.weights > 0.0)),
            "totalBixels": int(self.weights.size),
            "objectiveHistory": [round(float(value), 8) for value in self.history],
        }


def preconditioner(influence: DoseInfluence, enabled: bool) -> np.ndarray:
    """Diagonal scaling ``S`` mapping scaled variables to bixel weights."""
    if not enabled:
        return np.ones(influence.n_bixels, dtype=np.float32)
    norms = influence.column_norms()
    positive = norms[norms > 0.0]
    if positive.size == 0:
        raise ValueError("every bixel column is empty; the beams deposit no dose in this case")
    # Bixels that deposit nothing keep a finite scale so they stay at zero
    # rather than producing a division by zero.
    reference = float(np.median(positive))
    safe = np.where(norms > 0.0, norms, np.float32(reference))
    return (np.float32(reference) / safe).astype(np.float32)


def initial_weights(influence: DoseInfluence, objectives: ObjectiveSet, reference_gy: float) -> np.ndarray:
    """Uniform fluence scaled so the first objective structure sits at its dose."""
    weights = np.ones(influence.n_bixels, dtype=np.float32)
    dose = influence.dose(weights)
    first = objectives.objectives[0]
    indices = objectives.voxel_indices[first.structure]
    mean = float(dose[indices].mean())
    if mean <= 0.0:
        raise ValueError(
            f"a uniform fluence deposits no dose in {first.structure!r}. "
            "Check that the beams intersect the structure."
        )
    return weights * np.float32(max(reference_gy, 1e-6) / mean)


def optimize_fluence(
    influence: DoseInfluence,
    objectives: ObjectiveSet,
    reference_gy: float,
    settings: OptimizerSettings | None = None,
    progress: Callable[[str], None] | None = None,
) -> OptimizationResult:
    settings = settings or OptimizerSettings()
    scale = preconditioner(influence, settings.precondition)

    def dose_of(scaled: np.ndarray) -> np.ndarray:
        return influence.dose(scaled * scale)

    def gradient_of(voxel_gradient: np.ndarray) -> np.ndarray:
        return influence.transpose_dot(voxel_gradient) * scale

    start = initial_weights(influence, objectives, reference_gy) / scale
    lipschitz = influence.spectral_norm_squared(
        seed=settings.seed, scale=scale
    ) * objectives.max_voxel_curvature(influence.n_voxels)
    if not np.isfinite(lipschitz) or lipschitz <= 0.0:
        raise ValueError("could not estimate a step size; the influence matrix may be empty")
    step = 1.0 / lipschitz
    floor_step = step * 1e-10

    current = start.astype(np.float32)
    momentum = current.copy()
    theta = 1.0
    value = objectives.value(dose_of(current))
    history = [value]
    stalled = 0
    restarts = 0
    reason = "iteration limit reached"
    converged = False
    iteration = 0

    for iteration in range(1, settings.max_iterations + 1):
        _, voxel_gradient = objectives.value_and_gradient(dose_of(momentum))
        direction = gradient_of(voxel_gradient)

        trial_step = step
        candidate = current
        candidate_value = value
        for _ in range(settings.max_backtracks):
            candidate = np.maximum(momentum - np.float32(trial_step) * direction, np.float32(0.0))
            candidate_value = objectives.value(dose_of(candidate))
            if candidate_value <= value or trial_step <= floor_step:
                break
            trial_step *= settings.backtrack
        step = trial_step

        if candidate_value > value:
            # Monotone restart: drop the momentum, shrink the step, retry.
            momentum = current.copy()
            theta = 1.0
            step *= settings.backtrack
            restarts += 1
            if restarts >= settings.patience:
                reason = "line search could not decrease the objective"
                break
            continue

        theta_next = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * theta * theta))
        momentum = np.maximum(
            candidate + np.float32((theta - 1.0) / theta_next) * (candidate - current), np.float32(0.0)
        )
        theta = theta_next

        relative = (value - candidate_value) / max(abs(value), 1e-12)
        current = candidate
        value = candidate_value
        history.append(value)
        step *= settings.step_growth

        if relative < settings.tolerance:
            stalled += 1
            if stalled >= settings.patience:
                reason = f"relative objective change below {settings.tolerance:g}"
                converged = True
                break
        else:
            stalled = 0

        if progress is not None and iteration % 50 == 0:
            progress(f"iteration {iteration}: objective {value:.6g}, step {step:.4g}")

    return OptimizationResult(
        weights=(current * scale).astype(np.float32),
        dose=influence.dose(current * scale),
        objective=value,
        iterations=iteration,
        converged=converged,
        reason=reason,
        history=history,
        step_size=float(step),
    )
