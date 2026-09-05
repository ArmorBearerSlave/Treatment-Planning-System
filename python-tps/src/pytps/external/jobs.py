"""Job folders: frozen inputs, content digests, and result binding.

A bridge run is a directory. Inputs are written once and hashed; the exact
adapter that will execute is copied in and hashed; the tool locations and
versions are recorded. The adapter re-checks those hashes before it does any
work, and the importer refuses a result that does not carry them back.

That gives one useful property: a result in a job folder can only be imported
against the inputs it was actually computed from. It is a local integrity
binding, not an authenticated signature, and it establishes nothing about the
correctness of the external code.

Volume exchange
---------------
Volumes are **raw little-endian binary**, not JSON. A 3.1 million voxel CT is
66 MB of JSON and loses bytes to decimal round-tripping; the same data is 12 MB
of ``float32`` that MATLAB reads with one ``fread``. The layout is the same
X-fastest XYZ order the rest of this repository uses, so index ``(i, j, k)``
sits at offset ``i + nx * (j + ny * k)``.
"""

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .. import ENGINE_ID, INTENDED_USE
from ..geometry import Grid
from ..provenance import sha256_file, sha256_json

JOB_SCHEMA_VERSION = 1

#: numpy dtypes allowed in a job volume, with the MATLAB ``fread`` precision
#: string that reads each one back.
DTYPES: dict[str, tuple[str, str]] = {
    "float32": ("<f4", "float32"),
    "int16": ("<i2", "int16"),
}


class JobError(RuntimeError):
    """Raised when a job folder cannot be built, or a result cannot be trusted."""


@dataclass(frozen=True)
class VolumeSpec:
    """One raw binary volume in a job folder."""

    name: str
    dtype: str
    dimensions: tuple[int, int, int]
    byte_count: int
    digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.name,
            "dtype": self.dtype,
            "matlabPrecision": DTYPES[self.dtype][1],
            "byteOrder": "little-endian",
            "layout": "X-fastest XYZ",
            "dimensions": list(self.dimensions),
            "bytes": self.byte_count,
            "sha256": self.digest,
        }


def write_volume(path: Path, grid: Grid, array: np.ndarray, dtype: str) -> VolumeSpec:
    """Write ``array`` as a raw little-endian X-fastest volume."""
    if dtype not in DTYPES:
        raise JobError(f"unsupported job volume dtype {dtype!r}; expected one of {sorted(DTYPES)}")
    flat = grid.to_flat(np.asarray(array)).astype(DTYPES[dtype][0], copy=False)
    path.write_bytes(flat.tobytes())
    return VolumeSpec(
        name=path.name,
        dtype=dtype,
        dimensions=grid.dimensions,
        byte_count=path.stat().st_size,
        digest=sha256_file(path),
    )


def read_volume(path: Path, grid: Grid, dtype: str, expected_digest: str | None = None) -> np.ndarray:
    """Read a raw volume back into a ``(nx, ny, nz)`` array."""
    if dtype not in DTYPES:
        raise JobError(f"unsupported job volume dtype {dtype!r}")
    if not path.exists():
        raise JobError(f"expected volume {path.name} was not written by the adapter")
    if expected_digest is not None:
        actual = sha256_file(path)
        if actual != expected_digest:
            raise JobError(
                f"{path.name} does not match the digest the adapter recorded for it "
                f"({actual[:12]} vs {expected_digest[:12]}). Treat the job as failed."
            )
    raw = np.frombuffer(path.read_bytes(), dtype=DTYPES[dtype][0])
    if raw.size != grid.voxel_count:
        raise JobError(
            f"{path.name} holds {raw.size} values but the grid has {grid.voxel_count}. "
            "The adapter changed the grid, which this bridge does not allow."
        )
    return grid.from_flat(raw.astype(np.float32) if dtype == "float32" else raw, dtype=np.float32 if dtype == "float32" else np.int16)


