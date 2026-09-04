"""Auto-segmentation inference service for the NL-TPS Cornerstone3D viewer.

Runs TotalSegmentator (an existing, published open-source CT segmentation
tool -- not an NL-TPS-authored or validated model) against an uploaded CT
DICOM series and returns per-structure contour polygons in DICOM patient
(LPS) coordinates, in the same shape the viewer already uses for RTSTRUCT
contour geometry.

This is a technical feasibility spike, not a clinical component: results
are unreviewed, unverified, and must be presented to the user as an
AI-generated proposal requiring explicit human review -- never merged
with or presented as equivalent to a real, clinician-authored RTSTRUCT.
"""

import glob
import os
import subprocess
import tempfile

import nibabel as nib
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from skimage import measure

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Deterministic per-structure color assignment (cycled by output order),
# purely cosmetic -- not derived from any clinical significance ranking.
PALETTE = [
    [255, 99, 71], [70, 130, 180], [60, 179, 113], [238, 130, 238],
    [255, 215, 0], [255, 140, 0], [123, 104, 238], [0, 206, 209],
]

# Skip structures TotalSegmentator predicted with only a handful of
# voxels -- these are almost always noise on this kind of input, not a
# real finding, and would just clutter the proposal with junk contours.
MIN_VOXELS = 30


def mask_to_contours(data: np.ndarray, affine: np.ndarray) -> list[list[list[float]]]:
    """Extract per-slice polygon contours from a label mask, in DICOM LPS mm.

    Uses the NIfTI affine (computed by dicom2nifti from the original DICOM
    geometry) rather than a hand-rolled DICOM row/column-cosine formula --
    it is already-validated software, and RAS->LPS is just a sign flip on
    the first two axes, which is far less error-prone than re-deriving the
    DICOM Image Orientation (Patient)/Pixel Spacing conversion from scratch.
    """
    contours: list[list[list[float]]] = []
    for s in range(data.shape[2]):
        sl = data[:, :, s]
        if not sl.any():
            continue
        for contour in measure.find_contours(sl.astype(np.float32), 0.5):
            points: list[list[float]] = []
            # Decimate (every 2nd point) -- marching squares already gives
            # a smooth, dense point set; the browser doesn't need all of it.
            for a0, a1 in contour[::2]:
                ras = affine @ np.array([a0, a1, s, 1.0])
                points.append([-ras[0], -ras[1], ras[2]])
            if len(points) >= 3:
                contours.append(points)
    return contours


@app.post("/segment")
async def segment(files: list[UploadFile] = File(...)) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        dicom_dir = os.path.join(tmpdir, "dicom")
        os.makedirs(dicom_dir)
        for f in files:
            content = await f.read()
            with open(os.path.join(dicom_dir, f.filename or f"slice_{len(os.listdir(dicom_dir))}.dcm"), "wb") as out:
                out.write(content)

        out_dir = os.path.join(tmpdir, "out")
        subprocess.run(
            ["TotalSegmentator", "-i", dicom_dir, "-o", out_dir, "-d", "gpu"],
            check=True,
            capture_output=True,
        )

        rois = []
        for i, path in enumerate(sorted(glob.glob(os.path.join(out_dir, "*.nii.gz")))):
            name = os.path.basename(path).removesuffix(".nii.gz")
            img = nib.load(path)
            data = np.asarray(img.dataobj)
            if np.count_nonzero(data) < MIN_VOXELS:
                continue
            contours = mask_to_contours(data, img.affine)
            if contours:
                rois.append({"name": name, "color": PALETTE[i % len(PALETTE)], "contours": contours})

        return {"rois": rois, "model": "TotalSegmentator", "unverified": True}
