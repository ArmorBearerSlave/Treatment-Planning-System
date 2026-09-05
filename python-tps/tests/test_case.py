from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.case import PlanningCase, Structure
from pytps.geometry import GeometryError, Grid
from pytps.phantom import build_phantom_case


def tiny_case(**overrides) -> PlanningCase:
    grid = Grid((4, 4, 2), (2.0, 2.0, 4.0), (0.0, 0.0, 0.0))
    ct = np.zeros(grid.dimensions, dtype=np.float32)
    labels = np.zeros(grid.dimensions, dtype=np.int16)
    labels[1:3, 1:3, :] = 1
    payload = {
        "case_id": "TINY",
        "grid": grid,
        "ct_hu": ct,
        "labels": labels,
        "structures": [Structure(1, "PTV")],
    }
    payload.update(overrides)
    return PlanningCase(**payload)


class CaseValidationTests(unittest.TestCase):
    def test_rejects_array_shape_mismatch(self) -> None:
        with self.assertRaises(GeometryError):
            tiny_case(ct_hu=np.zeros((2, 2, 2), dtype=np.float32))

    def test_refuses_a_case_marked_for_clinical_use(self) -> None:
        with self.assertRaises(ValueError) as caught:
            tiny_case(clinical_use_permitted=True)
        self.assertIn("clinical", str(caught.exception))

    def test_rejects_duplicate_structure_labels(self) -> None:
        with self.assertRaises(ValueError):
            tiny_case(structures=[Structure(1, "A"), Structure(1, "B")])

    def test_unknown_structure_error_lists_what_exists(self) -> None:
        case = tiny_case()
        with self.assertRaises(KeyError) as caught:
            case.mask("BLADDER")
        self.assertIn("PTV", str(caught.exception))

    def test_structure_lookup_is_case_insensitive(self) -> None:
        self.assertEqual(tiny_case().structure_by_name("ptv").label, 1)


class CaseDerivedDataTests(unittest.TestCase):
    def test_volume_matches_voxel_count(self) -> None:
        case = tiny_case()
        self.assertEqual(int(case.mask("PTV").sum()), 8)
        self.assertAlmostEqual(case.structure_volume_cm3("PTV"), 8 * 16.0 / 1000.0, places=6)

    def test_density_is_derived_from_hu_and_cached(self) -> None:
        case = tiny_case()
        first = case.density()
        self.assertAlmostEqual(float(first.mean()), 1.0, places=3)
        self.assertIs(case.density(), first)


class NpzRoundTripTests(unittest.TestCase):
    def test_round_trip_preserves_everything(self) -> None:
        original = build_phantom_case(dimensions=(24, 20, 16), spacing=(8.0, 8.0, 8.0), noise_hu=3.0)
        with tempfile.TemporaryDirectory() as directory:
            path = original.save_npz(Path(directory) / "case.npz")
            restored = PlanningCase.load(path)
        self.assertEqual(restored.case_id, original.case_id)
        self.assertEqual(restored.grid, original.grid)
        self.assertTrue(np.array_equal(restored.ct_hu, original.ct_hu))
        self.assertTrue(np.array_equal(restored.labels, original.labels))
        self.assertEqual(
            [item.name for item in restored.structures], [item.name for item in original.structures]
        )
        self.assertEqual(restored.provenance["seed"], original.provenance["seed"])

    def test_unknown_extension_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.dcm"
            path.write_bytes(b"not a case")
            with self.assertRaises(ValueError):
                PlanningCase.load(path)

    def test_missing_file_is_reported(self) -> None:
        with self.assertRaises(FileNotFoundError):
            PlanningCase.load("does-not-exist.npz")