class JobFolder:
    """A frozen, hashed working directory for one external-tool run."""

    def __init__(self, path: Path, kind: str) -> None:
        self.path = Path(path)
        self.kind = kind
        self.inputs: dict[str, str] = {}
        self.volumes: dict[str, VolumeSpec] = {}
        self._frozen = False

    # -- construction -----------------------------------------------------
    @classmethod
    def create(cls, root: str | Path, kind: str, job_id: str | None = None) -> "JobFolder":
        root = Path(root)
        identifier = job_id or uuid.uuid4().hex[:16]
        path = root / f"{kind}-{identifier}"
        if path.exists():
            raise JobError(f"job folder {path} already exists; refusing to reuse it")
        path.mkdir(parents=True)
        return cls(path, kind)

    def add_json(self, name: str, payload: Any) -> Path:
        self._require_open()
        path = self.path / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.inputs[name] = sha256_file(path)
        return path

    def add_volume(self, name: str, grid: Grid, array: np.ndarray, dtype: str) -> VolumeSpec:
        self._require_open()
        spec = write_volume(self.path / name, grid, array, dtype)
        self.volumes[name] = spec
        self.inputs[name] = spec.digest
        return spec

    def add_adapter(self, source: Path) -> Path:
        """Copy the adapter that will run, so the job records what executed."""
        self._require_open()
        if not source.exists():
            raise JobError(f"adapter {source} not found")
        target = self.path / source.name
        shutil.copyfile(source, target)
        self.inputs[source.name] = sha256_file(target)
        return target

    def freeze(self, tools: dict[str, Any], notes: dict[str, Any] | None = None) -> dict[str, Any]:
        """Write ``job.json`` and stop accepting inputs."""
        self._require_open()
        record = {
            "schemaVersion": JOB_SCHEMA_VERSION,
            "kind": self.kind,
            "jobID": self.path.name,
            "engine": ENGINE_ID,
            "createdUTC": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "intendedUse": INTENDED_USE,
            "clinicalUsePermitted": False,
            "tools": tools,
            # Lists, not maps: MATLAB's jsondecode rewrites field names that are
            # not valid identifiers, so "ct.f32" would come back as "ct_f32" and
            # the adapter could not check the digest of the file it was given.
            "inputs": [
                {"file": name, "sha256": digest} for name, digest in sorted(self.inputs.items())
            ],
            "volumes": [spec.to_dict() for _, spec in sorted(self.volumes.items())],
            "notes": notes or {},
        }
        (self.path / "job.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self._frozen = True
        return record

    def _require_open(self) -> None:
        if self._frozen:
            raise JobError("this job is frozen; create a new job rather than editing a submitted one")

    # -- inspection -------------------------------------------------------
    def file(self, name: str) -> Path:
        return self.path / name

    def record(self) -> dict[str, Any]:
        path = self.path / "job.json"
        if not path.exists():
            raise JobError(f"{self.path} has no job.json; it was never frozen")
        return json.loads(path.read_text(encoding="utf-8"))

    def check_inputs_unchanged(self) -> None:
        """Confirm no frozen input was edited while the job ran."""
        record = self.record()
        changed = [
            entry["file"]
            for entry in record["inputs"]
            if not (self.path / entry["file"]).exists()
            or sha256_file(self.path / entry["file"]) != entry["sha256"]
        ]
        if changed:
            raise JobError(
                f"frozen job inputs changed while the job ran: {sorted(changed)}. "
                "The result cannot be bound to its inputs; discard it."
            )

    def load_result(self, name: str, required_bindings: dict[str, str]) -> dict[str, Any]:
        """Load a result document and check it binds to the frozen inputs."""
        path = self.path / name
        if not path.exists():
            raise JobError(
                f"the adapter produced no {name}. Read {self.file('matlab.log').name} for what "
                "MATLAB reported; a failed or non-converged run deliberately emits no result."
            )
        payload = json.loads(path.read_text(encoding="utf-8"))
        if int(payload.get("schemaVersion", -1)) != JOB_SCHEMA_VERSION:
            raise JobError(
                f"{name} declares schema version {payload.get('schemaVersion')}, expected {JOB_SCHEMA_VERSION}"
            )
        if payload.get("clinicalReleaseAllowed", False):
            raise JobError(f"{name} claims clinical release, which this package refuses to import")
        for key, expected in required_bindings.items():
            actual = payload.get(key)
            if actual != expected:
                raise JobError(
                    f"{name} was computed from different inputs: {key} is {str(actual)[:12]} "
                    f"but this job froze {expected[:12]}. Discard the result."
                )
        return payload


def job_summary(record: dict[str, Any], matlab: dict[str, Any], extra: Iterable[tuple[str, Any]] = ()) -> dict[str, Any]:
    """The block a plan artifact carries to describe an external run."""
    summary = {
        "jobID": record["jobID"],
        "kind": record["kind"],
        "createdUTC": record["createdUTC"],
        "tools": record["tools"],
        "inputDigests": record["inputs"],
        "matlab": matlab,
        "clinicalUsePermitted": False,
        "note": "Local provenance for an external research code. Not an approval or a verification.",
    }
    summary.update(dict(extra))
    summary["digest"] = sha256_json(summary)
    return summary
