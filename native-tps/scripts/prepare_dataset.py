"""Convert native research bundles into explicit, anatomy-grouped NumPy training pairs.

Predicted artifacts NEVER become ground truth. Dose targets must come from the
source's separately identified transport simulation. Requires numpy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np


def volume_array(volume, modality, units):
    grid = volume["grid"]
    dimensions = grid["dimensions"]
    if len(dimensions) != 3 or any(type(x) is not int or not 2 <= x <= 512 for x in dimensions):
        raise ValueError("Invalid volume dimensions")
    count = int(np.prod(dimensions))
    if count > 8_388_608 or volume["modality"] != modality or volume["units"] != units:
        raise ValueError("Invalid modality, units or volume size")
    values = np.asarray(volume["values"], dtype=np.float32)
    if values.ndim != 1 or values.size != count or not np.isfinite(values).all():
        raise ValueError("Invalid voxel values")
    if modality == "dose" and (values < 0).any():
        raise ValueError("Negative dose")
    return values.reshape(tuple(reversed(dimensions)))


def training_pair(bundle, task, allow_fixture=False):
    if bundle.get("schemaVersion") != 1 or bundle.get("clinicalUsePermitted") is not False or bundle.get("intendedUse") != "synthetic-research-only":
        raise ValueError("Not a native synthetic research bundle")
    source = bundle["source"]
    if source.get("syntheticOnly") is not True:
        raise ValueError("Only synthetic sources are accepted")
    fixture = source["generator"].startswith("Analytic pelvis fixture")
    if fixture and not allow_fixture:
        raise ValueError("Analytic fixtures are excluded; --allow-fixture is for pipeline tests only")
    ct = volume_array(source["ct"], "ct", "HU")
    labels = volume_array(source["truth"], "labels", "label")
    mr = volume_array(source["mr"], "mr", "a.u.")
    if source["ct"]["grid"] != source["truth"]["grid"] or source["ct"]["grid"] != source["mr"]["grid"]:
        raise ValueError("Spatial grid mismatch")
    if task == "contour":
        image, target = ct, labels
    elif task == "syntheticCT":
        image, target = mr, ct
    elif task == "predictDose":
        evidence = source.get("simulation")
        if not evidence or not evidence.get("normalization") or evidence.get("histories", 0) <= 0:
            raise ValueError("Dose training requires normalized transport reference dose and simulation evidence")
        if evidence["referenceDose"]["grid"] != source["ct"]["grid"]:
            raise ValueError("Transport dose grid mismatch")
        image, target = ct, volume_array(evidence["referenceDose"], "dose", "Gy")
    else:
        raise ValueError("Unknown task")
    if (labels < 0).any() or not np.equal(labels, np.floor(labels)).all():
        raise ValueError("Invalid label map")
    return image, target, labels


def split_for(anatomy):
    canonical = json.dumps(anatomy, ensure_ascii=False, separators=(",", ":")).encode()
    bucket = int(hashlib.sha256(canonical).hexdigest()[:4], 16) % 10
    return "train" if bucket < 8 else "validation" if bucket == 8 else "test"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundles", type=Path, nargs="+")
    parser.add_argument("--task", required=True, choices=["contour", "predictDose", "syntheticCT"])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-fixture", action="store_true")
    parser.add_argument("--validator", type=Path, default=Path(__file__).resolve().parents[1] / ".build/debug/tps-check")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Choose a new output directory; existing datasets are never overwritten")
    # Validate the complete batch before writing any files.
    prepared, seen = [], set()
    if not args.validator.is_file():
        raise ValueError("Build the native validator first with swift build, or supply --validator")
    for path in args.bundles:
        if path.stat().st_size > 256_000_000:
            raise ValueError("Bundle too large")
        raw = path.read_bytes()
        subprocess.run([str(args.validator.resolve()), "--validate-bundle", str(path.resolve())], check=True, capture_output=True, timeout=120)
        bundle = json.loads(raw)
        source = bundle["source"]
        if source["id"] in seen:
            raise ValueError("Duplicate case identity")
        seen.add(source["id"])
        arrays = training_pair(bundle, args.task, args.allow_fixture)
        anatomy = source["recipe"]["anatomyID"]
        split = split_for(anatomy)
        if bundle.get("split") != split:
            raise ValueError("Split differs from anatomy-group policy")
        # A digest-derived filename avoids user-controlled paths.
        key = hashlib.sha256(source["id"].encode()).hexdigest()[:24]
        entry = dict(caseID=source["id"], anatomyID=anatomy, split=split,
                     file=f"{key}.npz", bundleSHA256=hashlib.sha256(raw).hexdigest(),
                     nativeSourceHash=bundle["sourceHash"], generator=source["generator"],
                     generatorVersion=source["generatorVersion"], recipe=source["recipe"],
                     grid=source["ct"]["grid"], structures=source["structures"])
        if source.get("simulation"):
            entry["simulation"] = {k: v for k, v in source["simulation"].items() if k != "referenceDose"}
        prepared.append((entry, arrays))
    args.output.mkdir(parents=True)
    for entry, (image, target, labels) in prepared:
        np.savez_compressed(args.output / entry["file"], image=image, target=target, structures=labels)
    manifest = dict(schemaVersion=1, task=args.task, axisOrder="ZYX", clinicalUsePermitted=False,
                    datasetApproval="pending", fixtureDataAllowed=args.allow_fixture,
                    cases=[entry for entry, _ in prepared])
    (args.output / "dataset.json").write_text(json.dumps(manifest, indent=2))
    print(f"Prepared {len(prepared)} {args.task} pairs; dataset approval remains pending.")


if __name__ == "__main__":
    main()
