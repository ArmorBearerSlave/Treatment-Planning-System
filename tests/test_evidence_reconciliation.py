"""Failure-sensitivity controls for the evidence reconciler.

MPS-MAT-009 F2. The reconciler's whole value is that it can say no, so every declared
failure mode is driven here with a fixture that should be refused. A reconciler that only
ever passes over the real register is indistinguishable from one that returns True, and that
is precisely the defect it was written to correct: the project declared evidence obligations
for the whole of Stage A and nothing read them, so nothing could ever have failed.

Each test names the failure mode from the repair order it controls.
"""
from __future__ import annotations

import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import check_evidence_reconciliation as reconciler  # noqa: E402


def register_with(artifacts, acceptance_item="ITEM-A"):
    return {
        "records": {"REC": {"acceptance_item": acceptance_item, "artifacts": artifacts}},
        "records_pending": {},
        "obligations": {},
    }


class RecordChainFailureModes(unittest.TestCase):
    """The chain from a named record down to bytes on disk."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.real = Path(self.tmp.name) / "artifact.xml"
        self.real.write_bytes(b"<suite tests='1'/>\n")
        self.digest = hashlib.sha256(self.real.read_bytes()).hexdigest()
        # record_status resolves artifact paths against REPO_ROOT, so point it at the
        # temporary tree for the duration of each test rather than writing into the repo.
        self._saved_root = reconciler.REPO_ROOT
        reconciler.REPO_ROOT = Path(self.tmp.name)
        self.addCleanup(lambda: setattr(reconciler, "REPO_ROOT", self._saved_root))

    def test_retained_record_absent_is_non_passing(self):
        ok, why = reconciler.record_status("NOT-DECLARED", "ITEM-A", register_with([]))
        self.assertFalse(ok)
        self.assertIn("retained record absent", why)

    def test_record_naming_no_artifacts_is_non_passing(self):
        ok, why = reconciler.record_status("REC", "ITEM-A", register_with([]))
        self.assertFalse(ok)
        self.assertIn("names no artifacts", why)

    def test_artifact_absent_is_non_passing(self):
        register = register_with([{"path": "missing.xml", "sha256": self.digest}])
        ok, why = reconciler.record_status("REC", "ITEM-A", register)
        self.assertFalse(ok)
        self.assertIn("artifact absent", why)

    def test_hash_absent_is_non_passing(self):
        """A retained artifact with no declared digest binds the record to nothing."""
        register = register_with([{"path": "artifact.xml"}])
        ok, why = reconciler.record_status("REC", "ITEM-A", register)
        self.assertFalse(ok)
        self.assertIn("hash absent", why)

    def test_hash_mismatch_is_non_passing(self):
        register = register_with([{"path": "artifact.xml", "sha256": "0" * 64}])
        ok, why = reconciler.record_status("REC", "ITEM-A", register)
        self.assertFalse(ok)
        self.assertIn("hash mismatch", why)

    def test_evidence_belonging_to_the_wrong_item_is_non_passing(self):
        register = register_with([{"path": "artifact.xml", "sha256": self.digest}],
                                 acceptance_item="ITEM-B")
        ok, why = reconciler.record_status("REC", "ITEM-A", register)
        self.assertFalse(ok)
        self.assertIn("wrong item", why)

    def test_a_pending_record_does_not_discharge_anything(self):
        register = {"records": {}, "records_pending": {"REC": {}}, "obligations": {}}
        ok, why = reconciler.record_status("REC", "ITEM-A", register)
        self.assertFalse(ok)
        self.assertIn("pending", why)

    def test_the_complete_chain_passes_only_when_every_link_holds(self):
        register = register_with([{"path": "artifact.xml", "sha256": self.digest}])
        ok, why = reconciler.record_status("REC", "ITEM-A", register)
        self.assertTrue(ok, why)

    def test_a_changed_artifact_stops_passing(self):
        """The control that makes the hash meaningful: same path, different bytes."""
        register = register_with([{"path": "artifact.xml", "sha256": self.digest}])
        self.assertTrue(reconciler.record_status("REC", "ITEM-A", register)[0])
        self.real.write_bytes(b"<suite tests='2'/>\n")
        ok, why = reconciler.record_status("REC", "ITEM-A", register)
        self.assertFalse(ok)
        self.assertIn("hash mismatch", why)


class DeclarationLevelFailureModes(unittest.TestCase):
    """Modes that live between the freeze's declarations and the register's entries."""

    def setUp(self):
        self._declared = reconciler.declared_obligations
        self._load = reconciler.load_yaml
        self.addCleanup(lambda: setattr(reconciler, "declared_obligations", self._declared))
        self.addCleanup(lambda: setattr(reconciler, "load_yaml", self._load))

    def drive(self, declarations, register):
        reconciler.declared_obligations = lambda: declarations
        reconciler.load_yaml = lambda path: register
        return reconciler.check()

    def test_declaration_with_no_observer_is_non_passing(self):
        problems, tally = self.drive({"ITEM-A": ["something required"]},
                                     {"records": {}, "obligations": {}})
        self.assertTrue(any("no observer" in message for _, message in problems))
        self.assertEqual(tally["satisfied"], 0)

    def test_ambiguity_is_surfaced_and_not_resolved_by_choosing(self):
        register = {
            "records": {},
            "obligations": {"ITEM-A": [
                {"declaration": "x", "observer": "gate", "gate": "tools/a.py"},
                {"declaration": "x", "observer": "unobserved", "why": "other"},
            ]},
        }
        problems, tally = self.drive({"ITEM-A": ["x"]}, register)
        self.assertTrue(any("ambiguous" in message for _, message in problems))
        # Neither candidate was adopted: the ambiguity is the finding, not an input to a
        # tie-break.
        self.assertEqual(tally["satisfied"], 0)

    def test_a_gate_that_does_not_exist_is_non_passing(self):
        register = {"records": {}, "obligations": {"ITEM-A": [
            {"declaration": "x", "observer": "gate", "gate": "tools/mps/no_such_gate.py"}]}}
        problems, _ = self.drive({"ITEM-A": ["x"]}, register)
        self.assertTrue(any("does not exist" in message for _, message in problems))

    def test_a_gate_nothing_runs_is_non_passing(self):
        """Naming a real file that is not a declared step observes nothing."""
        register = {"records": {}, "obligations": {"ITEM-A": [
            {"declaration": "x", "observer": "gate",
             "gate": "tools/mps/mps_layout.py"}]}}
        problems, _ = self.drive({"ITEM-A": ["x"]}, register)
        self.assertTrue(any("not a declared step" in message for _, message in problems))

    def test_a_stale_register_entry_is_non_passing(self):
        register = {"records": {}, "obligations": {"ITEM-A": [
            {"declaration": "an obligation no freeze declares", "observer": "unobserved",
             "why": "stale"}]}}
        problems, _ = self.drive({"ITEM-A": []}, register)
        self.assertTrue(any("matches no evidence_required" in message
                            for _, message in problems))


class TheRealRegister(unittest.TestCase):
    """Properties of the register as committed, rather than of fixtures."""

    def test_the_gov_c_004_obligation_is_discharged_by_a_retained_artifact(self):
        """F2's own repair: the obligation that had no evidence now has hash-bound evidence."""
        ok, why = reconciler.record_status("GOV-C-004-literal-example", "MPS-MAT-005D")
        self.assertTrue(ok, why)

    def test_the_gov_c_004_record_carries_both_the_observation_and_its_control(self):
        register = reconciler.load_yaml(reconciler.REGISTER)
        record = register["records"]["GOV-C-004-literal-example"]
        roles = " ".join(a.get("role", "") for a in record["artifacts"])
        self.assertIn("positive", roles)
        self.assertIn("discrimination control", roles)

    def test_the_reconciler_reports_unresolved_obligations_rather_than_passing(self):
        """The suite is currently red here by design; this asserts it is red for real."""
        problems, tally = reconciler.check()
        self.assertGreater(tally["declarations"], 0)
        self.assertTrue(problems, "a reconciler that never fails is not an instrument")
        self.assertGreaterEqual(tally["by_artifact"], 1)


if __name__ == "__main__":
    unittest.main()
