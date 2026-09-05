"""Planning cases: a CT volume, a label volume, and a structure list.

Two on-disk forms are supported.

``.npz`` (native to this package)
    Fast, compact, and what :mod:`pytps.phantom` writes. Arrays are stored in
    ``(nx, ny, nz)`` order with a JSON metadata blob alongside them.

``.json`` (the PhantomCase contract also used elsewhere in this repository)
    Read-only interoperability. Values are X-fastest XYZ flat lists. These
    files are large; loading one is O(file size) in the JSON parser and can
    take tens of seconds.

Only synthetic or de-identified nonclinical data may be used. Nothing here
reads DICOM, and there is no patient-identity model on purpose.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .geometry import Grid, GeometryError
from .materials import hu_to_density

CASE_FORMAT_VERSION = 1


@dataclass(frozen=True)
class Structure:
    """One labelled region of interest."""

    label: int
    name: str
    color: tuple[float, float, float] = (0.8, 0.8, 0.8)

    def to_dict(self) -> dict[str, Any]:
        return {"id": int(self.label), "name": self.name, "color": list(self.color)}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Structure":
        color = payload.get("color") or (0.8, 0.8, 0.8)
        return cls(label=int(payload["id"]), name=str(payload["name"]), color=tuple(float(c) for c in color)[:3])


@dataclass
class PlanningCase:
    """A CT grid, its HU values, an integer label map, and structure names."""

    case_id: str
    grid: Grid
    ct_hu: np.ndarray
    labels: np.ndarray
    structures: list[Structure] = field(default_factory=list)
    name: str = ""
    synthetic_only: bool = True
    clinical_use_permitted: bool = False
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.ct_hu = np.ascontiguousarray(np.asarray(self.ct_hu, dtype=np.float32))
        self.labels = np.ascontiguousarray(np.asarray(self.labels, dtype=np.int16))
        if tuple(self.ct_hu.shape) != self.grid.dimensions:
            raise GeometryError(f"CT array {self.ct_hu.shape} does not match grid {self.grid.dimensions}")
        if tuple(self.labels.shape) != self.grid.dimensions:
            raise GeometryError(f"label array {self.labels.shape} does not match grid {self.grid.dimensions}")
        if self.clinical_use_permitted:
            raise ValueError("this package refuses cases flagged as permitted for clinical use")
        seen: set[int] = set()
        for structure in self.structures:
            if structure.label in seen:
                raise ValueError(f"duplicate structure label {structure.label}")
            seen.add(structure.label)

    # -- derived data -----------------------------------------------------
    def density(self) -> np.ndarray:
        """Relative mass density, cached on first use."""
        cached = getattr(self, "_density", None)
        if cached is None:
            cached = hu_to_density(self.ct_hu)
            self._density = cached
        return cached

    def structure_by_name(self, name: str) -> Structure:
        wanted = name.strip().casefold()
        for structure in self.structures:
            if structure.name.strip().casefold() == wanted:
                return structure
        available = ", ".join(sorted(item.name for item in self.structures)) or "(none)"
        raise KeyError(f"no structure named {name!r}; case defines: {available}")

    def mask(self, name: str) -> np.ndarray:
        """Boolean mask for a named structure."""
        return self.labels == np.int16(self.structure_by_name(name).label)

    def structure_volume_cm3(self, name: str) -> float:
        return float(np.count_nonzero(self.mask(name))) * self.grid.voxel_volume_cm3

    def summary(self) -> dict[str, Any]:
        return {
            "caseID": self.case_id,
            "name": self.name,
            "grid": self.grid.to_dict(),
            "voxels": self.grid.voxel_count,
            "syntheticOnly": self.synthetic_only,
            "clinicalUsePermitted": self.clinical_use_permitted,
            "structures": [
                {
                    "name": structure.name,
                    "label": structure.label,
                    "volumeCm3": round(self.structure_volume_cm3(structure.name), 3),
                }
                for structure in self.structures
            ],
        }

    # -- input/output -----------------------------------------------------
    def save_npz(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = {
            "formatVersion": CASE_FORMAT_VERSION,
            "caseID": self.case_id,
            "name": self.name,
            "grid": self.grid.to_dict(),
            "structures": [structure.to_dict() for structure in self.structures],
            "syntheticOnly": self.synthetic_only,
            "clinicalUsePermitted": self.clinical_use_permitted,
            "provenance": self.provenance,
        }
        np.savez_compressed(
            path, metadata=np.asarray(json.dumps(meta, sort_keys=True)), ct_hu=self.ct_hu, labels=self.labels
        )
        return path

    @classmethod
    def load(cls, path: str | Path) -> "PlanningCase":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"case file not found: {path}")
        if path.suffix.casefold() == ".npz":
            return cls._load_npz(path)
        if path.suffix.casefold() == ".json":
            return cls._load_phantom_case_json(path)
        raise ValueError(f"unsupported case format {path.suffix!r}; expected .npz or .json")

    @classmethod
    def _load_npz(cls, path: Path) -> "PlanningCase":
        with np.load(path, allow_pickle=False) as payload:
            meta = json.loads(str(payload["metadata"]))
            ct = payload["ct_hu"]
            labels = payload["labels"]
        version = int(meta.get("formatVersion", 0))
        if version != CASE_FORMAT_VERSION:
            raise ValueError(f"case format version {version} is not supported (expected {CASE_FORMAT_VERSION})")
        return cls(
            case_id=str(meta["caseID"]),
            grid=Grid.from_dict(meta["grid"]),
            ct_hu=ct,
            labels=labels,
            structures=[Structure.from_dict(item) for item in meta.get("structures", [])],
            name=str(meta.get("name", "")),
            synthetic_only=bool(meta.get("syntheticOnly", True)),
            clinical_use_permitted=bool(meta.get("clinicalUsePermitted", False)),
            provenance=dict(meta.get("provenance", {})),
        )

    @classmethod
    def _load_phantom_case_json(cls, path: Path) -> "PlanningCase":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if bool(payload.get("clinicalUsePermitted", False)):
            raise ValueError(f"{path.name} is flagged clinicalUsePermitted; this package refuses it")
        if not bool(payload.get("syntheticOnly", True)):
            raise ValueError(f"{path.name} is not flagged syntheticOnly; this package refuses it")
        if "ct" not in payload:
            raise ValueError(f"{path.name} has no 'ct' volume")
        ct_block = payload["ct"]
        grid = Grid.from_dict(ct_block["grid"])
        ct = grid.from_flat(ct_block["values"], dtype=np.float32)

        truth = payload.get("truth")
        if truth is None:
            labels = np.zeros(grid.dimensions, dtype=np.int16)
        else:
            truth_grid = Grid.from_dict(truth["grid"])
            grid.check_same_geometry(truth_grid, "CT vs truth label volume")
            labels = grid.from_flat(truth["values"], dtype=np.float32).round().astype(np.int16)

        units = str(ct_block.get("units", "")).casefold()
        if units and units not in {"hu", "hounsfield", "hounsfieldunits"}:
            raise ValueError(f"{path.name} CT units are {ct_block.get('units')!r}; expected Hounsfield units")

        return cls(
            case_id=str(payload.get("id", path.stem)),
            grid=grid,
            ct_hu=ct,
            labels=labels,
            structures=[Structure.from_dict(item) for item in payload.get("structures", [])],
            name=str(payload.get("name", "")),
            synthetic_only=True,
            clinical_use_permitted=False,
            provenance={
                "sourceFile": path.name,
                "generator": payload.get("generator"),
                "generatorVersion": payload.get("generatorVersion"),
                "intendedUse": payload.get("intendedUse"),
                "schemaVersion": payload.get("schemaVersion"),
            },
        )
