"""The coverage controls the build descriptor has always claimed to have.

The descriptor's own comment said this file held the make list equal to the project's
modules.xml. It did not exist. Written now, together with the dependency-closure control
that the NOT_IN_REPO defect recorded at 875fcee showed was missing, and with negative
controls for both -- a gate never shown to fail is indistinguishable from one that cannot.
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "mps" / "check_headless_coverage.py"
BUILD_FILE = REPO_ROOT / "build" / "nltps-headless-build.xml"

sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))


def run_gate():
    return subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True,
                          cwd=str(REPO_ROOT))


class HeadlessCoverageTest(unittest.TestCase):
    def test_gate_passes_as_committed(self):
        result = run_gate()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def _damaged(self, old, new, expect_in_stderr):
        original = BUILD_FILE.read_text(encoding="utf-8")
        self.assertIn(old, original)
        try:
            BUILD_FILE.write_text(original.replace(old, new, 1), encoding="utf-8",
                                  newline="")
            result = run_gate()
            self.assertEqual(1, result.returncode,
                             "the gate did not fail on a damaged descriptor")
            self.assertIn(expect_in_stderr, result.stderr)
        finally:
            BUILD_FILE.write_text(original, encoding="utf-8", newline="")
        self.assertEqual(original, BUILD_FILE.read_text(encoding="utf-8"))

    def test_unsupplied_dependency_is_detected(self):
        self._damaged(
            '        <module file="${project.dir}/sandbox/nltps.proof/nltps.proof.msd"/>\n',
            '',
            "dependency on nltps.proof")

    def test_uncovered_make_module_is_detected(self):
        self._damaged(
            '      <module file="${project.dir}/corpus/nltps.corpus/nltps.corpus.msd"/>\n',
            '',
            "does not cover the project")


class ModuleListScopeTest(unittest.TestCase):
    """module_list() must read only the make target.

    <module file="..."/> is also how the test target names support modules inside
    <repository>. Harvesting the whole document reported nltps.proof three times, which
    would have gone into the provenance record looking deliberate.
    """

    def test_module_list_has_no_duplicates(self):
        import headless_build

        modules = headless_build.module_list()
        self.assertEqual(len(modules), len(set(modules)), modules)

    def test_module_list_matches_project(self):
        import check_headless_coverage
        import headless_build

        self.assertEqual(sorted(headless_build.module_list()),
                         sorted(check_headless_coverage.project_modules().values()))


if __name__ == "__main__":
    unittest.main()
