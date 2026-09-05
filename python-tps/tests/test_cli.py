"""End-to-end command-line tests, including artifact tamper detection."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.cli import main
from pytps.plan import PlanRequest


def run(*argv: str) -> tuple[int, str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(list(argv))
    return code, buffer.getvalue()


SMALL_PHANTOM = ["--dimensions", "36", "30", "24", "--spacing", "8", "8", "8", "--noise", "0"]


class WorkflowTests(unittest.TestCase):
    """phantom -> template -> plan -> report -> verify, as documented."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory()
        root = Path(cls._temp.name)
        cls.case = root / "case.npz"
        cls.request = root / "request.json"
        cls.plan = root / "plan"

        code, _ = run("phantom", "--out", str(cls.case), *SMALL_PHANTOM)
        assert code == 0
        code, _ = run(
            "template", "--out", str(cls.request), "--case", str(cls.case),
            "--target", "PROSTATE", "--prescription", "60", "--fractions", "20",
            "--angles", "0", "90", "180", "270", "--bixel-width", "12",
        )
        assert code == 0
        payload = json.loads(cls.request.read_text(encoding="utf-8"))
        payload["optimizerOverrides"] = {"max_iterations": 60}
        cls.request.write_text(json.dumps(payload), encoding="utf-8")
        cls.plan_exit, cls.plan_output = run(
            "plan", "--case", str(cls.case), "--request", str(cls.request), "--out", str(cls.plan)
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def test_phantom_writes_a_loadable_case(self) -> None:
        self.assertTrue(self.case.exists())
        code, output = run("inspect", str(self.case))
        self.assertEqual(code, 0)
        summary = json.loads(output)
        self.assertEqual(summary["clinicalUsePermitted"], False)
        self.assertEqual(len(summary["ctDigest"]), 64)
        self.assertIn("PROSTATE", [item["name"] for item in summary["structures"]])

    def test_template_is_a_valid_request(self) -> None:
        request = PlanRequest.load(self.request)
        self.assertEqual(request.target, "PROSTATE")
        self.assertEqual(request.fractions, 20)
        self.assertEqual(request.optimizer.max_iterations, 60)
        self.assertGreater(len(request.objectives), 1)

    def test_template_carries_the_nonclinical_notice(self) -> None:
        payload = json.loads(self.request.read_text(encoding="utf-8"))
        self.assertIn("Nonclinical", payload["_notice"])
        self.assertIn("total-course", payload["_doseConvention"])

    def test_plan_writes_the_full_artifact(self) -> None:
        names = {item.name for item in self.plan.iterdir()}
        self.assertEqual(names, {"plan.json", "request.json", "dose.npz", "report.txt"})

    def test_plan_prints_the_report(self) -> None:
        self.assertIn("NOT FOR CLINICAL USE", self.plan_output)
        self.assertIn("DOSE-VOLUME METRICS", self.plan_output)

    def test_a_deliberately_short_run_exits_nonzero(self) -> None:
        """60 iterations cannot converge, and the exit code must say so."""
        self.assertEqual(self.plan_exit, 2)

    def test_report_command_reprints_the_saved_report(self) -> None:
        code, output = run("report", str(self.plan))
        self.assertEqual(code, 0)
        self.assertIn("PRESCRIPTION", output)

    def test_verify_passes_on_an_untouched_artifact(self) -> None:
        code, output = run("verify", str(self.plan), "--case", str(self.case))
        self.assertEqual(code, 0)
        self.assertIn("matches the plan's recorded case digests", output)
        self.assertIn("not an approval", output)

    def test_verify_detects_a_tampered_dose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "plan"
            copy.mkdir()
            for item in self.plan.iterdir():
                copy.joinpath(item.name).write_bytes(item.read_bytes())
            with np.load(copy / "dose.npz", allow_pickle=False) as payload:
                fields = {key: payload[key] for key in payload.files}
            fields["dose"] = fields["dose"] * 1.10  # a 10% "improvement"
            np.savez_compressed(copy / "dose.npz", **fields)
            code, _ = run("verify", str(copy))
        self.assertEqual(code, 1)

    def test_verify_detects_a_case_that_is_not_the_planned_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            other = Path(directory) / "other.npz"
            # Same geometry, different CT noise: only the pixel data differs.
            run("phantom", "--out", str(other), *SMALL_PHANTOM, "--seed", "999", "--noise", "20")
            code, _ = run("verify", str(self.plan), "--case", str(other))
        self.assertEqual(code, 1)

    def test_plan_json_records_the_boundary(self) -> None:
        plan = json.loads((self.plan / "plan.json").read_text(encoding="utf-8"))
        self.assertFalse(plan["clinicalUsePermitted"])
        self.assertIn("not approved", plan["status"])
        self.assertIsNone(plan["dose"]["absoluteCalibration"])
        self.assertEqual(plan["request"]["doseConvention"], "total-course physical Gy")


class CommandErrorTests(unittest.TestCase):
    def test_missing_case_is_reported_not_raised(self) -> None:
        code, _ = run("inspect", "no-such-case.npz")
        self.assertEqual(code, 1)

    def test_plan_without_a_request_or_inline_options_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            case = Path(directory) / "case.npz"
            run("phantom", "--out", str(case), *SMALL_PHANTOM)
            with self.assertRaises(SystemExit):
                run("plan", "--case", str(case), "--out", str(Path(directory) / "plan"))

    def test_verify_without_a_plan_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(SystemExit):
                run("verify", directory)

    def test_unknown_command_exits(self) -> None:
        with self.assertRaises(SystemExit):
            main(["not-a-command"])


class SelfTestCommandTests(unittest.TestCase):
    def test_selftest_passes(self) -> None:
        code, output = run("selftest")
        self.assertEqual(code, 0)
        self.assertIn("PASS", output)


if __name__ == "__main__":
    unittest.main()
