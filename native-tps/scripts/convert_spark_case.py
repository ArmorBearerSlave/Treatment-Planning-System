#!/usr/bin/env python3
"""Convert one Spark XCAT/DICOM/NPZ case to the native PhantomCase JSON contract.

The Spark pipeline does not provide a meaningful MR acquisition. Conversion
therefore rejects by default; --synthetic-mr creates an explicitly labelled
placeholder MR channel for pipeline/display tests only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from pathlib import Path

import numpy as np
import pydicom


ROI_NAMES = [
    "PROSTATE",
    "BLADDER",
    "RECTUM",
    "SEMINAL_VESICLES",
    "ASCENDING_LARGE_BOWEL",
    "DESCENDING_LARGE_BOWEL",
    "SMALL_BOWEL",
]
COLORS = {
    "PROSTATE": [1.0, 0.2, 0.2],
    "BLADDER": [1.0, 0.75, 0.2],
    "RECTUM": [0.4, 0.55, 1.0],
    "SEMINAL_VESICLES": [1.0, 0.4, 0.8],
    "ASCENDING_LARGE_BOWEL": [0.3, 0.8, 0.6],
    "DESCENDING_LARGE_BOWEL": [0.3, 0.8, 0.6],
    "SMALL_BOWEL": [0.5, 0.9, 0.4],
}


def load_ct(ct_dir: Path):
    slices = [pydicom.dcmread(path) for path in sorted(ct_dir.glob("*.dcm"))]
    slices.sort(key=lambda item: float(item.ImagePositionPatient[2]))
    if len(slices) < 2:
        raise ValueError("CT directory needs at least two DICOM slices")
    first = slices[0]
    iop = np.asarray(first.ImageOrientationPatient, dtype=np.float64)
    row, col = iop[:3], iop[3:]
    normal = np.cross(row, col)
    ipps = [np.asarray(item.ImagePositionPatient, dtype=np.float64) for item in slices]
    dz = float(np.dot(ipps[1] - ipps[0], normal))
    if dz <= 0:
        raise ValueError("CT slices are not ordered along the positive orientation normal")
    ct_zyx = np.stack(
        [item.pixel_array.astype(np.float32) * float(item.RescaleSlope) + float(item.RescaleIntercept) for item in slices],
        axis=0,
    )
    x, y = ct_zyx.shape[2], ct_zyx.shape[1]
    grid = {
        "dimensions": [x, y, len(slices)],
        "spacing": [float(first.PixelSpacing[1]), float(first.PixelSpacing[0]), dz],
        "origin": [float(value) for value in first.ImagePositionPatient],
        "direction": [float(row[0]), float(row[1]), float(row[2]), float(col[0]), float(col[1]), float(col[2]), float(normal[0]), float(normal[1]), float(normal[2])],
        "frameID": str(first.FrameOfReferenceUID),
    }
    return slices, ct_zyx, grid


def volume(grid, modality, units, values):
    flat = np.asarray(values, dtype=np.float32).reshape(-1)
    return {"grid": grid, "modality": modality, "units": units, "values": [float(value) for value in flat]}


def compact_json(payload, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--ct-dir", type=Path, required=True)
    parser.add_argument("--masks", type=Path, required=True, help="NPZ with named native masks")
    parser.add_argument("--dose", type=Path, required=True, help="TOPAS combined_dose.npy")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--synthetic-mr", action="store_true")
    parser.add_argument("--plan-json", type=Path, required=True)
    parser.add_argument("--parameter-file", type=Path, required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--histories", type=int, default=180000)
    parser.add_argument("--transport-version", default="OpenTOPAS 4.2.p3 exploratory")
    parser.add_argument("--nbio-version", default="TOPAS-nBio 4.1.0 exploratory")
    args = parser.parse_args()
    if not args.synthetic_mr:
        raise SystemExit("Refusing conversion: Spark XCAT has no meaningful MR acquisition; pass --synthetic-mr only for explicit pipeline fixtures")
    if args.histories <= 0:
        raise ValueError("histories must be positive")
    if len(args.image_digest) < 16:
        raise ValueError("image-digest must identify the pinned XCAT2 runtime")

    ct_slices, ct_zyx, grid = load_ct(args.ct_dir)
    masks_archive = np.load(args.masks)
    missing = [name for name in ROI_NAMES if name not in masks_archive.files]
    if missing:
        raise ValueError(f"missing masks: {missing}")
    labels = np.zeros(ct_zyx.shape, dtype=np.float32)
    structures = []
    for label_id, name in enumerate(ROI_NAMES, start=1):
        mask = masks_archive[name].astype(bool)
        if mask.shape != ct_zyx.shape:
            raise ValueError(f"mask {name} shape {mask.shape} != CT {ct_zyx.shape}")
        labels[mask] = label_id
        structures.append({"id": label_id, "name": name, "color": COLORS[name]})

    raw_dose_xyz = np.load(args.dose).astype(np.float32)
    if raw_dose_xyz.shape != (ct_zyx.shape[2], ct_zyx.shape[1], ct_zyx.shape[0]):
        raise ValueError(f"dose {raw_dose_xyz.shape} does not match TOPAS XYZ grid")
    dose_zyx = np.transpose(raw_dose_xyz, (2, 1, 0))
    raw_peak = float(dose_zyx.max())
    if raw_peak <= 0:
        raise ValueError("dose has no positive peak")
    scale = 70.2 / raw_peak
    dose_gy = dose_zyx * scale
    mr = np.zeros_like(ct_zyx, dtype=np.float32)
    case_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"nltps:spark:{args.case_id}"))
    bundle = {
        "schemaVersion": 1,
        "id": case_uuid,
        "name": args.case_id,
        "generator": "Spark XCAT2 + OpenTOPAS exploratory converter",
        "generatorVersion": "xcat2/OpenTOPAS adapter v1",
        "syntheticOnly": True,
        "clinicalUsePermitted": False,
        "intendedUse": "synthetic-research-only",
        "recipe": {"anatomyID": args.case_id, "seed": 0, "bodyScale": 1, "targetRadiusMM": 8, "motionPhase": 0, "nBioProfile": "unbound"},
        "ct": volume(grid, "ct", "HU", ct_zyx),
        "mr": volume(grid, "mr", "a.u.", mr),
        "truth": volume(grid, "labels", "label", labels),
        "structures": structures,
        "simulation": {
            "transportEngine": "OpenTOPAS",
            "transportVersion": args.transport_version,
            "nBioVersion": args.nbio_version,
            "parameterFileSHA256": hashlib.sha256(args.parameter_file.read_bytes()).hexdigest(),
            "histories": args.histories,
            "normalization": f"two opposed fields; raw TOPAS peak {raw_peak:.9g}; peak normalized to 70.2 Gy; scale {scale:.9g}",
            "referenceDose": volume(grid, "dose", "Gy", dose_gy),
            "observations": [],
        },
        "sourceNotes": {
            "mr": "Synthetic zero placeholder; not an acquisition and not suitable for MR training.",
            "dose": "Exploratory OpenTOPAS Monte Carlo, not commissioned clinical dose.",
            "lymphNodes": "Excluded by design.",
            "xcatPlanSHA256": hashlib.sha256(args.plan_json.read_bytes()).hexdigest(),
            "xcatImageDigest": args.image_digest,
        },
    }
    compact_json(bundle, args.output)
    print(json.dumps({"output": str(args.output), "bytes": args.output.stat().st_size, "structures": len(structures), "raw_peak_gy": raw_peak, "scale_factor": scale}))


if __name__ == "__main__":
    main()
