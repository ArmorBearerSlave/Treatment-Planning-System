"""Inference service for the AI dose-prediction feasibility spike.
Accepts an uploaded CT DICOM series + RTSTRUCT, rasterizes the same 8
ROIs used in training, runs the trained 3D U-Net, and returns the
predicted dose as a raw float32 binary buffer in the CT volume's native
voxel order (frame, row, col) -- matching Cornerstone3D's own scalar
data layout, so the browser can load it directly into a derived volume
with no further coordinate transform.

This is a technical feasibility spike, not a clinical component: trained
on only 10 synthetic XCAT cases (severely small for deep learning), and
the prediction must be presented as an unreviewed, unverified proposal.
"""

import io
import os
import tempfile

import numpy as np
import pydicom
import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from model import DosePredictionUNet
from prepare_training_data import load_ct_volume, rasterize_structures

CHECKPOINT_PATH = os.path.expanduser("~/nl-tps-autoseg/dosepred-service/dose_model.pt")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = DosePredictionUNet(in_channels=_checkpoint["in_channels"], base_channels=_checkpoint["base_channels"])
_model.load_state_dict(_checkpoint["state_dict"])
_model.to(_device).eval()


@app.post("/predict_dose")
async def predict_dose(ct_files: list[UploadFile] = File(...), rtstruct_file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        ct_dir = os.path.join(tmpdir, "ct")
        os.makedirs(ct_dir)
        for f in ct_files:
            content = await f.read()
            with open(os.path.join(ct_dir, f.filename or f"slice_{len(os.listdir(ct_dir))}.dcm"), "wb") as out:
                out.write(content)
        rtstruct_bytes = await rtstruct_file.read()

        ct, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing = load_ct_volume(ct_dir)
        rtstruct_path = os.path.join(tmpdir, "RTSTRUCT.dcm")
        with open(rtstruct_path, "wb") as out:
            out.write(rtstruct_bytes)
        structures = rasterize_structures(
            rtstruct_path, ct.shape, ipp, row_cosine, col_cosine, pixel_spacing, slice_spacing
        )

    pad_hw = _checkpoint["pad_hw"]
    ct_clip = _checkpoint["ct_clip"]
    max_dose_gy = _checkpoint["max_dose_gy"]

    ct_norm = np.clip(ct, *ct_clip)
    ct_norm = (ct_norm - ct_clip[0]) / (ct_clip[1] - ct_clip[0])
    ct_padded = np.pad(ct_norm, ((0, 0), pad_hw, pad_hw))
    structures_padded = np.pad(structures.astype(np.float32), ((0, 0), (0, 0), pad_hw, pad_hw))

    x = np.concatenate([ct_padded[None, ...], structures_padded], axis=0)
    x = torch.from_numpy(x).float().unsqueeze(0).to(_device)

    with torch.no_grad():
        pred = _model(x).squeeze(0).squeeze(0).cpu().numpy()

    h0, h1 = pad_hw[0], pred.shape[1] - pad_hw[1]
    w0, w1 = pad_hw[0], pred.shape[2] - pad_hw[1]
    pred = pred[:, h0:h1, w0:w1] * max_dose_gy
    pred = np.clip(pred, 0, None).astype(np.float32)

    return Response(content=pred.tobytes(), media_type="application/octet-stream")
