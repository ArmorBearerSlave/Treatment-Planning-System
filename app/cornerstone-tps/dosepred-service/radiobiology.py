"""Exploratory dose-to-outcome calculations for synthetic prostate studies.

This module does not infer clinical outcomes. It applies explicitly supplied
radiobiology parameters to a physical dose array and named masks. Parameters
must be calibrated for the intended endpoint before interpretation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np



def lq_survival(dose_gy: np.ndarray, alpha_per_gy: float, beta_per_gy2: float, rbe: float = 1.0) -> np.ndarray:
    """Return single-fraction surviving fraction using the LQ model."""
    if alpha_per_gy < 0 or beta_per_gy2 < 0 or rbe <= 0:
        raise ValueError("alpha, beta must be nonnegative and RBE must be positive")
    biologic_dose = np.asarray(dose_gy, dtype=np.float64) * rbe
    return np.exp(-(alpha_per_gy * biologic_dose + beta_per_gy2 * biologic_dose**2))



def cumulative_survival(
    dose_gy: np.ndarray,
    alpha_per_gy: float,
    beta_per_gy2: float,
    fractions: int,
    rbe: float = 1.0,
) -> np.ndarray:
    """Return survival after repeated identical fractions."""
    if fractions < 1:
        raise ValueError("fractions must be at least one")
    return lq_survival(dose_gy, alpha_per_gy, beta_per_gy2, rbe) ** fractions



def poisson_tcp(surviving_fraction: float, initial_clonogens: float) -> float:
    """Return Poisson TCP = exp(-expected surviving clonogens)."""
    if not 0 <= surviving_fraction <= 1 or initial_clonogens < 0:
        raise ValueError("survival must be in [0, 1] and clonogens nonnegative")
    return float(math.exp(-initial_clonogens * surviving_fraction))



def equivalent_uniform_dose(dose_gy: np.ndarray, mask: np.ndarray, exponent: float) -> float:
    """Return generalized EUD for a masked dose distribution."""
    values = np.asarray(dose_gy, dtype=np.float64)[np.asarray(mask, dtype=bool)]
    if values.size == 0:
        raise ValueError("mask contains no dose voxels")
    if exponent == 0:
        return float(np.exp(np.mean(np.log(np.maximum(values, 1e-12)))))
    return float(np.mean(np.maximum(values, 0) ** exponent) ** (1.0 / exponent))


def normalize_dose(dose_gy: np.ndarray, normalization: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    """Normalize raw Monte Carlo output using an explicit prescription policy."""
    mode = normalization.get("mode")
    prescription_gy = float(normalization.get("prescription_gy", 0.0))
    if mode != "peak_to_prescription":
        raise ValueError("normalization.mode must be peak_to_prescription")
    if prescription_gy <= 0:
        raise ValueError("normalization.prescription_gy must be positive")
    raw_peak = float(np.max(dose_gy))
    if raw_peak <= 0:
        raise ValueError("raw dose must have a positive peak")
    scale_factor = prescription_gy / raw_peak
    return np.asarray(dose_gy, dtype=np.float64) * scale_factor, {
        "mode": mode,
        "prescription_gy": prescription_gy,
        "raw_peak_gy": raw_peak,
        "scale_factor": scale_factor,
    }



def lkb_ntcp(eud_gy: float, td50_gy: float, m: float, n: float) -> float:
    """Return Lyman-Kutcher-Burman NTCP from an EUD."""
    if td50_gy <= 0 or m <= 0 or n <= 0:
        raise ValueError("TD50, m, and n must be positive")
    t = (eud_gy - td50_gy) / (m * td50_gy)
    return float(0.5 * (1.0 + math.erf(t / math.sqrt(2.0))))



def analyze_case(dose_gy: np.ndarray, masks: dict[str, np.ndarray], config: dict[str, Any]) -> dict[str, Any]:
    """Calculate configured exploratory tumor and OAR endpoints."""
    dose = np.asarray(dose_gy, dtype=np.float64)
    dose, normalization = normalize_dose(dose, config["normalization"])
    if not masks:
        raise ValueError("at least one named mask is required")
    mask_shape = next(iter(masks.values())).shape
    if dose.shape != mask_shape:
        if dose.shape == mask_shape[::-1]:
            dose = np.transpose(dose, (2, 1, 0))
        else:
            raise ValueError(f"dose shape {dose.shape} does not match mask shape {mask_shape}")
    if any(np.asarray(mask).shape != mask_shape for mask in masks.values()):
        raise ValueError("all masks must have the same shape")
    tumor = config["tumor"]
    rbe = float(tumor.get("rbe", 1.0))
    tumor_values = dose[np.asarray(masks[tumor["mask"]], dtype=bool)]
    if tumor_values.size == 0:
        raise ValueError("tumor mask contains no dose voxels")
    fraction_dose = tumor_values / int(config["fractions"])
    tumor_sf = cumulative_survival(
        fraction_dose,
        float(tumor["alpha_per_gy"]),
        float(tumor["beta_per_gy2"]),
        int(config["fractions"]),
        rbe,
    )
    mean_tumor_sf = float(np.mean(tumor_sf))
    result: dict[str, Any] = {
        "status": "exploratory_synthetic_only",
        "endpoint_claim": "not_clinical_cancer_kill_or_tumor_control",
        "fractions": int(config["fractions"]),
        "normalization": normalization,
        "rbe_policy": tumor.get("rbe_policy", "explicit_fixed_assumption"),
        "tumor": {
            "mask": tumor["mask"],
            "voxel_count": int(tumor_values.size),
            "mean_dose_gy": float(np.mean(tumor_values)),
            "max_dose_gy": float(np.max(tumor_values)),
            "fraction_dose_gy": float(np.mean(fraction_dose)),
            "mean_surviving_fraction": mean_tumor_sf,
            "tcp": poisson_tcp(mean_tumor_sf, float(tumor["initial_clonogens"])),
        },
        "oars": {},
    }
    for name, oar in config.get("oars", {}).items():
        mask = np.asarray(masks[oar["mask"]], dtype=bool)
        values = dose[mask]
        if values.size == 0:
            raise ValueError(f"OAR mask contains no dose voxels: {name}")
        eud = equivalent_uniform_dose(dose, mask, float(oar["volume_exponent_n"]))
        result["oars"][name] = {
            "mask": oar["mask"],
            "voxel_count": int(values.size),
            "mean_dose_gy": float(np.mean(values)),
            "max_dose_gy": float(np.max(values)),
            "eud_gy": eud,
            "ntcp": lkb_ntcp(eud, float(oar["td50_gy"]), float(oar["m"]), float(oar["volume_exponent_n"])),
        }
    return result



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dose", type=Path, required=True, help=".npy dose array in Gy")
    parser.add_argument("--masks", type=Path, required=True, help=".npz named masks")
    parser.add_argument("--config", type=Path, required=True, help="JSON radiobiology parameters")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    masks_archive = np.load(args.masks)
    masks = {name: masks_archive[name] for name in masks_archive.files}
    result = analyze_case(np.load(args.dose), masks, json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
