"""Assemble training tensors from native XCAT labels and OpenTOPAS MC dose.

Inputs are kept outside Git on the DGX Spark. Each output stores CT, named
native-organ masks, and a total-course MC dose normalized to the declared
prescription. The dose target is not the analytic RTDOSE fixture.
"""

from __future__ import annotations

import argparse
import json
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
SHAPE_ZYX = (96, 180, 180)
PRESCRIPTION_GY = 70.2


def load_ct(ct_dir: Path) -> np.ndarray:
    slices = [pydicom.dcmread(path) for path in sorted(ct_dir.glob("*.dcm"))]
    slices.sort(key=lambda item: float(item.ImagePositionPatient[2]))
    if len(slices) != SHAPE_ZYX[0]:
        raise ValueError(f"expected {SHAPE_ZYX[0]} CT slices, found {len(slices)}")
    return np.stack(
        [
            item.pixel_array.astype(np.float32) * float(item.RescaleSlope)
            + float(item.RescaleIntercept)
            for item in slices
        ],
        axis=0,
    )


def load_native_masks(path: Path) -> np.ndarray:
    archive = np.load(path)
    missing = [name for name in ROI_NAMES if name not in archive.files]
    if missing:
        raise ValueError(f"missing native masks: {missing}")
    masks = np.stack([archive[name].astype(np.uint8) for name in ROI_NAMES], axis=0)
    if masks.shape[1:] != SHAPE_ZYX:
        raise ValueError(f"mask shape {masks.shape} does not match {SHAPE_ZYX}")
    return masks


def load_and_normalize_dose(path: Path) -> tuple[np.ndarray, dict[str, float]]:
    raw = np.load(path).astype(np.float32)
    if raw.shape != (180, 180, 96):
        raise ValueError(f"TOPAS dose shape {raw.shape} does not match (180, 180, 96)")
    dose_zyx = np.transpose(raw, (2, 1, 0))
    raw_peak = float(dose_zyx.max())
    if raw_peak <= 0:
        raise ValueError(f"dose has no positive voxels: {path}")
    scale_factor = PRESCRIPTION_GY / raw_peak
    normalized_gy = dose_zyx * scale_factor
    return normalized_gy / PRESCRIPTION_GY, {
        "raw_peak_gy": raw_peak,
        "prescription_gy": PRESCRIPTION_GY,
        "scale_factor": scale_factor,
    }


def assemble_case(case_id: str, dicom_root: Path, dose_root: Path, mask_root: Path, output_root: Path) -> dict:
    case_dir = dicom_root / case_id
    ct = load_ct(case_dir / "CT" / "BASELINE")
    masks = load_native_masks(mask_root / case_id / "masks.npz")
    dose, normalization = load_and_normalize_dose(dose_root / case_id / "combined_dose.npy")
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / f"{case_id}.npz"
    np.savez_compressed(output_path, ct=ct, structures=masks, dose=dose)
    return {
        "case_id": case_id,
        "output": str(output_path),
        "ct_shape_zyx": list(ct.shape),
        "structure_names": ROI_NAMES,
        "structure_voxel_counts": [int(mask.sum()) for mask in masks],
        "dose_shape_zyx": list(dose.shape),
        "dose_units": "normalized_total_course_fraction_of_70.2_Gy",
        "normalization": normalization,
        "dose_source": "OpenTOPAS_two_opposed_field_weighted_SOBP_exploratory_MC",
        "label_source": "XCAT2_color_code=1_native_labels",
        "synthetic_only": True,
        "clinical_use_permitted": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dicom-root", type=Path, required=True)
    parser.add_argument("--dose-root", type=Path, required=True)
    parser.add_argument("--mask-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    records = []
    for case_dir in sorted(args.dicom_root.glob("VCT-PROSTATE-*")):
        records.append(assemble_case(case_dir.name, args.dicom_root, args.dose_root, args.mask_root, args.output_root))
        print(records[-1]["case_id"], records[-1]["output"], flush=True)
    manifest = {
        "schema_version": "1.0",
        "dataset_id": "VCT-PROSTATE-MC-NATIVE-001",
        "synthetic_only": True,
        "clinical_use_permitted": False,
        "target": "OpenTOPAS exploratory MC dose, peak-normalized to 70.2 Gy",
        "structures": ROI_NAMES,
        "records": records,
    }
    (args.output_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"case_count": len(records), "output_root": str(args.output_root)}, indent=2))


if __name__ == "__main__":
    main()
