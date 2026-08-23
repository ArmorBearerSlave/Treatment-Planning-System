"""F5: the Stage B gate measures the proposition it claims, over one state.

MPS-MAT-009 F5. The gate's stated question is "does the imported model say what the
controlled document says". Its measurement was a comparison of two committed files; the
persisted model entered only through root_identity(), which supplies node identity and never
a compared value. Inverting a requirement inside the corpus therefore left the gate reporting
119/119 equivalent -- a specific, confident, wrong answer to the exact question a reviewer
would run it to ask.

The repair composes two edges, and this exercises every seam between them:

    A  model changed        -> model/export FAIL, export/source PASS, composed NON-PASSING
    B  export changed       -> model/export FAIL, export/source FAIL, composed NON-PASSING
    C  source changed       -> model/export PASS, export/source FAIL, composed NON-PASSING
    D  all three current    -> both PASS, composed PASS

B is the discriminating case. A changed export matches neither the model nor the baseline, so
BOTH correspondences are broken, and a gate that stopped at the first would report one. That
under-reporting is invisible unless the seams are measured independently, which is why the
diagnostic measurement and the execution policy are separated here: production refuses the
PASS as soon as a prerequisite fails, while these controls characterise each edge on its own.

Every perturbation is same-type and parse-valid, so a rejection is about currentness rather
than about syntax. Fixtures are disposable copies in a temp directory and are never the
controlled model; the model perturbation reproduces the change that was made through
MPS-aware tooling for the retained counterexample.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import check_stage_b_equivalence as gate  # noqa: E402
from export_hlr_corpus import (  # noqa: E402
    ExportNotMeasurable,
    export_matches_model,
    serialize,
    export,
)

CORPUS = (REPO_ROOT / "mps" / "NLTPSGovernance" / "corpus" / "nltps.corpus" / "models"
          / "nltps.corpus.hlr")
EXPORT = REPO_ROOT / "mps" / "import" / "hlr-corpus-export.json"
BUNDLE = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"

PERTURBED_ID = "AIM-005"
ORIGINAL = "The NL-TPS shall maintain a model and dependency registry"
INVERTED = "The NL-TPS shall NOT maintain a model and dependency registry"


class Fixture:
    """A disposable copy of the three compared objects."""

    def __init__(self, tmp: Path):
        self.root = tmp
        self.model = tmp / "corpus"
        shutil.copytree(CORPUS, self.model)
        self.export = tmp / "export.json"
        self.export.write_bytes(EXPORT.read_bytes())
        self.bundle = tmp / "bundle.json"
        self.bundle.write_bytes(BUNDLE.read_bytes())
        self.table = tmp / "table.csv"

    def perturb_model(self):
        """Invert one requirement, exactly as the retained counterexample did through MPS."""
        changed = 0
        for root in self.model.glob("*.mpsr"):
            text = root.read_text(encoding="utf-8")
            if ORIGINAL in text:
                root.write_text(text.replace(ORIGINAL, INVERTED, 1), encoding="utf-8")
                changed += 1
        assert changed == 1, f"expected exactly one root to carry the statement, got {changed}"

    def perturb_export(self):
        """Same type, still valid JSON: change an exported field's value."""
        records = json.loads(self.export.read_text(encoding="utf-8"))
        for record in records:
            if record["id"] == PERTURBED_ID:
                record["statement_latex"] = record["statement_latex"].replace(
                    "shall maintain", "shall NOT maintain", 1)
                break
        else:
            raise AssertionError(f"{PERTURBED_ID} absent from the export")
        self.export.write_text(json.dumps(records, indent=2, sort_keys=True,
                                          ensure_ascii=False) + chr(10), encoding="utf-8")

    def perturb_source(self):
        """Same type, still valid JSON: change the baseline's own text for one requirement."""
        bundle = json.loads(self.bundle.read_text(encoding="utf-8"))
        for record in bundle["records"]:
            if record["id"] == PERTURBED_ID:
                record["normative_text_latex"] = record["normative_text_latex"].replace(
                    "shall maintain", "shall NOT maintain", 1)
                break
        else:
            raise AssertionError(f"{PERTURBED_ID} absent from the baseline")
        self.bundle.write_text(json.dumps(bundle, indent=2, sort_keys=True,
                                          ensure_ascii=False) + chr(10), encoding="utf-8")

    def model_export_edge(self) -> bool:
        current, _, _ = export_matches_model(self.model, self.export)
        return current

    def export_source_edge(self) -> bool:
        _, problems = gate.run(self.bundle, self.export, self.model, self.table)
        return not problems

    def composed(self) -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "mps" / "check_stage_b_equivalence.py"),
             "--model", str(self.model), "--export", str(self.export),
             "--bundle", str(self.bundle), "--table", str(self.table)],
            capture_output=True, text=True, cwd=str(REPO_ROOT))
        return result.returncode, result.stdout + result.stderr