class PhantomCaseJsonTests(unittest.TestCase):
    """The interoperability reader for the repository's PhantomCase contract."""

    def _payload(self, **overrides) -> dict:
        grid = {
            "dimensions": [2, 2, 2],
            "spacing": [1.0, 1.0, 1.0],
            "origin": [0.0, 0.0, 0.0],
            "direction": [1, 0, 0, 0, 1, 0, 0, 0, 1],
            "frameID": "F",
        }
        # X-fastest XYZ ordering, as the contract specifies.
        payload = {
            "schemaVersion": 1,
            "id": "EXT-001",
            "name": "external",
            "syntheticOnly": True,
            "clinicalUsePermitted": False,
            "ct": {"grid": grid, "modality": "CT", "units": "HU", "values": [0, 1, 2, 3, 4, 5, 6, 7]},
            "truth": {
                "grid": grid,
                "modality": "LABEL",
                "units": "label",
                "values": [0, 0, 0, 0, 1, 1, 1, 1],
            },
            "structures": [{"id": 1, "name": "PTV", "color": [1, 0, 0]}],
        }
        payload.update(overrides)
        return payload

    def _write(self, directory: str, payload: dict) -> Path:
        path = Path(directory) / "case.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_reads_x_fastest_values_into_the_right_voxels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            case = PlanningCase.load(self._write(directory, self._payload()))
        self.assertEqual(case.case_id, "EXT-001")
        self.assertEqual(float(case.ct_hu[1, 0, 0]), 1.0)  # x fastest
        self.assertEqual(float(case.ct_hu[0, 1, 0]), 2.0)  # then y
        self.assertEqual(float(case.ct_hu[0, 0, 1]), 4.0)  # then z
        self.assertEqual(int(case.labels[0, 0, 1]), 1)
        self.assertEqual(case.structures[0].name, "PTV")

    def test_refuses_a_case_permitted_for_clinical_use(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._write(directory, self._payload(clinicalUsePermitted=True))
            with self.assertRaises(ValueError):
                PlanningCase.load(path)

    def test_refuses_a_case_not_marked_synthetic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._write(directory, self._payload(syntheticOnly=False))
            with self.assertRaises(ValueError):
                PlanningCase.load(path)

    def test_rejects_non_hounsfield_ct_units(self) -> None:
        payload = self._payload()
        payload["ct"]["units"] = "arbitrary"
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                PlanningCase.load(self._write(directory, payload))

    def test_rejects_a_truth_volume_on_a_different_grid(self) -> None:
        payload = self._payload()
        payload["truth"]["grid"] = {**payload["truth"]["grid"], "spacing": [2.0, 1.0, 1.0]}
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(GeometryError):
                PlanningCase.load(self._write(directory, payload))

    def test_rejects_an_oblique_grid(self) -> None:
        payload = self._payload()
        payload["ct"]["grid"]["direction"] = [0, 1, 0, -1, 0, 0, 0, 0, 1]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(GeometryError):
                PlanningCase.load(self._write(directory, payload))


class PhantomTests(unittest.TestCase):
    def test_is_deterministic_for_a_seed(self) -> None:
        a = build_phantom_case(noise_hu=10.0, seed=42, dimensions=(24, 20, 16), spacing=(8.0, 8.0, 8.0))
        b = build_phantom_case(noise_hu=10.0, seed=42, dimensions=(24, 20, 16), spacing=(8.0, 8.0, 8.0))
        self.assertTrue(np.array_equal(a.ct_hu, b.ct_hu))

    def test_different_seeds_differ(self) -> None:
        a = build_phantom_case(noise_hu=10.0, seed=1, dimensions=(24, 20, 16), spacing=(8.0, 8.0, 8.0))
        b = build_phantom_case(noise_hu=10.0, seed=2, dimensions=(24, 20, 16), spacing=(8.0, 8.0, 8.0))
        self.assertFalse(np.array_equal(a.ct_hu, b.ct_hu))

    def test_is_flagged_synthetic_and_nonclinical(self) -> None:
        case = build_phantom_case(dimensions=(24, 20, 16), spacing=(8.0, 8.0, 8.0))
        self.assertTrue(case.synthetic_only)
        self.assertFalse(case.clinical_use_permitted)

    def test_all_structures_are_present_and_disjoint(self) -> None:
        case = build_phantom_case(dimensions=(36, 30, 24), spacing=(6.0, 6.0, 6.0))
        names = [structure.name for structure in case.structures]
        self.assertIn("PROSTATE", names)
        total = sum(int(case.mask(name).sum()) for name in names)
        self.assertEqual(total, int((case.labels != 0).sum()))

    def test_air_surrounds_the_body(self) -> None:
        case = build_phantom_case(dimensions=(36, 30, 24), spacing=(6.0, 6.0, 6.0), noise_hu=0.0)
        outside = case.labels == 0
        self.assertLess(float(case.ct_hu[outside].max()), -500.0)

    def test_too_small_a_grid_is_rejected_with_guidance(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_phantom_case(dimensions=(8, 8, 6), spacing=(4.0, 4.0, 4.0))
        self.assertIn("too small", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
