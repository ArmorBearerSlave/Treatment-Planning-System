"""MI-EXIT-01: a measurement-invalid state must not arrive as a substantive finding.

Two controlled instruments printed the words MEASUREMENT INVALID and nevertheless exited 1,
because `raise SystemExit("text")` prints the text and exits 1 -- Python reserves the integer
form for the status. The internal state was right and the externally observable verdict was
wrong, which is the F5-FU-02 shape: a correct conclusion corrupted on its way out of the
process.

The collapse matters because it merges the two states a reader most needs to tell apart:

    exit 1   the measurement was valid and found a substantive discrepancy
    exit 1   the measurement could not be established at all

report_assurance_metrics.py is the load-bearing case, because it is what validates the
headline assurance aggregates. "The asserted assurance state disagrees with its population"
and "I could not read the population" are not the same claim, and only the first is a finding
about the record.

Every control here invokes the real command line and observes the real process exit code.
A test that called an internal helper and asserted on an exception type would not have caught
this defect, because the defect lived precisely at the boundary those tests do not cross.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

MANIFEST = REPO_ROOT / "tools" / "mps" / "derived_manifest.py"
METRICS = REPO_ROOT / "tools" / "spec" / "report_assurance_metrics.py"
PROJECT = REPO_ROOT / "mps" / "NLTPSGovernance"
RELOCATION = REPO_ROOT / "spec" / "relocation_verification.yaml"

VALID = 0
SUBSTANTIVE_FINDING = 1
MEASUREMENT_INVALID = 2


def run(tool: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run([sys.executable, str(tool), *args],
                            capture_output=True, text=True, cwd=str(REPO_ROOT))
    return result.returncode, result.stdout + result.stderr


class TheLanguageSemanticsBeingRepaired(unittest.TestCase):

    def test_a_string_valued_system_exit_is_exit_1(self):
        """The mechanism of the defect, pinned so the repair cannot silently regress to it."""
        result = subprocess.run(
            [sys.executable, "-c", "raise SystemExit('MEASUREMENT INVALID: x')"],
            capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn("MEASUREMENT INVALID", result.stderr)

    def test_no_controlled_instrument_raises_system_exit_with_a_measurement_invalid_string(self):
        for tool in (MANIFEST, METRICS):
            source = tool.read_text(encoding="utf-8")
            self.assertNotIn('raise SystemExit(f"MEASUREMENT INVALID', source, tool.name)
            self.assertNotIn('raise SystemExit("MEASUREMENT INVALID', source, tool.name)


class DerivedManifestThreeStates(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.saved = Path(self.tmp.name) / "manifest.json"

    def test_A_valid_measurement_satisfied_proposition_exits_0(self):
        code, output = run(MANIFEST, str(PROJECT), "--out", str(self.saved))
        self.assertEqual(VALID, code, output)
        code, output = run(MANIFEST, str(PROJECT), "--compare", str(self.saved))
        self.assertEqual(VALID, code, output)
        self.assertIn("PASS", output)

    def test_B_valid_measurement_substantive_discrepancy_exits_1(self):
        """Reaches the semantic comparison: both manifests are readable and well formed."""
        run(MANIFEST, str(PROJECT), "--out", str(self.saved))
        body = json.loads(self.saved.read_text(encoding="utf-8"))
        self.assertTrue(body["paths"], "the comparison must have something to compare")
        body["paths"] = body["paths"][:-1]
        self.saved.write_text(json.dumps(body), encoding="utf-8")

        code, output = run(MANIFEST, str(PROJECT), "--compare", str(self.saved))
        self.assertEqual(SUBSTANTIVE_FINDING, code, output)
        self.assertIn("differs", output)
        self.assertNotIn("MEASUREMENT INVALID", output)

    def test_C_measurement_cannot_be_established_exits_2(self):
        code, output = run(MANIFEST, str(Path(self.tmp.name) / "absent"))
        self.assertEqual(MEASUREMENT_INVALID, code, output)
        self.assertIn("MEASUREMENT INVALID", output)
        # No substantive conclusion is drawn about the derived output.
        self.assertNotIn("derived manifest:", output)

    def test_C_an_unreadable_comparison_manifest_is_also_measurement_invalid(self):
        broken = Path(self.tmp.name) / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        code, output = run(MANIFEST, str(PROJECT), "--compare", str(broken))
        self.assertEqual(MEASUREMENT_INVALID, code, output)
        self.assertIn("MEASUREMENT INVALID", output)


class AssuranceMetricsThreeStates(unittest.TestCase):
    """Load-bearing: this instrument validates the headline assurance aggregates."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_A_derived_populations_agree_with_asserted_aggregates_exits_0(self):
        code, output = run(METRICS, "--check")
        self.assertEqual(VALID, code, output)
        self.assertIn("Acceptance items:", output)
        self.assertIn("Evidence obligations:", output)
        self.assertIn("V&V checks:", output)

    def test_B_derived_populations_disagree_with_asserted_aggregates_exits_1(self):
        """A valid, readable assertion that is simply wrong. The comparison is reached."""
        body = yaml.safe_load(RELOCATION.read_text(encoding="utf-8"))
        body["results"]["records"] = 9999
        wrong = Path(self.tmp.name) / "relocation.yaml"
        wrong.write_text(yaml.safe_dump(body), encoding="utf-8")

        code, output = run(METRICS, "--check", "--relocation", str(wrong))
        self.assertEqual(SUBSTANTIVE_FINDING, code, output)
        self.assertIn("9999", output)
        self.assertIn("2144", output, "the derived population must be reported alongside")
        self.assertNotIn("MEASUREMENT INVALID", output)

    def test_C_a_population_that_cannot_be_derived_exits_2(self):
        code, output = run(METRICS, "--check",
                           "--checklist", str(Path(self.tmp.name) / "absent.yaml"))
        self.assertEqual(MEASUREMENT_INVALID, code, output)
        self.assertIn("MEASUREMENT INVALID", output)

    def test_C_says_nothing_about_whether_the_assurance_state_is_correct(self):
        """The distinction that makes this repair worth making."""
        code, output = run(METRICS, "--check",
                           "--checklist", str(Path(self.tmp.name) / "absent.yaml"))
        self.assertEqual(MEASUREMENT_INVALID, code)
        for metric in ("Acceptance items:", "Evidence obligations:", "V&V checks:"):
            self.assertNotIn(metric, output)
        for verdict in ("PASS:", "FAIL:", "disagree"):
            self.assertNotIn(verdict, output)

    def test_C_an_unreadable_population_source_is_measurement_invalid_not_a_finding(self):
        broken = Path(self.tmp.name) / "broken.yaml"
        broken.write_text("acceptance_items: [ unclosed", encoding="utf-8")
        code, output = run(METRICS, "--check", "--checklist", str(broken))
        self.assertEqual(MEASUREMENT_INVALID, code, output)
        self.assertIn("MEASUREMENT INVALID", output)

    def test_the_metrics_remain_derived_rather_than_hard_coded(self):
        """The pre-existing rule this repair must not have disturbed."""
        source = METRICS.read_text(encoding="utf-8")
        import re
        for forbidden in (r"\b11\s*/\s*16\b", r"\b17\s*/\s*25\b", r"= *2144\b"):
            self.assertIsNone(re.search(forbidden, source))


if __name__ == "__main__":
    unittest.main()
