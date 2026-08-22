"""The diagnostic probe's Ant element must stay derived from the production one.

The probe is only evidence about the production failure while it is the production
invocation with one class substituted. A hand-maintained copy is correct on the day it is
written and silently stops being correct the first time the production element is edited --
and a probe that has drifted still runs, still prints readings, and describes a different
execution. This binds the two together so that drift is a test failure rather than a
misleading diagnosis.
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "mps" / "derive_probe_target.py"
BUILD_FILE = REPO_ROOT / "build" / "nltps-headless-build.xml"


class ProbeDerivationTest(unittest.TestCase):
    def _run(self, build_file_text=None):
        return subprocess.run([sys.executable, str(TOOL), "--check"],
                              capture_output=True, text=True, cwd=str(REPO_ROOT))

    def test_probe_element_is_derived_from_production(self):
        result = self._run()
        self.assertEqual(0, result.returncode,
                         "probe element has drifted from the production element:\n"
                         + result.stdout + result.stderr)

    def test_drift_is_detected(self):
        """The gate is only worth having if it fails when it should.

        A control that has never been shown to fail is indistinguishable from one that
        cannot fail, which is the same defect this whole investigation is about.
        """
        original = BUILD_FILE.read_text(encoding="utf-8")
        self.assertIn('jnaLibraryPath="${mps.home}/lib/jna">', original)
        # Change the production element only. The probe element must no longer derive from it.
        damaged = original.replace(
            '<launchtests mpsHome="${mps.home}" haltOnFailure="true"',
            '<launchtests mpsHome="${mps.home}" haltOnFailure="false"', 1)
        self.assertNotEqual(original, damaged)
        try:
            BUILD_FILE.write_text(damaged, encoding="utf-8", newline="")
            result = self._run()
            self.assertEqual(1, result.returncode,
                             "the derivation gate did not notice a changed production "
                             "element; it cannot detect drift")
        finally:
            BUILD_FILE.write_text(original, encoding="utf-8", newline="")
        self.assertEqual(original, BUILD_FILE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
