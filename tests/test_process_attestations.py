"""Controls for construction-process attribution and the five obligation states.

MPS-MAT-009. Two things are being protected here.

The first is an architecture boundary. The modelled clinical role ontology answers who may
authorize, review or act WITHIN the treatment-planning system. Construction-process
attribution answers who accepted an engineering obligation DURING CONSTRUCTION of it. They
share the words "authority" and "role" and are not the same semantic domain, and the reuse is
attractive enough that it needs forbidding rather than merely discouraging: conflating them
would let the system's own domain model govern the provenance of its own construction, after
which the clinical ontology comes under pressure to accommodate process needs it was never
designed for.

The second is that the five states stay five. Each collapse loses information that someone
later needs: OPEN into ATTESTED loses who accepted what, and OBSERVED into DISCHARGED loses
the difference between an artifact existing and an artifact establishing the claim.
"""
from __future__ import annotations

import hashlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "spec"))

import check_evidence_reconciliation as reconciler  # noqa: E402

ATTESTATIONS = REPO_ROOT / "mps" / "materialization" / "process-attestations.yaml"

# The modelled clinical/domain governance vocabulary. A construction-process record naming
# any of these has crossed the boundary.
CLINICAL_ONTOLOGY = (
    "nltps.roles", "ProfessionalRole", "OperationalRole", "RoleCapability",
    "AuthorityClass", "ApprovalGate", "AuthorizedActor",
)


class ArchitectureBoundary(unittest.TestCase):

    def test_the_attestation_register_exists_and_parses(self):
        self.assertTrue(ATTESTATIONS.is_file())
        self.assertIsInstance(yaml.safe_load(ATTESTATIONS.read_text(encoding="utf-8")), dict)

    def test_process_attribution_does_not_depend_on_the_clinical_role_ontology(self):
        """The boundary, enforced rather than documented.

        Checked over the register's DATA, not its prose: the architecture_boundary section
        names the forbidden concepts in order to forbid them, and a naive substring scan of
        the whole file would therefore fail on the very text that establishes the rule.
        """
        body = yaml.safe_load(ATTESTATIONS.read_text(encoding="utf-8"))
        payload = yaml.safe_dump(
            {"attestations": body.get("attestations") or [],
             "state_model": body.get("state_model") or {}})
        for concept in CLINICAL_ONTOLOGY:
            self.assertNotIn(
                concept, payload,
                f"construction-process attribution must not reference {concept}; "
                f"the domain model must not govern its own construction")

    def test_the_register_declares_that_attestation_does_not_discharge(self):
        body = yaml.safe_load(ATTESTATIONS.read_text(encoding="utf-8"))
        self.assertIs(False, body.get("attestation_discharges_obligations"))

    def test_all_five_states_are_represented(self):
        body = yaml.safe_load(ATTESTATIONS.read_text(encoding="utf-8"))
        self.assertEqual(
            {"DECLARED", "OPEN", "ATTESTED", "OBSERVED", "DISCHARGED"},
            set(body["state_model"]))

    def test_no_historical_assertion_was_retrofitted_with_an_authority(self):
        """0 of 103 evidence lines named an authority; none may acquire one retroactively."""
        body = yaml.safe_load(ATTESTATIONS.read_text(encoding="utf-8"))
        self.assertEqual([], body.get("attestations") or [],
                         "an attestation must be contemporaneous, not fitted to old prose")


