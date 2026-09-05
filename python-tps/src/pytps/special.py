"""Vectorised special functions.

numpy has no error function and this package deliberately avoids a scipy
dependency, so :func:`erf` uses the Abramowitz & Stegun 7.1.26 rational
approximation. Its maximum absolute error is 1.5e-7, which is well inside
float32 precision and far below the modelling error of the dose kernel.
"""

from __future__ import annotations

import numpy as np

_P = 0.3275911
_A = (0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429)

#: Worst-case absolute error of the approximation itself (1.5e-7). Evaluating
#: it in float32 adds rounding, so the observed error is a few times 1e-7.
ERF_MAX_ABS_ERROR = 1.0e-6


def erf(x: np.ndarray) -> np.ndarray:
    """Error function, accurate to about 1.5e-7 absolute."""
    values = np.asarray(x, dtype=np.float32)
    magnitude = np.abs(values)
    t = np.float32(1.0) / (np.float32(1.0) + np.float32(_P) * magnitude)
    poly = t * (
        np.float32(_A[0])
        + t
        * (
            np.float32(_A[1])
            + t * (np.float32(_A[2]) + t * (np.float32(_A[3]) + t * np.float32(_A[4])))
        )
    )
    result = np.float32(1.0) - poly * np.exp(-magnitude * magnitude)
    return np.where(values < 0, -result, result).astype(np.float32)


def gaussian_bar_integral(delta: np.ndarray, sigma: np.ndarray, width: float) -> np.ndarray:
    """Integral of a unit Gaussian over a bar of ``width`` centred at ``-delta``.

    ``delta`` is the signed offset from the bar centre to the evaluation point.
    Summing this over a lattice of adjacent bars covering more than about three
    standard deviations gives one, independently of the bar width - which is
    the property a bixel kernel must have if the plan is not to depend on the
    bixel size chosen.
    """
    scale = np.float32(1.0) / (sigma * np.float32(np.sqrt(2.0)))
    half = np.float32(0.5 * width)
    return (np.float32(0.5) * (erf((delta + half) * scale) - erf((delta - half) * scale))).astype(np.float32)
