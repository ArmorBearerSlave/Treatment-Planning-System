"""Builds a small training dataset for the AI dose-prediction feasibility
spike: for each synthetic XCAT prostate case with a full RT set (CT +
RTSTRUCT + RTDOSE), rasterizes the RTSTRUCT ROIs onto the CT voxel grid
and extracts the CT (HU) and RTDOSE (Gy) arrays, saving one compressed
.npz per case. Run once on the machine with access to the source DICOM
data (the DGX Spark).

Only 10 cases are available -- this is a severely small dataset for deep
learning (typical published dose-prediction work uses hundreds), and the
resulting model should be understood as a feasibility/architecture
demonstration, not a validated predictor. See governance notes for the
formal caveat.
"""

import glob
import os

import numpy as np
import pydicom

ROI_NAMES = [
    "BODY",
    "PROSTATE_PROXY",
    "GTV_ANALYTIC",
    "PTV_ANALYTIC",
    "BLADDER_PROXY",
    "RECTUM_PROXY",
    "FEMORAL_HEAD_L_PROXY",
    "FEMORAL_HEAD_R_PROXY",
]

DATA_ROOT = "/home/armorbearer/hupci-sim/brain-vct/dicom-xcat/VCT-PROSTATE-10X39-001-P1"
OUTPUT_DIR = os.path.expanduser("~/nl-tps-autoseg/dosepred-data")


def load_ct_volume(ct_dir):
    files = sorted(glob.glob(os.path.join(ct_dir, "*.dcm")))
    slices = [pydicom.dcmread(f) for f in files]
    slices.sort(key=lambda s: float(s.ImagePositionPatient[2]))
    volume = np.stack(
        [s.pixel_array.astype(np.float32) * s.RescaleSlope + s.RescaleIntercept for s in slices],
        axis=0,
    )
    first = slices[0]
    ipp = np.array(first.ImagePositionPatient, dtype=np.float64)
    iop = np.array(first.ImageOrientationPatient, dtype=np.float64)
    row_cosine, col_cosine = iop[:3], iop[3:]
    pixel_spacing = np.array(first.PixelSpacing, dtype=np.float64)
    slice_spacing = float(slices[1].ImagePositionPatient[2] - slices[0].ImagePositionPatient[2])
    return volume, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing


def rasterize_structures(rtstruct_path, shape, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing):
    from skimage.draw import polygon as sk_polygon

    ds = pydicom.dcmread(rtstruct_path)
    roi_numbers = {}
    for item in ds.StructureSetROISequence:
        if item.ROIName in ROI_NAMES:
            roi_numbers[item.ROINumber] = item.ROIName

    masks = {name: np.zeros(shape, dtype=np.uint8) for name in ROI_NAMES}
    for roi_contour in ds.ROIContourSequence:
        name = roi_numbers.get(roi_contour.ReferencedROINumber)
        if name is None or not hasattr(roi_contour, "ContourSequence"):
            continue
        for contour in roi_contour.ContourSequence:
            pts = np.array(contour.ContourData, dtype=np.float64).reshape(-1, 3)
            rel = pts - ipp
            cols = rel.dot(row_cosine) / pixel_spacing[1]
            rows = rel.dot(col_cosine) / pixel_spacing[0]
            slice_idx = int(round(rel[0].dot(np.cross(row_cosine, col_cosine)) / slice_spacing))
            if 0 <= slice_idx < shape[0]:
                rr, cc = sk_polygon(rows, cols, shape=shape[1:])
                masks[name][slice_idx, rr, cc] = 1
    return np.stack([masks[name] for name in ROI_NAMES], axis=0)


def load_dose_volume(rtdose_path, ct_shape):
    ds = pydicom.dcmread(rtdose_path)
    dose = ds.pixel_array.astype(np.float32) * float(ds.DoseGridScaling)
    assert dose.shape == ct_shape, f"dose shape {dose.shape} != CT shape {ct_shape}"
    return dose


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    case_dirs = sorted(glob.glob(os.path.join(DATA_ROOT, "VCT-PROSTATE-*")))
    for case_dir in case_dirs:
        case_id = os.path.basename(case_dir)
        ct_dir = os.path.join(case_dir, "CT", "BASELINE")
        rtstruct_path = os.path.join(case_dir, "RT", "RTSTRUCT.dcm")
        rtdose_path = os.path.join(case_dir, "RT", "RTDOSE.dcm")
        if not (os.path.isdir(ct_dir) and os.path.exists(rtstruct_path) and os.path.exists(rtdose_path)):
            print(f"Skipping {case_id}: missing CT/RTSTRUCT/RTDOSE")
            continue

        ct, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing = load_ct_volume(ct_dir)
        structures = rasterize_structures(
            rtstruct_path, ct.shape, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing
        )
        dose = load_dose_volume(rtdose_path, ct.shape)

        out_path = os.path.join(OUTPUT_DIR, f"{case_id}.npz")
        np.savez_compressed(out_path, ct=ct, structures=structures, dose=dose)
        print(f"{case_id}: ct {ct.shape}, structures {structures.shape}, dose {dose.shape}, "
              f"max dose {dose.max():.2f} Gy, structure voxel counts {structures.sum(axis=(1,2,3)).tolist()}")


if __name__ == "__main__":
    main()