class FiveStatesStayFive(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        artifact = Path(self.tmp.name) / "obs.xml"
        artifact.write_bytes(b"<suite failures='1'/>\n")
        self.digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        self._root = reconciler.REPO_ROOT
        reconciler.REPO_ROOT = Path(self.tmp.name)
        self.addCleanup(lambda: setattr(reconciler, "REPO_ROOT", self._root))
        self._att = reconciler.attestations_for
        self.addCleanup(lambda: setattr(reconciler, "attestations_for", self._att))
        reconciler.attestations_for = lambda oid: []

    def bound_register(self, satisfies):
        record = {"acceptance_item": "ITEM-A",
                  "artifacts": [{"path": "obs.xml", "sha256": self.digest}]}
        if satisfies is not None:
            record["satisfies_obligation"] = satisfies
        return {"records": {"REC": record}, "records_pending": {}, "obligations": {}}

    def test_unattributed_assertion_is_not_attested(self):
        """OPEN != ATTESTED. Prose without a named authority stays OPEN."""
        entry = {"declaration": "x", "observer": "unobserved",
                 "why": "attested in prose in the checklist evidence list"}
        state, _ = reconciler.obligation_state("ITEM-A", 0, entry, {"records": {}})
        self.assertEqual(reconciler.OPEN, state)
        self.assertNotEqual(reconciler.ATTESTED, state)

    def test_a_named_authority_without_an_artifact_is_attested_not_discharged(self):
        """ATTESTED != DISCHARGED. Acknowledgement is not establishment."""
        reconciler.attestations_for = lambda oid: [
            {"obligation_id": oid, "authority": "A. Person", "authority_role": "eng lead"}]
        entry = {"declaration": "x", "observer": "unobserved", "why": "no artifact"}
        state, why = reconciler.obligation_state("ITEM-A", 0, entry, {"records": {}})
        self.assertEqual(reconciler.ATTESTED, state)
        self.assertNotEqual(reconciler.DISCHARGED, state)
        self.assertIn("A. Person", why)

    def test_a_bound_but_failing_artifact_is_observed_not_discharged(self):
        """OBSERVED != DISCHARGED. Binding is not satisfaction."""
        entry = {"declaration": "x", "observer": "retained_artifact", "record": "REC"}
        state, why = reconciler.obligation_state(
            "ITEM-A", 0, entry, self.bound_register(satisfies=None))
        self.assertEqual(reconciler.OBSERVED, state)
        self.assertNotEqual(reconciler.DISCHARGED, state)
        self.assertIn("not declared to satisfy", why)

    def test_only_satisfying_bound_evidence_is_discharged(self):
        entry = {"declaration": "x", "observer": "retained_artifact", "record": "REC"}
        state, _ = reconciler.obligation_state(
            "ITEM-A", 0, entry, self.bound_register(satisfies=True))
        self.assertEqual(reconciler.DISCHARGED, state)

    def test_an_unbound_artifact_is_open_even_when_claimed_satisfying(self):
        """satisfies_obligation cannot rescue a record whose artifact does not verify."""
        register = self.bound_register(satisfies=True)
        register["records"]["REC"]["artifacts"][0]["sha256"] = "0" * 64
        entry = {"declaration": "x", "observer": "retained_artifact", "record": "REC"}
        state, why = reconciler.obligation_state("ITEM-A", 0, entry, register)
        self.assertEqual(reconciler.OPEN, state)
        self.assertIn("hash mismatch", why)

    def test_only_discharged_closes(self):
        self.assertEqual(frozenset({reconciler.DISCHARGED}), reconciler.CLOSING_STATES)
        for state in (reconciler.OPEN, reconciler.ATTESTED, reconciler.OBSERVED):
            self.assertNotIn(state, reconciler.CLOSING_STATES)


class DerivedMetrics(unittest.TestCase):
    """Aggregates must be recomputed from their populations, never preserved."""

    def test_asserted_aggregates_agree_with_their_populations(self):
        import report_assurance_metrics as metrics

        explicit, entities, claims = metrics.construction_population()
        asserted = metrics.asserted_aggregates()
        self.assertEqual(asserted["records"], entities)
        self.assertEqual(asserted["vv_claims"], claims)
        self.assertEqual(asserted["source_explicit_hazard_sets"], explicit)

    def test_acceptance_items_derive_from_item_state(self):
        import report_assurance_metrics as metrics

        complete, total, states = metrics.acceptance_items()
        self.assertEqual(complete, states.get("complete", 0))
        self.assertEqual(total, sum(states.values()))
        self.assertEqual(0, states.get("blocked", 0),
                         "reopened items have identifiable work remaining, not blockers")

    def test_obligations_count_only_discharged(self):
        import report_assurance_metrics as metrics

        discharged, total, states = metrics.evidence_obligations()
        self.assertEqual(discharged, states.get(reconciler.DISCHARGED, 0))
        self.assertEqual(total, sum(states.values()))
        # An observer that reports everything discharged is not an observer.
        self.assertLess(discharged, total)

    def test_no_metric_is_hard_coded_in_the_reporter(self):
        """The numbers must come from the populations, not from the source of the reporter."""
        source = (REPO_ROOT / "tools" / "spec"
                  / "report_assurance_metrics.py").read_text(encoding="utf-8")
        for forbidden in (r"\b11\s*/\s*16\b", r"\b17\s*/\s*25\b", r"\b76\s*/\s*2", r"= *2144\b"):
            self.assertIsNone(re.search(forbidden, source),
                              f"reporter must not hard-code {forbidden}")


if __name__ == "__main__":
    unittest.main()
