"""The two-verdict currency gate, and the test-family population ledger.

Both controls exist because of failures this programme observed rather than imagined. The
currency gate keeps the build verdict and the model-test verdict apart, because a build that
completes over a model the checker rejects has already happened here. The family ledger
requires every declared test family to carry an explicit state, because a family nobody
populates would otherwise vanish by silence -- the same hole as a task passing over zero
selected tests, one level up.

Every negative control below damages the evidence and requires the gate to fail. A gate
never shown to fail is indistinguishable from one that cannot.
"""
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "mps" / "check_headless_build_currency.py"
EVIDENCE = REPO_ROOT / "mps" / "materialization" / "headless-acceptance-evidence.json"
PLAN = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"

VALID_STATES = {"materialized", "not-yet-materialized", "not-applicable"}


def run_gate():
    return subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True,
                          cwd=str(REPO_ROOT))


class CurrencyGateTest(unittest.TestCase):
    def _damaged(self, mutate, expect):
        original = EVIDENCE.read_text(encoding="utf-8")
        try:
            evidence = json.loads(original)
            mutate(evidence)
            EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8", newline="")
            result = run_gate()
            self.assertEqual(1, result.returncode,
                             "the gate accepted damaged evidence")
            self.assertIn(expect, result.stderr)
        finally:
            EVIDENCE.write_text(original, encoding="utf-8", newline="")
        self.assertEqual(original, EVIDENCE.read_text(encoding="utf-8"))

    def test_passes_as_committed(self):
        result = run_gate()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_a_build_verdict_cannot_substitute_for_the_model_test_verdict(self):
        """The defect this gate exists for.

        A green build over a model the checker rejects has actually occurred here. If the
        model-test branch may be absent while the build branch is green, the gate would
        report acceptance evidence current on generation alone.
        """
        self._damaged(lambda e: e.pop("model_tests"),
                      "generation is not checking")

    def test_a_model_test_verdict_cannot_substitute_for_the_build_verdict(self):
        self._damaged(lambda e: e.pop("build"), "the build verdict is absent")

    def test_stale_verdict_is_rejected(self):
        self._damaged(
            lambda e: e["model_tests"].update({"model_tree_sha256": "0" * 64}),
            "so it is stale")

    def test_zero_executed_is_not_a_pass(self):
        def mutate(e):
            e["model_tests"].update({"authored": 0, "discovered": 0, "executed": 0})
        self._damaged(mutate, "empty population")

    def test_population_disagreement_is_rejected(self):
        self._damaged(lambda e: e["model_tests"].update({"discovered": 1}),
                      "authored/discovered/executed disagree")

    def test_halt_on_failure_required(self):
        self._damaged(lambda e: e["model_tests"].update({"halt_on_failure": False}),
                      "haltOnFailure is not set")

    def test_recorded_identities_match_the_frozen_population(self):
        with io.open(EVIDENCE, encoding="utf-8") as handle:
            evidence = json.load(handle)
        identities = evidence["model_tests"]["identities"]
        self.assertEqual(2, len(identities))
        self.assertTrue(any("testAssessedClaimWithoutEvidenceIsRejected" in i
                            for i in identities), identities)
        self.assertTrue(any("REA_C_002" in i and i.startswith("test_S1")
                            for i in identities), identities)


class TestFamilyLedgerTest(unittest.TestCase):
    """No declared family may disappear by nobody populating its status."""

    def _families(self):
        import yaml

        with io.open(PLAN, encoding="utf-8") as handle:
            plan = yaml.safe_load(handle.read())

        def walk(node):
            if isinstance(node, dict):
                if "test_family_status" in node:
                    return node["test_family_status"]
                for value in node.values():
                    found = walk(value)
                    if found is not None:
                        return found
            elif isinstance(node, list):
                for value in node:
                    found = walk(value)
                    if found is not None:
                        return found
            return None

        ledger = walk(plan)
        self.assertIsNotNone(ledger, "no test_family_status ledger in the checklist")
        return ledger

    def test_every_family_carries_an_explicit_state(self):
        ledger = self._families()
        families = ledger["families"]
        self.assertTrue(families)
        for entry in families:
            self.assertIn("family", entry)
            self.assertIn(entry.get("state"), VALID_STATES,
                          f"{entry.get('family')} has state {entry.get('state')!r}")
            self.assertIn("mechanism", entry, entry.get("family"))

    def test_a_materialized_family_carries_evidence_and_others_carry_rationale(self):
        for entry in self._families()["families"]:
            if entry["state"] == "materialized":
                self.assertTrue(entry.get("evidence", "").strip(),
                                f"{entry['family']} is materialized with no evidence")
            else:
                self.assertTrue(entry.get("rationale", "").strip(),
                                f"{entry['family']} is {entry['state']} with no rationale")

    def test_the_ledger_is_not_uniformly_green(self):
        """Not an assertion about the world; an assertion about this ledger's honesty.

        If every family were materialized the ledger would be indistinguishable from one
        that was filled in by default. Four of six are not, and the item claims only the
        two that are.
        """
        states = [entry["state"] for entry in self._families()["families"]]
        self.assertIn("materialized", states)
        self.assertIn("not-yet-materialized", states)


class TestFamilyReconciliationTest(unittest.TestCase):
    """Nothing may cross between the two populations by silence, in either direction."""

    TOOL = REPO_ROOT / "tools" / "mps" / "check_test_family_reconciliation.py"
    BLUEPRINT = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"

    def _run(self):
        return subprocess.run([sys.executable, str(self.TOOL)], capture_output=True,
                              text=True, cwd=str(REPO_ROOT))

    def test_passes_as_committed(self):
        result = self._run()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_reports_undecided_families_every_run(self):
        """An undecided disposition must stay visible, not merely pass.

        The whole reason undecided is allowed is that inferring a disposition would be
        worse. That only holds while the gate keeps saying which ones are open.
        """
        result = self._run()
        self.assertIn("OPEN:", result.stdout)
        self.assertIn("ARCH-INVARIANT-001-no-language-equivalence", result.stdout)

    def test_a_blueprint_family_without_a_disposition_fails(self):
        original = self.BLUEPRINT.read_text(encoding="utf-8")
        try:
            data = json.loads(original)
            data["initial_test_families"].append("injected-control-family")
            self.BLUEPRINT.write_text(json.dumps(data, indent=2) + "\n",
                                      encoding="utf-8", newline="")
            result = self._run()
            self.assertEqual(1, result.returncode,
                             "a declared family with no disposition was accepted")
            self.assertIn("has no disposition", result.stderr)
        finally:
            self.BLUEPRINT.write_text(original, encoding="utf-8", newline="")
        self.assertEqual(original, self.BLUEPRINT.read_text(encoding="utf-8"))

    def test_a_ledger_family_without_a_stated_basis_fails(self):
        original = PLAN.read_text(encoding="utf-8")
        anchor = "                - family: node-and-constraint-tests\n"
        self.assertIn(anchor, original)
        injected = ("                - family: injected-ledger-family\n"
                    "                  mechanism: none\n"
                    "                  state: not-yet-materialized\n"
                    "                  rationale: negative control\n")
        try:
            PLAN.write_text(original.replace(anchor, injected + anchor, 1),
                            encoding="utf-8", newline="")
            result = self._run()
            self.assertEqual(1, result.returncode,
                             "an operational family with no stated basis was accepted")
            self.assertIn("without a stated basis", result.stderr)
        finally:
            PLAN.write_text(original, encoding="utf-8", newline="")
        self.assertEqual(original, PLAN.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
