"""Bridges to externally installed research codes.

Two are supported, both MATLAB-based and both used **as separately installed
dependencies**: no matRad or CERR source is copied, vendored, or modified here,
and neither checkout is written to.

- :mod:`pytps.external.matrad` runs matRad photon dose calculation and fluence
  optimisation, and imports the result as an independent dose distribution.
- :mod:`pytps.external.cerr` builds a CERR ``planC`` from a case and a dose and
  returns CERR's own dose-volume analysis, for cross-checking this package's
  DVH code against an independent implementation.

Both work the same way: freeze the inputs into a job folder, hash them, run a
generated adapter in a batch MATLAB process, and refuse to import a result that
does not bind back to those hashes. Nothing is imported into a plan without
that binding, and neither bridge confers approval, verification, commissioning,
or clinical validity on anything.

matRad and CERR are used under their own licences. See ``docs/EXTERNAL.md``.
"""

from __future__ import annotations

from .jobs import JobError, JobFolder, VolumeSpec
from .matlab import MatlabError, MatlabRunner, find_matlab

__all__ = [
    "JobError",
    "JobFolder",
    "VolumeSpec",
    "MatlabError",
    "MatlabRunner",
    "find_matlab",
]
