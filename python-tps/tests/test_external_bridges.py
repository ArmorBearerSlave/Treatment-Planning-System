"""The matRad and CERR bridges, exercised end to end against a MATLAB stand-in.

The stand-in (``fake_matlab.py``) implements the job contract but not the
science, so these tests cover what the bridge is responsible for: freezing and
hashing inputs, launching, binding a result back to those inputs, importing it,
and reconciling it. Verification of the real adapters is in ``docs/EXTERNAL.md``
and can only be done with MATLAB, matRad and CERR installed.
"""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.external import JobError
from pytps.external.cerr import (
    CerrSettings,
    export_job as export_cerr_job,
    reconcile,
    run_cerr_analysis,
    sampling_tolerance_gy_for,
)
from pytps.external.matrad import (
    MatRadSettings,
    check_objectives,
    export_job as export_matrad_job,
    prepare_request,
    run_matrad_plan,
)
from pytps.objectives import MaxDose, MeanDose, MinDose, TargetDose
from pytps.phantom import build_phantom_case
from pytps.plan import PlanRequest, PlanRequestError

HERE = Path(__file__).resolve().parent
SMALL = {"dimensions": (24, 20, 16), "spacing": (10.0, 10.0, 10.0), "noise_hu": 0.0}


def fake_matlab(directory: Path) -> Path:
    """A launcher that runs the stand-in with the current interpreter."""
    launcher = directory / "matlab"
    launcher.write_text(
        f'#!/bin/sh\nexec "{sys.executable}" "{HERE / "fake_matlab.py"}" "$@"\n', encoding="utf-8"
    )
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    return launcher


def fake_library(directory: Path, kind: str) -> Path:
    """A directory that passes the checkout marker test."""
    root = directory / kind
    root.mkdir(parents=True, exist_ok=True)
    (root / ("matRad_rc.m" if kind == "matrad" else "getCERRPath.m")).write_text("% fake\n")
    return root


def small_request(**overrides) -> PlanRequest:
    payload = {
        "target": "PROSTATE",
        "prescription_gy": 60.0,
        "fractions": 20,
        "gantry_angles": (0.0, 180.0),
        "bixel_width_mm": 15.0,
        "plan_label": "bridge test",
    }
    payload.update(overrides)
    return PlanRequest(**payload)


class ObjectiveMappingTests(unittest.TestCase):
    """matRad must express the objective identically, or not at all."""

    def test_the_three_squared_objectives_map(self) -> None:
        check_objectives(
            (
                TargetDose("PROSTATE", 100.0, 60.0),
                MaxDose("RECTUM", 20.0, 40.0),
                MinDose("PROSTATE", 10.0, 57.0),
            )
        )

    def test_mean_dose_is_refused_rather_than_approximated(self) -> None:
        with self.assertRaises(PlanRequestError) as caught:
            check_objectives((TargetDose("PROSTATE", 100.0, 60.0), MeanDose("RECTUM", 5.0, 20.0)))
        self.assertIn("mean-dose", str(caught.exception))
        self.assertIn("invalid", str(caught.exception))

    def test_a_target_objective_is_required(self) -> None:
        with self.assertRaises(PlanRequestError):
            check_objectives((MaxDose("RECTUM", 20.0, 40.0),))


class JobExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = build_phantom_case(**SMALL)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_matrad_job_carries_everything_the_adapter_reads(self) -> None:
        request = prepare_request(self.case, small_request())
        job = export_matrad_job(self.case, request, self.root, tools={"matlab": "fake"})
        names = {item.name for item in job.path.iterdir()}
        self.assertLessEqual(
            {
                "job.json",
                "source.json",
                "request.json",
                "ct.f32",
                "labels.i16",
                "pytps_matrad_plan.m",
                "pytps_filehash.m",
                "pytps_readvolume.m",
                "pytps_writejson.m",
            },
            names,
        )
        payload = json.loads(job.file("request.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["doseConvention"], "total-course physical Gy")
        self.assertEqual(len(payload["isocenterMM"]), 3)
        self.assertIn("maxIterations", payload)

    def test_the_adapter_that_will_run_is_copied_and_hashed(self) -> None:
        request = prepare_request(self.case, small_request())
        job = export_matrad_job(self.case, request, self.root, tools={})
        record = job.record()
        adapters = [entry for entry in record["inputs"] if entry["file"].endswith(".m")]
        self.assertEqual(len(adapters), 4)
        source = (
            Path(__file__).resolve().parents[1] / "src" / "pytps" / "matlab" / "pytps_matrad_plan.m"
        ).read_bytes()
        self.assertEqual(job.file("pytps_matrad_plan.m").read_bytes(), source)

    def test_cerr_job_includes_the_dose(self) -> None:
        dose = np.full(self.case.grid.dimensions, 2.0, dtype=np.float32)
        job = export_cerr_job(self.case, dose, self.root, tools={}, bin_width_gy=0.25)
        self.assertIn("dose.f32", {item.name for item in job.path.iterdir()})
        payload = json.loads(job.file("request.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["binWidthGy"], 0.25)

    def test_a_negative_dose_is_refused_before_export(self) -> None:
        dose = np.full(self.case.grid.dimensions, -1.0, dtype=np.float32)
        with self.assertRaises(JobError):
            export_cerr_job(self.case, dose, self.root, tools={})

    def test_the_target_must_exist(self) -> None:
        with self.assertRaises(PlanRequestError) as caught:
            prepare_request(self.case, small_request(target="GTV_NODES"))
        self.assertIn("PROSTATE", str(caught.exception))

    def test_missing_objectives_are_defaulted(self) -> None:
        request = prepare_request(self.case, small_request())
        self.assertTrue(request.objectives_were_defaulted)
        self.assertTrue(any(item.kind() == "target_dose" for item in request.objectives))


class BridgeRunTests(unittest.TestCase):
    """The whole path, with the stand-in standing in for MATLAB."""

    def setUp(self) -> None:
        self.case = build_phantom_case(**SMALL)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.settings = MatRadSettings(
            matlab=fake_matlab(self.root),
            library=fake_library(self.root, "matrad"),
            timeout_s=120,
        )
        os.environ.pop("PYTPS_FAKE_MATLAB", None)

    def tearDown(self) -> None:
        os.environ.pop("PYTPS_FAKE_MATLAB", None)
        self.temp.cleanup()

    def test_a_matrad_run_becomes_an_ordinary_plan_result(self) -> None:
        result, job = run_matrad_plan(self.case, small_request(), self.root / "jobs", self.settings)
        self.assertEqual(result.provider, "matrad")
        self.assertIsNone(result.influence)
        self.assertIsNone(result.optimization)
        self.assertTrue(result.converged)
        self.assertEqual(set(result.dvhs), {item.name for item in self.case.structures})
        self.assertEqual(result.dose.size, self.case.grid.voxel_count)
        self.assertTrue(job.file("exit-code.txt").exists())
        self.assertTrue(job.file("matlab.log").exists())

    def test_the_saved_artifact_names_its_provider_and_its_job(self) -> None:
        result, job = run_matrad_plan(self.case, small_request(), self.root / "jobs", self.settings)
        directory = result.save(self.root / "plan")
        summary = json.loads((directory / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["provider"], "matrad")
        self.assertIsNone(summary["influence"])
        self.assertEqual(summary["external"]["jobID"], job.path.name)
        self.assertFalse(summary["clinicalUsePermitted"])
        report = (directory / "report.txt").read_text(encoding="utf-8")
        self.assertIn("external code, run through a pytps bridge", report)
        self.assertIn("NOT FOR CLINICAL USE", report)

    def test_the_plan_warns_that_the_dose_came_from_elsewhere(self) -> None:
        result, _ = run_matrad_plan(self.case, small_request(), self.root / "jobs", self.settings)
        self.assertTrue(any("uncommissioned" in warning for warning in result.warnings))

    def test_a_failed_matlab_run_keeps_the_job_and_explains(self) -> None:
        os.environ["PYTPS_FAKE_MATLAB"] = "fail"
        with self.assertRaises(JobError) as caught:
            run_matrad_plan(self.case, small_request(), self.root / "jobs", self.settings)
        message = str(caught.exception)
        self.assertIn("Job retained at", message)
        self.assertIn("Last log lines", message)

    def test_a_nonconverged_run_is_not_importable(self) -> None:
        os.environ["PYTPS_FAKE_MATLAB"] = "nonconverged"
        with self.assertRaises(JobError):
            run_matrad_plan(self.case, small_request(), self.root / "jobs", self.settings)

    def test_a_result_that_does_not_bind_is_refused(self) -> None:
        os.environ["PYTPS_FAKE_MATLAB"] = "tamper"
        with self.assertRaises(JobError) as caught:
            run_matrad_plan(self.case, small_request(), self.root / "jobs", self.settings)
        self.assertIn("different inputs", str(caught.exception))

    def test_forward_mode_is_rejected_by_the_planning_entry_point(self) -> None:
        settings = MatRadSettings(
            matlab=self.settings.matlab, library=self.settings.library, mode="forward"
        )
        with self.assertRaises(PlanRequestError):
            run_matrad_plan(self.case, small_request(), self.root / "jobs", settings)

    def test_an_unknown_mode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MatRadSettings(mode="guess")


class CerrRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = build_phantom_case(**SMALL)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.dose = np.zeros(self.case.grid.dimensions, dtype=np.float32)
        self.dose[self.case.labels != 0] = 12.0
        self.dose[self.case.mask("PROSTATE")] = 60.0
        self.settings = CerrSettings(
            matlab=fake_matlab(self.root), library=fake_library(self.root, "cerr"), timeout_s=120
        )
        os.environ.pop("PYTPS_FAKE_MATLAB", None)

    def tearDown(self) -> None:
        os.environ.pop("PYTPS_FAKE_MATLAB", None)
        self.temp.cleanup()

    def test_matching_metrics_reconcile(self) -> None:
        analysis, _ = run_cerr_analysis(self.case, self.dose, self.root / "jobs", self.settings)
        self.assertTrue(analysis.sampling_is_voxel_exact)
        self.assertTrue(analysis.agrees)
        self.assertEqual(analysis.warnings, [])
        names = {item.structure for item in analysis.comparisons}
        self.assertEqual(names, {item.name for item in self.case.structures})

    def test_a_metric_disagreement_is_reported_as_a_definition_difference(self) -> None:
        os.environ["PYTPS_FAKE_MATLAB"] = "drift"
        analysis, _ = run_cerr_analysis(self.case, self.dose, self.root / "jobs", self.settings)
        self.assertTrue(analysis.sampling_is_voxel_exact)
        self.assertFalse(analysis.agrees)
        self.assertTrue(any("metric-definition difference" in item for item in analysis.warnings))

    def test_reconcile_uses_cerrs_own_dx_definition(self) -> None:
        """pytps must compare nearest-rank against nearest-rank, not against its
        interpolated DVH value, or every structure would look discrepant."""
        from pytps.dvh import nearest_rank_dose

        indices = np.flatnonzero(self.case.mask("PROSTATE").reshape(-1))
        values = self.dose.reshape(-1)[indices]
        record = {
            "name": "PROSTATE",
            "sampleCount": int(indices.size),
            "meanGy": float(values.mean()),
            "minGy": float(values.min()),
            "maxGy": float(values.max()),
            "maxSampleDifferenceGy": 0.0,
            "d95Gy": nearest_rank_dose(values, 0.95),
        }
        comparisons, warnings = reconcile(self.case, self.dose, [record], tolerance_gy=1e-6)
        self.assertEqual(warnings, [])
        self.assertAlmostEqual(comparisons[0].metrics["D95"]["difference"], 0.0, places=9)

    def test_a_voxel_count_mismatch_is_flagged_as_not_like_for_like(self) -> None:
        record = {
            "name": "PROSTATE",
            "sampleCount": 3,
            "meanGy": 60.0,
            "minGy": 60.0,
            "maxGy": 60.0,
            "maxSampleDifferenceGy": 0.0,
        }
        _, warnings = reconcile(self.case, self.dose, [record], tolerance_gy=1e-6)
        self.assertTrue(any("not like-for-like" in item for item in warnings))

    def test_a_sampling_difference_is_flagged_as_a_geometry_problem(self) -> None:
        record = {
            "name": "PROSTATE",
            "sampleCount": int(self.case.mask("PROSTATE").sum()),
            "meanGy": 60.0,
            "minGy": 60.0,
            "maxGy": 60.0,
            "maxSampleDifferenceGy": 0.5,
        }
        _, warnings = reconcile(self.case, self.dose, [record], tolerance_gy=1e-6)
        self.assertTrue(any("geometry" in item for item in warnings))

    def test_float32_round_trip_noise_is_not_a_geometry_problem(self) -> None:
        """A fixed absolute threshold passed at 60 Gy and failed at 80 Gy; the
        tolerable difference has to scale with the dose."""
        record = {
            "name": "PROSTATE",
            "sampleCount": int(self.case.mask("PROSTATE").sum()),
            "meanGy": float(self.dose[self.case.mask("PROSTATE")].mean()),
            "minGy": float(self.dose[self.case.mask("PROSTATE")].min()),
            "maxGy": float(self.dose[self.case.mask("PROSTATE")].max()),
            "maxSampleDifferenceGy": 1.3e-06,
        }
        _, warnings = reconcile(self.case, self.dose, [record], tolerance_gy=1e-3)
        self.assertEqual(warnings, [])

    def test_the_sampling_tolerance_tracks_the_dose_magnitude(self) -> None:
        small = sampling_tolerance_gy_for(np.array([1.0], dtype=np.float32))
        large = sampling_tolerance_gy_for(np.array([200.0], dtype=np.float32))
        self.assertGreater(large, small * 50)
        self.assertLess(large, 1e-3)

    def test_invalid_settings_are_rejected(self) -> None:
        for kwargs in ({"bin_width_gy": 0.0}, {"tolerance_gy": -1.0}):
            with self.assertRaises(ValueError):
                CerrSettings(**kwargs)


if __name__ == "__main__":
    unittest.main()
