"""MI-EXIT-01: a measurement-invalid state must not arrive as a substantive finding.

Two controlled instruments printed the words MEASUREMENT INVALID and nevertheless exited 1,
because `raise SystemExit("text")` prints the text and exits 1 -- Python reserves the integer
form for the status. The internal state was right and the externally observable verdict was
wrong.

The class is measurement-state-to-process-verdict corruption, which is NOT the same as
F5-FU-02. There, a correct equivalence result had already been computed and was destroyed
while being printed: genuine post-measurement corruption. Here no complete measurement ever
existed, so nothing was corrupted after the fact -- an incomplete measurement was mapped onto
the verdict code reserved for a completed one. Related, and distinct.

The contract is conditional, not universal:

    an instrument emitting 0   measured validly and its success proposition holds
    an instrument emitting 1   measured validly and established a substantive finding
    an instrument emitting 2   did not adjudicate, because measurement was invalid

Not every instrument must be able to emit all three. derived_manifest either enumerates its
population or reports that it could not; it has no substantive-finding state and none is
invented for it. And exit 2 from argparse for a usage error is not measurement invalidity, so
the exit code alone remains insufficient for classification.

Every control here observes a real process exit code. A test asserting on an exception type
would not have caught the original defect, because the defect lived exactly at the boundary
such a test never crosses. Where a branch needs fixture inputs, a disposable wrapper injects
them and exits with the measurement's own return code -- rather than the production command
growing switches that accept arbitrary sources, which is what round 1 did and what created
its provenance defects.

No control here depends on gitignored derived state. Round 1's did, and on a cold tree one
failed while another passed vacuously over an empty population.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

MANIFEST_TOOL = REPO_ROOT / "tools" / "mps" / "derived_manifest.py"
METRICS_TOOL = REPO_ROOT / "tools" / "spec" / "report_assurance_metrics.py"
RELOCATION = REPO_ROOT / "spec" / "relocation_verification.yaml"
CHECKLIST = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"

VALID = 0
SUBSTANTIVE_FINDING = 1
MEASUREMENT_INVALID = 2

MARKER = "MEASUREMENT INVALID"


# --------------------------------------------------------------------------------------
# AST anti-pattern guard
# --------------------------------------------------------------------------------------

def raises_system_exit_with_marker(source: str) -> list[int]:
    """Line numbers of `raise SystemExit(<string containing MEASUREMENT INVALID>)`.

    Round 1 used a line-oriented substring guard, which missed the very shape the historical
    defect had: the call wrapped across lines, with the marker on a continuation line. A
    regex over lines cannot see a construct whose parts are on different lines, so the guard
    passed while the defect was present in exactly the form it was written to catch.

    Parsing settles it. The detector is deliberately narrow: it finds one anti-pattern. It is
    not, and must not be read as, proof of ternary exit semantics across the repository --
    the behavioural controls below are what establish that for the two repaired sites.
    """
    hits: list[int] = []

    def carries_marker(node: ast.AST) -> bool:
        for inner in ast.walk(node):
            if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                if MARKER in inner.value:
                    return True
        return False

    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
            continue
        func = node.exc.func
        name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        if name != "SystemExit":
            continue
        if any(carries_marker(arg) for arg in node.exc.args):
            hits.append(node.lineno)
    return hits


class AstGuardIsProvenBeforeItIsTrusted(unittest.TestCase):
    """Synthetic controls. A guard nobody has seen fail is not a guard."""

    def test_detects_a_single_line_string(self):
        source = 'raise SystemExit("MEASUREMENT INVALID: x")'
        self.assertEqual([1], raises_system_exit_with_marker(source))

    def test_detects_a_wrapped_call_with_the_marker_on_a_continuation_line(self):
        """The exact historical shape the line-oriented guard could not see."""
        source = textwrap.dedent('''
            def f(x):
                raise SystemExit(
                    f"MEASUREMENT INVALID: the graph declares {x} "
                    f"but the population disagrees.")
        ''')
        self.assertTrue(raises_system_exit_with_marker(source))

    def test_detects_a_marker_split_across_implicit_concatenation(self):
        """Detected, and I expected it not to be.

        The first version of this control asserted that a marker split across adjacent string
        literals would escape, on the reasoning that no single constant contains it. Python
        folds implicit concatenation at parse time, so the parser sees one constant and the
        guard finds it. The assertion is corrected to the observed behaviour rather than the
        predicted one; the guard is stronger here than it was claimed to be.
        """
        source = textwrap.dedent('''
            raise SystemExit("MEASUREMENT "
                             "INVALID: split across lines")
        ''')
        self.assertTrue(raises_system_exit_with_marker(source))

    def test_a_marker_assembled_at_runtime_is_outside_what_the_guard_claims(self):
        """The honest limit: the guard reads literals, not computed values."""
        source = 'raise SystemExit("MEASUREMENT" + " INVALID: assembled")'
        self.assertEqual([], raises_system_exit_with_marker(source))

    def test_detects_a_parenthesised_multiline_f_string(self):
        source = textwrap.dedent('''
            raise SystemExit(
                f"MEASUREMENT INVALID: {1 + 1}"
            )
        ''')
        self.assertTrue(raises_system_exit_with_marker(source))

    def test_allows_a_correct_integer_system_exit(self):
        self.assertEqual([], raises_system_exit_with_marker("raise SystemExit(2)"))

    def test_allows_printing_the_marker_and_returning_2(self):
        source = textwrap.dedent('''
            def f():
                print("MEASUREMENT INVALID: x", file=sys.stderr)
                return 2
        ''')
        self.assertEqual([], raises_system_exit_with_marker(source))

    def test_the_two_repaired_instruments_are_clean(self):
        for tool in (MANIFEST_TOOL, METRICS_TOOL):
            with self.subTest(tool=tool.name):
                self.assertEqual([], raises_system_exit_with_marker(
                    tool.read_text(encoding="utf-8")))

    def test_an_integer_valued_system_exit_carrying_a_variable_is_allowed(self):
        """`raise SystemExit(code)` is the correct form and must not be flagged.

        Stated as a control so nobody later "fixes" the test wrapper to sys.exit() for
        consistency and is then puzzled that the guard treats the two differently. The guard
        keys on a STRING argument containing the marker; an integer, or a name bound to one,
        is exactly what the repair asks for.
        """
        for allowed in ("raise SystemExit(2)",
                        "raise SystemExit(return_code)",
                        "raise SystemExit(measurement.run(a, b))"):
            with self.subTest(form=allowed):
                self.assertEqual([], raises_system_exit_with_marker(allowed))

    def test_the_guard_population_is_controlled_source_only(self):
        """A disposable wrapper is outside the population by construction, not by exemption.

        The wrapper legitimately ends with `raise SystemExit(<int>)`, which the guard permits
        anyway -- but the point stands independently: the guard is applied to the controlled
        instruments, and scratch files created by a test are never part of what it scans.
        """
        with tempfile.TemporaryDirectory() as tmp:
            wrapper = metrics_wrapper(Path(tmp) / "wrapper.py")
            self.assertEqual([], raises_system_exit_with_marker(
                wrapper.read_text(encoding="utf-8")),
                "the wrapper's integer-valued SystemExit is correct and unflagged")
            self.assertFalse(str(wrapper).startswith(str(REPO_ROOT)),
                             "a disposable wrapper lives outside the controlled tree")

    def test_the_language_semantics_that_caused_the_defect(self):
        result = subprocess.run([sys.executable, "-c",
                                 "raise SystemExit('MEASUREMENT INVALID: demo')"],
                                capture_output=True, text=True)
        self.assertEqual(1, result.returncode)


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------

def run(*argv: str) -> tuple[int, str]:
    result = subprocess.run([sys.executable, *argv], capture_output=True, text=True,
                            cwd=str(REPO_ROOT))
    return result.returncode, result.stdout + result.stderr


def build_project(root: Path) -> list[str]:
    """A self-contained project fixture with a known, non-empty derived population.

    Built here rather than pointed at the repository, because the repository's derived output
    is gitignored: on a cold clone it does not exist, and a control over an empty population
    is vacuous. Round 1's positive control compared 0 paths against 0 paths and passed.
    """
    files = {
        "mod/test_gen/nltps/A_Test.java": "class A {}",
        "mod/classes_gen/nltps/A_Test.class": "binary-ish",
        "mod/source_gen/nltps/B.java": "class B {}",
    }
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return sorted(files)


def metrics_wrapper(path: Path) -> Path:
    """A disposable subprocess wrapper that injects fixtures and exits with the real code.

    It imports the same measurement function the production CLI calls and does not restate
    any of it. Its only job is to let a control observe the process exit code for branches
    whose inputs must be substituted -- without the production command exposing a way to
    substitute them.
    """
    path.write_text(textwrap.dedent(f'''
        import json, sys
        from pathlib import Path
        sys.path.insert(0, r"{REPO_ROOT / "tools" / "spec"}")
        sys.path.insert(0, r"{REPO_ROOT / "tools" / "mps"}")
        import report_assurance_metrics as measurement

        checklist, relocation, document_path = sys.argv[1], sys.argv[2], sys.argv[3]
        document = None
        if document_path != "-":
            document = json.loads(Path(document_path).read_text(encoding="utf-8"))
        raise SystemExit(measurement.run_assurance_measurement(
            Path(checklist), Path(relocation), True, document))
    '''), encoding="utf-8")
    return path


# --------------------------------------------------------------------------------------
# derived_manifest: reachable states are 0 and 2
# --------------------------------------------------------------------------------------

class DerivedManifestStates(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_valid_measurement_over_a_non_empty_population_exits_0(self):
        expected = build_project(self.root / "project")
        out = self.root / "manifest.json"
        code, output = run(str(MANIFEST_TOOL), str(self.root / "project"), "--out", str(out))
        self.assertEqual(VALID, code, output)

        manifest = json.loads(out.read_text(encoding="utf-8"))
        # Non-vacuity, asserted before the verdict is accepted.
        self.assertGreater(len(manifest["paths"]), 0)
        self.assertEqual(3, len(manifest["paths"]))
        self.assertEqual(expected, manifest["paths"])

    def test_measurement_that_cannot_be_established_exits_2(self):
        code, output = run(str(MANIFEST_TOOL), str(self.root / "absent"))
        self.assertEqual(MEASUREMENT_INVALID, code, output)
        self.assertIn(MARKER, output)
        self.assertNotIn("derived manifest:", output)

    def test_it_exposes_no_comparison_interface(self):
        """MI-R-03: --compare was never needed for MI-EXIT-01 and is gone."""
        code, output = run(str(MANIFEST_TOOL), "--help")
        self.assertEqual(VALID, code)
        self.assertNotIn("--compare", output)

    def test_it_has_no_reachable_substantive_finding_state_and_that_is_correct(self):
        source = MANIFEST_TOOL.read_text(encoding="utf-8")
        self.assertNotIn("return 1", source,
                         "this instrument either measures or reports that it could not; "
                         "a substantive-finding state must not be invented for symmetry")


# --------------------------------------------------------------------------------------
# report_assurance_metrics: all three states
# --------------------------------------------------------------------------------------

class AssuranceMetricsStates(unittest.TestCase):
    """Load-bearing: this instrument validates the headline assurance aggregates."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.wrapper = metrics_wrapper(self.root / "wrapper.py")

    def test_production_invocation_over_canonical_sources_exits_0(self):
        """The production path, invoked exactly as a person or CI would."""
        code, output = run(str(METRICS_TOOL), "--check")
        self.assertEqual(VALID, code, output)
        for metric in ("Acceptance items:", "Evidence obligations:", "V&V checks:"):
            self.assertIn(metric, output)

    def test_the_production_cli_cannot_be_pointed_at_substitute_sources(self):
        """MI-R-01 and MI-R-02: the provenance hazard is removed, not documented."""
        code, output = run(str(METRICS_TOOL), "--help")
        self.assertEqual(VALID, code)
        for removed in ("--checklist", "--relocation"):
            self.assertNotIn(removed, output)
        code, output = run(str(METRICS_TOOL), "--checklist", str(self.root / "x.yaml"))
        self.assertNotEqual(VALID, code)
        self.assertNotIn("Acceptance items:", output,
                         "an unrecognised option must not yield a production-shaped report")

    def test_substantive_finding_exits_1(self):
        """A valid, readable assertion that is simply wrong; the comparison is reached."""
        body = yaml.safe_load(RELOCATION.read_text(encoding="utf-8"))
        body["results"]["records"] = 9999
        wrong = self.root / "relocation.yaml"
        wrong.write_text(yaml.safe_dump(body), encoding="utf-8")

        code, output = run(str(self.wrapper), str(CHECKLIST), str(wrong), "-")
        self.assertEqual(SUBSTANTIVE_FINDING, code, output)
        self.assertIn("9999", output)
        self.assertIn("2144", output)
        self.assertNotIn(MARKER, output)

    def test_an_underivable_population_exits_2_and_adjudicates_nothing(self):
        code, output = run(str(self.wrapper), str(self.root / "absent.yaml"),
                           str(RELOCATION), "-")
        self.assertEqual(MEASUREMENT_INVALID, code, output)
        self.assertIn(MARKER, output)
        for metric in ("Acceptance items:", "Evidence obligations:", "V&V checks:"):
            self.assertNotIn(metric, output)
        for verdict in ("PASS:", "FAIL:", "disagree"):
            self.assertNotIn(verdict, output)

    def test_the_historical_vv_claim_count_branch_exits_2(self):
        """MI-R-05: the exact branch that carried the original defect, exercised.

        A trace graph declaring a claim total that its own records do not support is treated
        as measurement invalid, because the measuring source contradicts itself and the
        instrument cannot know which population is authoritative. That interpretation is a
        semantic judgement held for Probe 1 review; what MI-EXIT-01 requires is only that it
        be encoded distinctly from a substantive governance discrepancy.
        """
        document = {
            "vv_claim_count": 9,
            "records": [
                {"id": "A-1", "hazard_specificity": "derived", "vv_claim_id": "VV-A-1"},
                {"id": "A-2", "hazard_specificity": "source_explicit", "vv_claim_id": "VV-A-2"},
            ],
        }
        graph = self.root / "graph.json"
        graph.write_text(json.dumps(document), encoding="utf-8")

        code, output = run(str(self.wrapper), str(CHECKLIST), str(RELOCATION), str(graph))
        self.assertEqual(MEASUREMENT_INVALID, code, output)
        self.assertIn(MARKER, output)
        self.assertIn("vv_claim_count", output)
        for metric in ("Acceptance items:", "Evidence obligations:", "V&V checks:"):
            self.assertNotIn(metric, output)
        self.assertNotIn("PASS:", output)
        self.assertNotIn("FAIL:", output)

    def test_the_metrics_remain_derived_rather_than_hard_coded(self):
        import re

        source = METRICS_TOOL.read_text(encoding="utf-8")
        for forbidden in (r"\b11\s*/\s*16\b", r"\b17\s*/\s*25\b", r"= *2144\b"):
            self.assertIsNone(re.search(forbidden, source))


class TaxonomyScope(unittest.TestCase):
    """What the exit codes do and do not settle."""

    def test_usage_exit_2_is_not_measurement_invalidity(self):
        code, output = run(str(METRICS_TOOL), "--no-such-option")
        self.assertEqual(2, code)
        self.assertNotIn(MARKER, output,
                         "argparse exits 2 for a usage error; the code alone cannot "
                         "classify meaning, which is why Probe 1 must survey semantically")


if __name__ == "__main__":
    unittest.main()
