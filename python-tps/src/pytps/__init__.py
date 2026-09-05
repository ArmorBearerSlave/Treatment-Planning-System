"""pytps - a small, self-contained photon treatment-planning research engine.

Nonclinical. This package is not a commissioned dose authority, is not
verified or validated for patient care, and produces no clinically approved
output. Every plan artifact it writes is flagged accordingly.

It is deliberately independent of the Swift/Xcode application under
``native-tps/`` and the Cornerstone3D web application under
``app/cornerstone-tps/``. It shares no code with either; it interoperates only
through published file formats.
"""

from __future__ import annotations

__version__ = "0.1.0"
ENGINE_NAME = "pytps"
ENGINE_ID = f"{ENGINE_NAME}-{__version__}"

#: Fixed, machine-checkable statement of intended use. Every artifact carries it.
INTENDED_USE = (
    "Nonclinical research and engineering only. Synthetic or de-identified data only. "
    "Not for diagnosis, treatment planning decisions, or patient irradiation."
)

__all__ = ["__version__", "ENGINE_NAME", "ENGINE_ID", "INTENDED_USE"]
