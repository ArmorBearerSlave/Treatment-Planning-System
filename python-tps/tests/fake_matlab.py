"""A stand-in for MATLAB, so the bridges can be tested without one.

It implements the same job contract the real adapters do: check the frozen
input digests, read the raw volumes, write a result that binds back to those
digests. It does **not** implement matRad or CERR - the dose it invents is
arbitrary and the metrics it reports are computed from that dose. What the
tests exercise is the bridge: freezing, hashing, launching, binding, importing
and reconciling.

Behaviour is steered by the PYTPS_FAKE_MATLAB environment variable:

    ``ok`` (default)  produce a valid result
    ``fail``          exit non-zero without producing one
    ``nonconverged``  report a non-converged optimisation
    ``tamper``        produce a result whose digests do not bind
    ``drift``         (CERR) report metrics that disagree with the dose
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_volume(path: Path, dtype: str, dimensions) -> np.ndarray:
    raw = np.frombuffer(path.read_bytes(), dtype=dtype)
    nx, ny, nz = dimensions
    return np.ascontiguousarray(raw.reshape(nz, ny, nx).transpose(2, 1, 0))


def write_volume(path: Path, array: np.ndarray) -> None:
    path.write_bytes(np.ascontiguousarray(array.transpose(2, 1, 0)).ravel().astype("<f4").tobytes())


def nearest_rank(values: np.ndarray, fraction: float) -> float:
    ordered = np.sort(np.asarray(values, dtype=np.float64).reshape(-1))[::-1]
    return float(ordered[max(1, int(np.ceil(fraction * ordered.size))) - 1])


def synthetic_dose(labels: np.ndarray, target_label: int, scale: float) -> np.ndarray:
    """A crude but deterministic stand-in: hot in the target, cooler outside."""
    dose = np.zeros(labels.shape, dtype=np.float32)
    dose[labels != 0] = 0.3 * scale
    dose[labels == target_label] = scale
    # A little structure so histograms are not degenerate.
    ramp = np.linspace(0.9, 1.1, labels.shape[2], dtype=np.float32)
    return dose * ramp[None, None, :]


def main(argv: list[str]) -> int:
    behaviour = os.environ.get("PYTPS_FAKE_MATLAB", "ok")
    command = argv[argv.index("-batch") + 1] if "-batch" in argv else ""
    if "version" in command and "fprintf" in command:
        print("0.0-fake|FAKE64")
        return 0
    if behaviour == "fail":
        print("fake MATLAB was told to fail", file=sys.stderr)
        return 1

    paths = re.findall(r"'([^']*)'", command)
    job = Path(paths[1]) if len(paths) > 1 else Path(paths[0])
    record = json.loads((job / "job.json").read_text(encoding="utf-8"))
    for entry in record["inputs"]:
        actual = sha256_file(job / entry["file"])
        if actual != entry["sha256"]:
            print(f"frozen input changed: {entry['file']}", file=sys.stderr)
            return 1

    source = json.loads((job / "source.json").read_text(encoding="utf-8"))
    request = json.loads((job / "request.json").read_text(encoding="utf-8"))
    dimensions = tuple(source["grid"]["dimensions"])
    labels = read_volume(job / "labels.i16", "<i2", dimensions)

    if record["kind"] == "matrad":
        if behaviour == "nonconverged":
            print("fake matRad: optimiser did not converge", file=sys.stderr)
            return 1
        target = next(
            item["label"] for item in source["structures"] if item["name"] == request["target"]
        )
        forward = request.get("mode") == "forward"
        dose = synthetic_dose(labels, target, 1.0 if forward else float(request["prescriptionGy"]))
        write_volume(job / "dose.f32", dose)
        payload = {
            "schemaVersion": 1,
            "kind": "matrad",
            "jobID": record["jobID"],
            "sourceDigest": sha256_file(job / "source.json"),
            "requestDigest": sha256_file(job / "request.json"),
            "clinicalReleaseAllowed": False,
            "doseBasis": "relative-uniform-fluence" if forward else "total-course-physical-Gy",
            "doseFile": "dose.f32",
            "doseDigest": sha256_file(job / "dose.f32"),
            "doseDtype": "float32",
            "doseLayout": "X-fastest XYZ",
            "weights": [1.0, 1.0],
            "evidence": {
                "matRadVersion": "fake",
                "MATLABVersion": "0.0-fake",
                "optimizer": "fake",
                "optimizerConverged": True,
                "mode": request.get("mode", "optimize"),
                "bixelCount": 2,
                "machine": "fake Generic photons",
                "isocenterDeltaMM": [0.0, 0.0, 0.0],
                "normalization": "fake",
            },
        }
        if behaviour == "tamper":
            payload["requestDigest"] = "0" * 64
        (job / "result.json").write_text(json.dumps(payload), encoding="utf-8")
        print("fake matRad result ready")
        return 0

    if record["kind"] == "cerr":
        dose = read_volume(job / "dose.f32", "<f4", dimensions)
        drift = 0.25 if behaviour == "drift" else 0.0
        records = []
        for item in source["structures"]:
            values = dose[labels == item["label"]]
            if values.size == 0:
                continue
            entry = {
                "label": item["label"],
                "name": item["name"],
                "sampleCount": int(values.size),
                "volumeCC": float(values.size),
                "meanGy": float(values.mean()) + drift,
                "minGy": float(values.min()),
                "maxGy": float(values.max()),
                "maxSampleDifferenceGy": 0.0,
                "binCentersGy": [0.0],
                "differentialVolumeCC": [float(values.size)],
            }
            for fraction in (0.02, 0.50, 0.95, 0.98):
                entry[f"d{round(fraction * 100):02d}Gy"] = nearest_rank(values, fraction)
            records.append(entry)
        payload = {
            "schemaVersion": 1,
            "kind": "cerr",
            "jobID": record["jobID"],
            "sourceDigest": sha256_file(job / "source.json"),
            "requestDigest": sha256_file(job / "request.json"),
            "doseDigest": sha256_file(job / "dose.f32"),
            "clinicalReleaseAllowed": False,
            "records": records,
            "evidence": {"MATLABVersion": "0.0-fake", "libraryRoot": "fake"},
        }
        (job / "report.json").write_text(json.dumps(payload), encoding="utf-8")
        print("fake CERR report ready")
        return 0

    print(f"fake MATLAB does not know job kind {record['kind']!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
