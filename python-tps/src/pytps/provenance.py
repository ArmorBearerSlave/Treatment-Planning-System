"""Local provenance records.

These are *local* integrity records: content digests, versions, and a
timestamp. They are not authenticated signatures, do not establish an approval,
and do not freeze the dependency environment. They exist so that a plan
artifact can be checked against the inputs it claims to come from.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from . import ENGINE_ID, INTENDED_USE, __version__

PACKAGE_ROOT = Path(__file__).resolve().parent


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(payload: Any) -> str:
    return sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def sha256_array(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    return sha256_bytes(contiguous.tobytes())


def engine_digest() -> dict[str, Any]:
    """Digest every source file of this package, plus a combined digest."""
    files = sorted(path for path in PACKAGE_ROOT.rglob("*.py") if "__pycache__" not in path.parts)
    per_file = {path.relative_to(PACKAGE_ROOT).as_posix(): sha256_file(path) for path in files}
    combined = sha256_bytes(
        "\n".join(f"{name}:{digest}" for name, digest in sorted(per_file.items())).encode("utf-8")
    )
    return {"combined": combined, "files": per_file}


def environment_record() -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(terse=True),
        "machine": platform.machine(),
    }


def build_record(inputs: dict[str, Any]) -> dict[str, Any]:
    """Assemble the provenance block carried by every plan artifact."""
    return {
        "engine": ENGINE_ID,
        "engineVersion": __version__,
        "engineSource": engine_digest(),
        "environment": environment_record(),
        "generatedUTC": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": inputs,
        "intendedUse": INTENDED_USE,
        "clinicalUsePermitted": False,
        "approvalState": "none",
        "verificationState": "not_verified",
        "notes": [
            "Local content digests only. Not an authenticated signature.",
            "No commissioning, beam-model measurement, or absolute dose calibration exists.",
            "No named person has reviewed or approved this artifact.",
        ],
    }
