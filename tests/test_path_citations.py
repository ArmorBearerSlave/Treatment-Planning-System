"""The path-citation gate, and proof that it can fail in both directions.

The defect it guards against was real: a build descriptor comment claimed a test file that
did not exist. The gate is cheap, so what matters is that it is not decorative -- both the
missing-citation branch and the stale-declaration branch are exercised here.
"""
import io
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "spec" / "check_path_citations.py"
ALLOWLIST = REPO_ROOT / "spec" / "path_citation_allowlist.yaml"
CANARY = REPO_ROOT / "spec" / "artifacts.yaml"


def run_gate():
    return subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True,
                          cwd=str(REPO_ROOT))


class PathCitationTest(unittest.TestCase):
    def test_passes_as_committed(self):
        result = run_gate()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_undeclared_missing_citation_fails(self):
        """The fixture path is assembled at runtime, never written here as a literal.

        The gate scans the test suite along with everything else, so a literal would itself
        be a citation of a missing file -- which would then have to be declared in the
        allowlist, and declaring it is exactly what stops this control from firing. The
        first attempt did that: the gate went green and this control asserted nothing.
        """
        fixture = "tools/mps/check_" + "runtime_only_fixture" + ".py"
        self.assertFalse((REPO_ROOT / fixture).exists())
        original = CANARY.read_text(encoding="utf-8")
        try:
            CANARY.write_text(original + "\n# cites " + fixture + "\n",
                              encoding="utf-8", newline="")
            result = run_gate()
            self.assertEqual(1, result.returncode,
                             "the gate did not notice a citation of a missing file")
            self.assertIn(fixture, result.stderr)
        finally:
            CANARY.write_text(original, encoding="utf-8", newline="")
        self.assertEqual(original, CANARY.read_text(encoding="utf-8"))

    def test_declaration_that_has_outlived_its_reason_fails(self):
        """An allowlist entry for a path that now exists must fail, not pass quietly.

        Otherwise "declared absent" survives the file being written, and the declaration
        stops describing anything.
        """
        original = ALLOWLIST.read_text(encoding="utf-8")
        try:
            ALLOWLIST.write_text(
                original + "- path: tools/spec/check_path_citations.py\n"
                           "  status: declared_future_work\n"
                           "  reason: deliberately wrong; this file exists\n",
                encoding="utf-8", newline="")
            result = run_gate()
            self.assertEqual(1, result.returncode,
                             "the gate did not notice a declaration that now resolves")
            self.assertIn("but now exists", result.stderr)
        finally:
            ALLOWLIST.write_text(original, encoding="utf-8", newline="")
        self.assertEqual(original, ALLOWLIST.read_text(encoding="utf-8"))

    def test_declarations_are_the_expected_set_and_still_absent(self):
        """The exact set, not a count.

        An allowlist is only a control while adding to it is a deliberate act. Asserting
        the membership makes a new declaration a visible change to this file rather than
        a number quietly going up.
        """
        import yaml

        with io.open(ALLOWLIST, encoding="utf-8") as handle:
            declared = yaml.safe_load(handle.read())["absent_by_declaration"]
        self.assertEqual(
            {"mps/bootstrap/does-not-exist.yaml",
             "tools/mps/check_nonexistent_thing.py",
             # MPS-MAT-009 F2. Two fixtures driving the evidence reconciler's failure modes:
             # an observer gate that does not exist, and an ambiguous duplicate declaration.
             # Both must stay absent, for the same reason as the two above.
             "tools/a.py",
             "tools/mps/no_such_gate.py",
             # RT-F-06. Mutation control C: a reviewable unit declared record_file_backed
             # whose record does not exist must be refused. It must stay absent.
             "mps/materialization/mps-mat-009/absent.yaml"},
            {entry["path"] for entry in declared})
        for entry in declared:
            self.assertFalse((REPO_ROOT / entry["path"]).exists(), entry["path"])
            self.assertIn(entry["status"],
                          ("negative_control_fixture", "declared_future_work"))
            self.assertTrue(entry["reason"].strip())


if __name__ == "__main__":
    unittest.main()
