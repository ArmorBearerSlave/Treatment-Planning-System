"""Trains the small 3D dose-prediction U-Net on the ~10-case dataset built
by prepare_training_data.py. Severely data-limited by design (feasibility
spike, not a validated model) -- expect significant overfitting; this
exists to prove the pipeline/architecture, not to produce a clinically
meaningful predictor.
"""

import glob
import os

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from model import DosePredictionUNet

DATA_DIR = os.path.expanduser("~/nl-tps-autoseg/dosepred-data")
CHECKPOINT_PATH = os.path.expanduser("~/nl-tps-autoseg/dosepred-service/dose_model.pt")
# 96 is already divisible by 8 (3 downsampling levels); 180 is not, so pad
# H/W symmetrically to 184 (also divisible by 8) and crop back after.
PAD_HW = (2, 2)
CT_CLIP = (-1000.0, 1500.0)
MAX_DOSE_GY = 80.0


class DoseDataset(Dataset):
    def __init__(self, npz_paths):
        self.npz_paths = npz_paths

    def __len__(self):
        return len(self.npz_paths)

    def __getitem__(self, idx):
        data = np.load(self.npz_paths[idx])
        ct = np.clip(data["ct"], *CT_CLIP)
        ct = (ct - CT_CLIP[0]) / (CT_CLIP[1] - CT_CLIP[0])
        structures = data["structures"].astype(np.float32)
        dose = data["dose"].astype(np.float32) / MAX_DOSE_GY

        ct = np.pad(ct, ((0, 0), PAD_HW, PAD_HW))
        structures = np.pad(structures, ((0, 0), (0, 0), PAD_HW, PAD_HW))
        dose = np.pad(dose, ((0, 0), PAD_HW, PAD_HW))

        x = np.concatenate([ct[None, ...], structures], axis=0)
        y = dose[None, ...]
        return torch.from_numpy(x).float(), torch.from_numpy(y).float()


def main():
    npz_paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.npz")))
    print(f"Found {len(npz_paths)} cases")
    # Last 2 held out for a validation loss check; with only 10 cases this
    # is not a meaningful generalization estimate, just a sanity signal.
    train_paths, val_paths = npz_paths[:-2], npz_paths[-2:]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DosePredictionUNet(in_channels=9, base_channels=8).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    train_loader = DataLoader(DoseDataset(train_paths), batch_size=1, shuffle=True)
    val_loader = DataLoader(DoseDataset(val_paths), batch_size=1, shuffle=False)

    epochs = 60
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                pred = model(x)
                val_loss += loss_fn(pred, y).item()
        val_loss /= max(len(val_loader), 1)

        print(f"epoch {epoch + 1}/{epochs}  train_mse={train_loss:.5f}  val_mse={val_loss:.5f}")

    torch.save(
        {
            "state_dict": model.state_dict(),
            "in_channels": 9,
            "base_channels": 8,
            "pad_hw": PAD_HW,
            "ct_clip": CT_CLIP,
            "max_dose_gy": MAX_DOSE_GY,
            "roi_names": [
                "BODY", "PROSTATE_PROXY", "GTV_ANALYTIC", "PTV_ANALYTIC",
                "BLADDER_PROXY", "RECTUM_PROXY", "FEMORAL_HEAD_L_PROXY", "FEMORAL_HEAD_R_PROXY",
            ],
            "train_cases": [os.path.basename(p) for p in train_paths],
            "val_cases": [os.path.basename(p) for p in val_paths],
        },
        CHECKPOINT_PATH,
    )
    print(f"Saved checkpoint to {CHECKPOINT_PATH}")


if __name__ == "__main__":
    main()