class Seams(unittest.TestCase):

    def fixture(self) -> Fixture:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Fixture(Path(tmp.name))

    def test_seam_D_all_three_current_passes(self):
        f = self.fixture()
        self.assertTrue(f.model_export_edge(), "model/export must hold on the baseline")
        self.assertTrue(f.export_source_edge(), "export/source must hold on the baseline")
        code, output = f.composed()
        self.assertEqual(0, code, output)
        self.assertIn("matches the neutral export", output)

    def test_seam_A_model_changed_fails_only_the_model_export_edge(self):
        f = self.fixture()
        f.perturb_model()
        self.assertFalse(f.model_export_edge())
        self.assertTrue(f.export_source_edge(),
                        "the export still matches the baseline, so this edge must hold")
        code, output = f.composed()
        self.assertEqual(1, code, output)
        self.assertIn("persisted model != neutral export", output)
        self.assertNotIn("neutral export != source baseline", output)

    def test_seam_B_export_changed_fails_both_edges_and_reports_both(self):
        """The discriminating case: a gate that stopped at the first would under-report."""
        f = self.fixture()
        f.perturb_export()
        self.assertFalse(f.model_export_edge())
        self.assertFalse(f.export_source_edge())
        code, output = f.composed()
        self.assertEqual(1, code, output)
        self.assertIn("persisted model != neutral export", output)
        self.assertIn("neutral export != source baseline", output)

    def test_seam_C_source_changed_fails_only_the_export_source_edge(self):
        f = self.fixture()
        f.perturb_source()
        self.assertTrue(f.model_export_edge(),
                        "the model and export are untouched, so this edge must hold")
        self.assertFalse(f.export_source_edge())
        code, output = f.composed()
        self.assertEqual(1, code, output)
        self.assertIn("neutral export != source baseline", output)
        self.assertNotIn("failed edge: persisted model != neutral export", output)

    def test_no_pass_is_emitted_when_any_edge_fails(self):
        """Execution policy, distinct from the diagnostic measurement above."""
        for perturb in ("perturb_model", "perturb_export", "perturb_source"):
            with self.subTest(seam=perturb):
                f = self.fixture()
                getattr(f, perturb)()
                code, output = f.composed()
                self.assertNotEqual(0, code)
                self.assertNotIn("PASS:", output)


class MeasurementInvalidity(unittest.TestCase):
    """A failed measurement is not a finding about the corpus."""

    def test_an_absent_model_is_measurement_invalid_not_equivalence_failure(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        f = Fixture(Path(tmp.name))
        shutil.rmtree(f.model)
        code, output = f.composed()
        self.assertEqual(2, code, output)
        self.assertIn("MEASUREMENT INVALID", output)
        self.assertNotIn("NOT ESTABLISHED", output)

    def test_an_unreadable_model_raises_not_measurable(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        f = Fixture(Path(tmp.name))
        shutil.rmtree(f.model)
        with self.assertRaises(ExportNotMeasurable):
            export_matches_model(f.model, f.export)


class ClaimScope(unittest.TestCase):
    """The PASS line may claim only what the measurement path establishes."""

    def test_the_pass_line_scopes_itself_to_the_exported_field_contract(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        code, output = Fixture(Path(tmp.name)).composed()
        self.assertEqual(0, code, output)
        self.assertIn("frozen exported-field contract", output)
        # Generic equivalence language would claim a proposition no edge here measures: the
        # first edge observes only the fields the exporter selects.
        for overclaim in ("model is equivalent", "model and source are equivalent"):
            self.assertNotIn(overclaim, output)

    def test_the_pass_line_identifies_the_state_it_established(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        code, output = Fixture(Path(tmp.name)).composed()
        self.assertEqual(0, code, output)
        for token in ("model tree", "export", "baseline", "corpus"):
            self.assertIn(token, output)

    def test_there_is_one_definition_of_the_model_export_contract(self):
        """The gate must not re-implement model traversal or export serialization."""
        source = (REPO_ROOT / "tools" / "mps"
                  / "check_stage_b_equivalence.py").read_text(encoding="utf-8")
        for owned_by_the_exporter in ("def export_root", "def provenance(", "json.dumps(records"):
            self.assertNotIn(owned_by_the_exporter, source,
                             "the exporter owns the model-to-export contract; a second "
                             "definition here would drift")


if __name__ == "__main__":
    unittest.main()
