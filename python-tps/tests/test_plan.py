from __future__ import annotations

import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.dose import PencilBeamSettings
from pytps.optimize import OptimizerSettings
from pytps.phantom import build_phantom_case
from pytps.plan import PlanRequest, PlanRequestError, default_objectives, run_plan, target_centroid

SMALL = {"dimensions": (36, 30, 24), "spacing": (8.0, 8.0, 8.0), "noise_hu": 0.0}
FAST = OptimizerSettings(max_iterations=60)


def small_request(**overrides) -> PlanRequest:
    payload = {
        "target": "PROSTATE",
        "prescription_gy": 60.0,
        "fractions": 20,
        "gantry_angles": (0.0, 90.0, 180.0, 270.0),
        "bixel_width_mm": 12.0,
        "field_margin_mm": 10.0,
        "optimizer": FAST,
        "plan_label": "unit test",
    }
    payload.update(overrides)
    return PlanRequest(**payload)


class RequestValidationTests(unittest.TestCase):
    def test_rejects_impossible_prescriptions(self) -> None:
        for overrides in (
            {"prescription_gy": 0.0},
            {"prescription_gy": -10.0},
            {"prescription_gy": 5000.0},
            {"fractions": 0},
            {"target": "  "},
            {"field_margin_mm": -1.0},
        ):
            with self.assertRaises(PlanRequestError, msg=str(overrides)):
                small_request(**overrides)

    def test_per_fraction_dose_is_derived_not_stored(self) -> None:
        request = small_request(prescription_gy=60.0, fractions=20)
        self.assertAlmostEqual(request.dose_per_fraction_gy, 3.0, places=6)
        self.assertEqual(request.to_dict()["doseConvention"], "total-course physical Gy")

    def test_serialisation_round_trip_preserves_the_digest(self) -> None:
        request = small_request(prescription_gy=54.0, fractions=18)
        restored = PlanRequest.from_dict(request.to_dict())
        self.assertEqual(restored.digest(), request.digest())

    def test_digest_changes_when_anything_meaningful_changes(self) -> None:
        base = small_request()
        self.assertNotEqual(base.digest(), replace(base, prescription_gy=61.0).digest())
        self.assertNotEqual(base.digest(), replace(base, gantry_angles=(0.0, 180.0)).digest())
        self.assertNotEqual(
            base.digest(), replace(base, kernel=PencilBeamSettings(mu_per_mm=0.006)).digest()
        )

    def test_unknown_overrides_are_rejected_rather_than_ignored(self) -> None:
        payload = small_request().to_dict()
        payload["kernelOverrides"] = {"not_a_setting": 1.0}
        with self.assertRaises(PlanRequestError):
            PlanRequest.from_dict(payload)

    def test_unsupported_request_version_is_rejected(self) -> None:
        payload = small_request().to_dict()
        payload["requestVersion"] = 99
        with self.assertRaises(PlanRequestError):
            PlanRequest.from_dict(payload)


class PlanRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case = build_phantom_case(**SMALL)
        cls.result = run_plan(cls.case, small_request())

    def test_target_receives_close_to_the_prescription(self) -> None:
        mean = self.result.dvhs["PROSTATE"].metrics["meanGy"]
        self.assertAlmostEqual(mean, 60.0, delta=6.0)

    def test_target_is_hotter_than_every_organ(self) -> None:
        target_mean = self.result.dvhs["PROSTATE"].metrics["meanGy"]
        for name in ("BLADDER", "RECTUM", "FEMUR_L", "FEMUR_R"):
            self.assertLess(self.result.dvhs[name].metrics["meanGy"], target_mean)

    def test_dose_is_nonnegative_and_finite(self) -> None:
        self.assertGreaterEqual(float(self.result.dose.min()), 0.0)
        self.assertTrue(np.all(np.isfinite(self.result.dose)))

    def test_air_outside_the_patient_stays_cold(self) -> None:
        outside = self.case.labels == 0
        inside_peak = float(self.result.dose_volume[self.case.labels != 0].max())
        self.assertLess(float(self.result.dose_volume[outside].max()), 0.6 * inside_peak)

    def test_isocentre_defaults_to_the_target_centroid(self) -> None:
        expected = target_centroid(self.case, "PROSTATE")
        self.assertTrue(np.allclose(self.result.request.isocenter, expected, atol=1e-3))

    def test_every_structure_gets_a_dvh(self) -> None:
        self.assertEqual(
            set(self.result.dvhs), {structure.name for structure in self.case.structures}
        )

    def test_provenance_records_the_inputs_and_the_boundary(self) -> None:
        provenance = self.result.provenance
        self.assertEqual(provenance["clinicalUsePermitted"], False)
        self.assertEqual(provenance["approvalState"], "none")
        self.assertEqual(provenance["verificationState"], "not_verified")
        self.assertEqual(len(provenance["inputs"]["caseCTDigest"]), 64)
        self.assertIn("combined", provenance["engineSource"])

    def test_a_short_optimiser_run_is_reported_as_not_converged(self) -> None:
        self.assertFalse(self.result.optimization.converged)
        self.assertTrue(any("optimiser stopped" in warning for warning in self.result.warnings))

    def test_summary_is_json_serialisable(self) -> None:
        text = json.dumps(self.result.summary())
        self.assertIn("clinicalUsePermitted", text)
        self.assertIn("total-course physical Gy", text)


class PlanRejectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = build_phantom_case(**SMALL)

    def test_unknown_target_lists_the_available_structures(self) -> None:
        with self.assertRaises(PlanRequestError) as caught:
            run_plan(self.case, small_request(target="GTV_NODES"))
        self.assertIn("PROSTATE", str(caught.exception))

    def test_objectives_on_unknown_structures_are_rejected(self) -> None:
        from pytps.objectives import MaxDose, TargetDose

        request = small_request(
            objectives=(TargetDose("PROSTATE", 100.0, 60.0), MaxDose("LIVER", 10.0, 20.0))
        )
        with self.assertRaises(PlanRequestError) as caught:
            run_plan(self.case, request)
        self.assertIn("LIVER", str(caught.exception))

    def test_missing_objectives_are_defaulted_and_flagged(self) -> None:
        result = run_plan(self.case, small_request())
        self.assertTrue(result.request.objectives_were_defaulted)
        self.assertTrue(any("placeholder" in warning for warning in result.warnings))

    def test_default_objectives_cover_the_named_organs(self) -> None:
        objectives = default_objectives(self.case, "PROSTATE", 60.0)
        structures = {objective.structure for objective in objectives}
        self.assertEqual(structures, {"PROSTATE", "BLADDER", "RECTUM", "FEMUR_L", "FEMUR_R", "BODY"})
        target = next(item for item in objectives if item.structure == "PROSTATE")
        self.assertAlmostEqual(target.dose_gy, 60.0)


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case = build_phantom_case(**SMALL)
        cls.result = run_plan(cls.case, small_request())

    def test_saved_artifact_contains_every_expected_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.result.save(Path(directory) / "plan")
            names = {item.name for item in path.iterdir()}
        self.assertEqual(names, {"plan.json", "request.json", "dose.npz", "report.txt"})

    def test_saved_dose_matches_the_recorded_digest(self) -> None:
        from pytps.provenance import sha256_array

        with tempfile.TemporaryDirectory() as directory:
            path = self.result.save(Path(directory) / "plan")
            plan = json.loads((path / "plan.json").read_text(encoding="utf-8"))
            with np.load(path / "dose.npz", allow_pickle=False) as payload:
                dose = payload["dose"]
        self.assertEqual(sha256_array(dose.reshape(-1)), plan["dose"]["digest"])
        self.assertEqual(tuple(dose.shape), self.case.grid.dimensions)

    def test_report_states_the_boundary_and_the_dose_convention(self) -> None:
        report = self.result.save(Path(tempfile.mkdtemp()) / "plan") / "report.txt"
        text = report.read_text(encoding="utf-8")
        self.assertIn("NOT FOR CLINICAL USE", text)
        self.assertIn("total-course physical Gy", text)
        self.assertIn("LIMITATIONS", text)
        self.assertIn("PROSTATE", text)


if __name__ == "__main__":
    unittest.main()
