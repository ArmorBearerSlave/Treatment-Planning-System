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


class RedStateControlTest(CurrencyGateTest):
    """The red states must be auditable to the same standard as the green one.

    Failure sensitivity and foreign-rule discrimination are the two controls that do the
    most epistemic work in the package, and a green run is silent about both by
    construction: each is a claim about what happens when the assertion should fail. Without
    retained artifacts they would rest on implementer narrative, which is the one source an
    independent reviewer is told not to rely on.
    """

    def test_controls_are_present(self):
        with io.open(EVIDENCE, encoding="utf-8") as handle:
            controls = json.load(handle)["controls"]
        self.assertEqual({"failure_sensitivity", "foreign_rule_discrimination"},
                         set(controls))

    def test_retained_reports_exist_and_match_their_hashes(self):
        import hashlib

        with io.open(EVIDENCE, encoding="utf-8") as handle:
            controls = json.load(handle)["controls"]
        for name, control in controls.items():
            path = REPO_ROOT / control["report"]
            self.assertTrue(path.is_file(), name)
            self.assertEqual(control["report_sha256"],
                             hashlib.sha256(path.read_bytes()).hexdigest(), name)

    def test_retained_reports_are_stored_so_git_cannot_change_them(self):
        """The bytes a reviewer clones must be the bytes the hashes were taken over.

        The first attempt stored these reports with CRLF endings. Git normalises to LF on
        commit, so the committed bytes differed from the working copy and the gate would
        have failed on the fresh clone it exists to serve -- while passing locally. Same
        shape as the restoration residue: the artifact verified here was not the artifact
        delivered there.
        """
        with io.open(EVIDENCE, encoding="utf-8") as handle:
            controls = json.load(handle)["controls"]
        for name, control in controls.items():
            raw = (REPO_ROOT / control["report"]).read_bytes()
            self.assertEqual(0, raw.count(b"\r"),
                             f"{name} report contains CR bytes; git will rewrite it and the "
                             f"recorded hash will not survive a clone")

    def test_missing_controls_are_rejected(self):
        self._damaged(lambda e: e.pop("controls"), "rest on narrative alone")

    def test_a_control_that_did_not_restore_is_rejected(self):
        self._damaged(
            lambda e: e["controls"]["failure_sensitivity"].update(
                {"restored_model_tree_sha256": "0" * 64}),
            "did not restore to the tree it perturbed from")

    def test_a_control_that_perturbed_nothing_is_rejected(self):
        self._damaged(
            lambda e: e["controls"]["failure_sensitivity"].update(
                {"perturbed_model_tree_sha256": e["model_tree_sha256"]}),
            "perturbed nothing")

    def test_a_control_where_the_harness_witness_failed_is_rejected(self):
        """H1 failing makes the run a harness result, whatever S1 did."""
        self._damaged(
            lambda e: e["controls"]["foreign_rule_discrimination"].update({"passing": []}),
            "harness result rather than a semantic one")

    def test_a_control_where_s1_passed_is_rejected(self):
        self._damaged(
            lambda e: e["controls"]["foreign_rule_discrimination"].update(
                {"not_passing": []}),
            "does not demonstrate what it claims")

    def test_a_tampered_report_is_rejected(self):
        self._damaged(
            lambda e: e["controls"]["failure_sensitivity"].update(
                {"report_sha256": "0" * 64}),
            "does not match its recorded hash")


class ArtifactPortabilityTest(CurrencyGateTest):
    """Evidence identity must be computed over the artifact as a reviewer receives it.

    Two failures of this kind occurred. The retained reports were first stored CRLF, so the
    committed bytes differed from the working copy and the hashes verified locally and
    nowhere else. And the two primary hashes pointed into build/work/, which is gitignored
    and which the test target deletes every run -- dangling references to files a reviewer
    could not obtain, while the supporting controls verified, with nothing marking which was
    which. Checking only the paths just changed is what let the second stand.
    """

    def _references(self):
        with io.open(EVIDENCE, encoding="utf-8") as handle:
            evidence = json.load(handle)
        refs = [(evidence["build"], "log"), (evidence["model_tests"], "report")]
        for control in evidence["controls"].values():
            refs.append((control, "report"))
            refs.append((control, "patch"))
        return refs

    def test_every_referenced_artifact_is_committed_and_verifies(self):
        import hashlib
        import subprocess

        for holder, key in self._references():
            reference = holder[key]
            self.assertTrue(reference.startswith("mps/materialization/evidence/"), reference)
            path = REPO_ROOT / reference
            self.assertTrue(path.is_file(), reference)
            self.assertEqual(holder[key + "_sha256"],
                             hashlib.sha256(path.read_bytes()).hexdigest(), reference)
            self.assertEqual(0, path.read_bytes().count(b"\r"), reference)
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", reference],
                                     capture_output=True, cwd=str(REPO_ROOT))
            self.assertEqual(0, tracked.returncode,
                             reference + " is not tracked, so a clone cannot obtain it")

    def test_an_artifact_outside_the_evidence_tree_is_rejected(self):
        self._damaged(
            lambda e: e["build"].update({"log": "build/work/green-make.log"}),
            "dangling reference")

    def test_each_control_binds_its_patch_to_its_observation(self):
        with io.open(EVIDENCE, encoding="utf-8") as handle:
            controls = json.load(handle)["controls"]
        for name, control in controls.items():
            self.assertTrue(control["patch_reproduces_perturbed_tree"], name)
            self.assertNotEqual(control["base_model_tree_sha256"],
                                control["perturbed_model_tree_sha256"], name)

    def test_an_unbound_intervention_is_rejected(self):
        self._damaged(
            lambda e: e["controls"]["failure_sensitivity"].update(
                {"patch_reproduces_perturbed_tree": False}),
            "not bound to the observation")


class ModelTreeHashTest(unittest.TestCase):
    """The currency key must not depend on how the checkout wrote line endings.

    MPS writes CRLF; .gitattributes declares eol=lf so the repository stores LF; git
    therefore reports a clean tree while 184 of 185 controlled files differ byte-for-byte
    from what a clone receives. Hashing raw bytes produced a key that verified only on the
    machine that computed it.
    """

    def test_hash_is_line_ending_invariant(self):
        import shutil
        import sys
        import tempfile

        sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
        import headless_build

        source = REPO_ROOT / "mps" / "NLTPSGovernance"
        base = headless_build.model_tree_hash(source)
        holder = Path(tempfile.mkdtemp())
        try:
            copy = holder / "proj"
            shutil.copytree(source, copy)
            flipped = 0
            for path in headless_build.controlled_files(copy):
                raw = path.read_bytes()
                other = (raw.replace(b"\r\n", b"\n") if b"\r" in raw
                         else raw.replace(b"\n", b"\r\n"))
                if other != raw:
                    path.write_bytes(other)
                    flipped += 1
            self.assertGreater(flipped, 0, "nothing flipped; the control proves nothing")
            self.assertEqual(base, headless_build.model_tree_hash(copy))
        finally:
            shutil.rmtree(holder, ignore_errors=True)


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
