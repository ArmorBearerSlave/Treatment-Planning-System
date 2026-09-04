"""Convert XCAT2 color_code=1 labels into masks and synthetic RTSTRUCT contours."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
from pydicom.uid import ExplicitVRLittleEndian, RTStructureSetStorage, generate_uid
from skimage.measure import find_contours


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--shape", nargs=3, type=int, metavar=("Z", "Y", "X"), required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--ct-dir", type=Path, required=True)
    parser.add_argument("--mask-output", type=Path, required=True)
    parser.add_argument("--rtstruct-output", type=Path, required=True)
    return parser.parse_args()


def load_ct(ct_dir: Path):
    slices = [pydicom.dcmread(path, stop_before_pixels=True) for path in sorted(ct_dir.glob("*.dcm"))]
    if len(slices) < 2:
        raise ValueError("CT directory must contain at least two slices")
    slices.sort(key=lambda item: float(item.ImagePositionPatient[2]))
    first = slices[0]
    iop = np.asarray(first.ImageOrientationPatient, dtype=np.float64)
    row_cosine, col_cosine = iop[:3], iop[3:]
    normal = np.cross(row_cosine, col_cosine)
    ipps = [np.asarray(item.ImagePositionPatient, dtype=np.float64) for item in slices]
    spacing = float(np.dot(ipps[1] - ipps[0], normal))
    if spacing <= 0:
        raise ValueError("CT slices are not ordered along the positive normal")
    return slices, ipps[0], row_cosine, col_cosine, np.asarray(first.PixelSpacing, dtype=np.float64), spacing


def load_masks(labels_path: Path, shape: tuple[int, int, int], label_map_path: Path):
    labels = np.fromfile(labels_path, dtype="<f4")
    if labels.size != int(np.prod(shape)):
        raise ValueError(f"label volume has {labels.size} voxels; expected {np.prod(shape)}")
    labels = labels.reshape(shape)
    label_map = json.loads(label_map_path.read_text(encoding="utf-8"))
    masks = {}
    for name, ids in label_map.items():
        if not isinstance(name, str) or not name or not isinstance(ids, list) or not ids:
            raise ValueError(f"invalid label group: {name!r}")
        mask = np.isin(labels, np.asarray(ids, dtype=np.float32))
        if not mask.any():
            raise ValueError(f"label group {name!r} has no voxels: {ids}")
        masks[name] = mask
    return masks


def to_patient_point(row, col, slice_index, ipp, row_cosine, col_cosine, pixel_spacing, normal, slice_spacing):
    point = (
        ipp
        + col * pixel_spacing[1] * row_cosine
        + row * pixel_spacing[0] * col_cosine
        + slice_index * slice_spacing * normal
    )
    return [float(value) for value in point]


def write_rtstruct(output_path, ct_slices, masks, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing):
    normal = np.cross(row_cosine, col_cosine)
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = RTStructureSetStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()
    ds = FileDataset(str(output_path), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.SOPClassUID = RTStructureSetStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = ct_slices[0].StudyInstanceUID
    ds.SeriesInstanceUID = generate_uid()
    ds.FrameOfReferenceUID = ct_slices[0].FrameOfReferenceUID
    ds.Modality = "RTSTRUCT"
    ds.SeriesNumber = 900
    ds.InstanceNumber = 1
    ds.StructureSetLabel = "XCAT_LABELS"
    ds.StructureSetName = "XCAT_SYNTHETIC_LABELS"
    ds.StructureSetDescription = "XCAT2 LABEL-DERIVED; SYNTHETIC; NOT FOR PLANNING"
    ds.ApprovalStatus = "UNAPPROVED"
    ds.StructureSetDate = "20000101"
    ds.StructureSetTime = "000000"

    contour_images = []
    for image in ct_slices:
        reference = Dataset()
        reference.ReferencedSOPClassUID = image.SOPClassUID
        reference.ReferencedSOPInstanceUID = image.SOPInstanceUID
        contour_images.append(reference)
    series = Dataset()
    series.SeriesInstanceUID = ct_slices[0].SeriesInstanceUID
    series.ContourImageSequence = Sequence(contour_images)
    study = Dataset()
    study.ReferencedSOPClassUID = "1.2.840.10008.3.1.2.3.1"
    study.ReferencedSOPInstanceUID = ct_slices[0].StudyInstanceUID
    study.RTReferencedSeriesSequence = Sequence([series])
    frame = Dataset()
    frame.FrameOfReferenceUID = ct_slices[0].FrameOfReferenceUID
    frame.RTReferencedStudySequence = Sequence([study])
    ds.ReferencedFrameOfReferenceSequence = Sequence([frame])

    roi_items = []
    contour_items = []
    for roi_number, (name, mask) in enumerate(masks.items(), start=1):
        roi = Dataset()
        roi.ROINumber = roi_number
        roi.ReferencedFrameOfReferenceUID = ct_slices[0].FrameOfReferenceUID
        roi.ROIName = name
        roi.ROIGenerationAlgorithm = "AUTOMATIC"
        roi.ROIGenerationDescription = "XCAT2 color_code=1 voxel labels"
        roi_items.append(roi)

        roi_contour = Dataset()
        roi_contour.ReferencedROINumber = roi_number
        roi_contour.ROIDisplayColor = [255, 0, 0]
        contours = []
        for slice_index in range(mask.shape[0]):
            for polygon in find_contours(mask[slice_index].astype(np.uint8), 0.5):
                if len(polygon) < 3:
                    continue
                points = [
                    to_patient_point(
                        row,
                        col,
                        slice_index,
                        ipp,
                        row_cosine,
                        col_cosine,
                        pixel_spacing,
                        normal,
                        slice_spacing,
                    )
                    for row, col in polygon
                ]
                contour = Dataset()
                contour.ContourGeometricType = "CLOSED_PLANAR"
                contour.NumberOfContourPoints = len(points)
                contour.ContourData = [value for point in points for value in point]
                contour.ContourImageSequence = Sequence([contour_images[slice_index]])
                contours.append(contour)
        roi_contour.ContourSequence = Sequence(contours)
        contour_items.append(roi_contour)

    ds.StructureSetROISequence = Sequence(roi_items)
    ds.ROIContourSequence = Sequence(contour_items)
    ds.save_as(str(output_path), write_like_original=False)


def main() -> None:
    args = parse_args()
    shape = tuple(args.shape)
    ct_slices, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing = load_ct(args.ct_dir)
    masks = load_masks(args.labels, shape, args.label_map)
    if len(ct_slices) != shape[0]:
        raise ValueError(f"CT slice count {len(ct_slices)} does not match label depth {shape[0]}")
    args.mask_output.parent.mkdir(parents=True, exist_ok=True)
    args.rtstruct_output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.mask_output, **masks)
    write_rtstruct(args.rtstruct_output, ct_slices, masks, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing)
    print(json.dumps({"synthetic_only": True, "approval_status": "UNAPPROVED", "structures": {name: int(mask.sum()) for name, mask in masks.items()}}, indent=2))


if __name__ == "__main__":
    main()
