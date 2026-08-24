"""The first dedicated observer of the MPS-MAT-009 artifacts as a review-record population.

Generic readers already reached these files before this control existed. check_path_citations
acquires them through its ("mps/materialization", ("*.yaml",)) glob, and the repository
hygiene gate acquires them through git ls-files; both were resolving all nine as members
while a literal search for the directory name returned nothing. What did not exist was any
observer that treated them AS review records -- that checked review-result consistency across
the population rather than merely enumerating the files.

    generic enumeration of files  !=  semantic observation of those files as review records

That distinction is the whole of REC-OBS-01, and the earlier, stronger claim -- that nothing
read them at all -- was false. It came from inferring absence of readers from absence of a
literal reference, which cannot be done: a reader may acquire its target through a parent
glob, a recursive walk, tracked-file enumeration, or any other broader population definition.
A name search is a recall aid; membership is established by resolving the candidate reader's
actual population.

What this observer establishes is membership and completeness of the review population, and
-- since the RT-F-01/02/07 transport -- that an open finding carries enough substance to be
disposed of from a clone. It does not establish that any adjudication is sound, that any
finding is true, that evidence is adequate, that a disposition is correct, or that the
external review events happened as recorded. PopulationObserved does not imply
AdjudicationSound, which is why REC-OBS-01 stays open.

The property is NOT "every repair must carry a verdict" -- PENDING is legitimate, and a
review that has not happened must not be forced to produce one. It is that a reviewed
population must be represented uniformly, because once the field exists on some members and
not others, absence starts carrying meaning it was never given.

Two populations, one classification structure:

    E = every review entry declared in independent-reviews.yaml
    F = every reviewable_units member whose kind is record_file_backed

Both are derived from population.reviewable_units, which is the single authoritative
classification. A commit-scoped review has no backing record file and is discoverable only
through that declaration; a population derived from record files alone could not see it, and
requiring a synthetic file to make it visible would be manufacturing evidence to satisfy an
observer.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

import yaml

# NF-23. This module used to carry its own reading of the review-object identity fields,
# `obj.get("sha") or obj.get("later_committed_as")`, which is the semantics C8 withdrew from
# the closure observer and did not withdraw from here. The two disagreed on seven of ten
# shapes -- a falsy sha with a usable later_committed_as, a commit carrying only
# later_committed_as, a working_tree carrying only sha -- so this control accepted identities
# the closure rule rejects while asserting that every review identifies what it reviewed.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from controlled_field_semantics import (  # noqa: E402
    IDENTITY_FIELD_BY_KIND,
    reviewed_identity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = REPO_ROOT / "mps" / "materialization" / "mps-mat-009"
REVIEWS = RECORD_DIR / "independent-reviews.yaml"

LEGITIMATE_VERDICTS = {"PENDING", "FAIL", "INDEPENDENTLY VERIFIED"}
MEMBERSHIP_KINDS = {"record_file_backed", "commit_scoped"}
REQUIRED_REVIEWER_FIELDS = (
    "relationship", "identity", "satisfies_mps_mat_009_named_reviewer_obligation",
)


def register() -> dict:
    return yaml.safe_load(REVIEWS.read_text(encoding="utf-8"))


def entries(body: dict) -> set[str]:
    """E: every review declared in the register."""
    return {review["review_id"] for review in body["reviews"]}


def file_backed_units(body: dict) -> dict[str, str]:
    """F: review id -> record path, for units backed by a controlled record file."""
    return {unit["review"]: unit["record"]
            for unit in body["population"]["reviewable_units"]
            if unit["kind"] == "record_file_backed"}


def commit_scoped_units(body: dict) -> set[str]:
    return {unit["review"] for unit in body["population"]["reviewable_units"]
            if unit["kind"] == "commit_scoped"}


def reconcile(body: dict) -> list[str]:
    """Both directions, plus the classification rules. Empty means consistent."""
    problems: list[str] = []
    declared = entries(body)
    backed = file_backed_units(body)

    for unit in body["population"]["reviewable_units"]:
        kind = unit.get("kind")
        if kind not in MEMBERSHIP_KINDS:
            problems.append(f"reviewable unit declares unknown kind {kind!r}")
            continue
        if kind == "record_file_backed":
            if not unit.get("record"):
                problems.append(f"{unit.get('review')}: record_file_backed with no record")
            elif not (REPO_ROOT / unit["record"]).is_file():
                problems.append(f"{unit['review']}: record {unit['record']} does not exist")
        if unit["review"] not in declared:
            problems.append(f"{unit['review']}: declared as a reviewable unit but has no "
                            f"entry in the review register")

    known_units = {unit["review"] for unit in body["population"]["reviewable_units"]}
    for review_id in declared:
        if review_id not in known_units:
            problems.append(f"{review_id}: review entry names no declared reviewable unit")

    # Directory classification, over record-backed units only: commit-scoped units have no
    # record path to classify.
    classified = set(backed.values()) | set(
        body["population"]["supporting_records"]["records"])
    on_disk = {str(p.relative_to(REPO_ROOT)).replace("\\", "/")
               for p in RECORD_DIR.glob("*.yaml")}
    for path in sorted(on_disk - classified):
        problems.append(f"{path}: present in the record directory and classified neither as "
                        f"a record-backed reviewable unit nor as a supporting record")
    for path in sorted(classified - on_disk):
        problems.append(f"{path}: classified in the register but absent from disk")
    return problems


class TheRegisterAsCommitted(unittest.TestCase):

    def test_the_populations_reconcile_in_both_directions(self):
        self.assertEqual([], reconcile(register()))

    def test_both_membership_kinds_are_present(self):
        """Otherwise the commit-scoped path is untested by the real data."""
        body = register()
        self.assertTrue(file_backed_units(body))
        self.assertTrue(commit_scoped_units(body))

    def test_a_filename_pattern_would_not_reproduce_the_population(self):
        backed = set(file_backed_units(register()).values())
        glob_would_match = {str(p.relative_to(REPO_ROOT)).replace("\\", "/")
                            for p in RECORD_DIR.glob("*-repair.yaml")}
        self.assertIn("mps/materialization/mps-mat-009/f2-observability.yaml",
                      backed - glob_would_match)


class MutationControls(unittest.TestCase):
    """RT-F-06, proven by disposable mutation of the loaded register.

    No control here depends on a hard-coded list of review ids; completeness is derived from
    the declaration each time.
    """

    def setUp(self):
        self.body = register()

    def test_A_a_commit_scoped_entry_with_no_record_file_is_accepted(self):
        body = copy.deepcopy(self.body)
        body["population"]["reviewable_units"].append({
            "kind": "commit_scoped", "reviewed_object": "0" * 40, "review": "REV-SYNTHETIC"})
        body["reviews"].append({
            "review_id": "REV-SYNTHETIC", "subject": "x",
            "reviewed_object": {"kind": "commit", "sha": "0" * 40},
            "verdict": "PENDING",
            "reviewer": {"relationship": "r", "identity": "unnamed",
                         "satisfies_mps_mat_009_named_reviewer_obligation": False},
            "primary_artifact_retention": "external_not_retained"})
        self.assertEqual([], reconcile(body))
        self.assertIn("REV-SYNTHETIC", entries(body))

    def test_B_a_record_backed_unit_with_no_register_entry_fails(self):
        body = copy.deepcopy(self.body)
        body["population"]["reviewable_units"].append({
            "kind": "record_file_backed",
            "record": "mps/materialization/mps-mat-009/findings.yaml",
            "review": "REV-UNRECORDED"})
        problems = reconcile(body)
        self.assertTrue(any("has no entry in the review register" in p for p in problems))

    def test_C_a_record_backed_entry_pointing_at_a_nonexistent_record_fails(self):
        body = copy.deepcopy(self.body)
        body["population"]["reviewable_units"].append({
            "kind": "record_file_backed",
            "record": "mps/materialization/mps-mat-009/absent.yaml",
            "review": "REV-GHOST"})
        body["reviews"].append({"review_id": "REV-GHOST", "verdict": "PENDING"})
        problems = reconcile(body)
        self.assertTrue(any("does not exist" in p for p in problems))

    def test_D_a_new_record_backed_unit_enters_F_without_editing_an_id_list(self):
        body = copy.deepcopy(self.body)
        before = set(file_backed_units(body))
        body["population"]["reviewable_units"].append({
            "kind": "record_file_backed",
            "record": "mps/materialization/mps-mat-009/adjudication.yaml",
            "review": "REV-NEW"})
        after = set(file_backed_units(body))
        self.assertEqual({"REV-NEW"}, after - before,
                         "F is derived from the declaration, not from a maintained list")

    def test_E_removing_an_entry_for_a_known_file_backed_unit_fails(self):
        body = copy.deepcopy(self.body)
        victim = sorted(file_backed_units(body))[0]
        body["reviews"] = [r for r in body["reviews"] if r["review_id"] != victim]
        problems = reconcile(body)
        self.assertTrue(any(victim in p and "no entry in the review register" in p
                            for p in problems))

    def test_F_an_unclassified_file_in_the_directory_still_fails(self):
        body = copy.deepcopy(self.body)
        body["population"]["supporting_records"]["records"] = [
            r for r in body["population"]["supporting_records"]["records"]
            if not r.endswith("adjudication.yaml")]
        problems = reconcile(body)
        self.assertTrue(any("adjudication.yaml" in p and "classified neither" in p
                            for p in problems))


class VerdictsAreFromAnExplicitStateSpace(unittest.TestCase):

    def test_every_review_carries_a_legitimate_verdict(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIn(review["verdict"], LEGITIMATE_VERDICTS)

    def test_pending_is_legitimate(self):
        self.assertIn("PENDING", LEGITIMATE_VERDICTS)
        self.assertIn("PENDING", register()["verdict_vocabulary"])

    def test_every_review_identifies_the_object_it_reviewed(self):
        """NF-23. Resolved through the shared semantics, not a second reading of them."""
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                obj = review["reviewed_object"]
                self.assertIn(obj["kind"], set(IDENTITY_FIELD_BY_KIND))
                value, problem = reviewed_identity(review)
                self.assertIsNone(problem, problem)
                self.assertTrue(value)

    def test_membership_kind_is_not_object_identity_strength(self):
        """Two dimensions, and the data exercises their independence."""
        body = register()
        reviews = {r["review_id"]: r for r in body["reviews"]}
        backed = file_backed_units(body)
        self.assertEqual("working_tree", reviews["REV-F2"]["reviewed_object"]["kind"])
        self.assertIn("REV-F2", backed, "record-backed, yet only working-tree identified")
        self.assertEqual("commit",
                         reviews["REV-MI-EXIT-01-R1"]["reviewed_object"]["kind"])
        self.assertIn("REV-MI-EXIT-01-R1", commit_scoped_units(body),
                      "commit-scoped, and SHA-bound")


class IndependenceIsNotNamedAuthority(unittest.TestCase):

    def test_every_review_separates_relationship_from_identity(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                for field in REQUIRED_REVIEWER_FIELDS:
                    self.assertIn(field, review["reviewer"])

    def test_no_review_claims_to_satisfy_the_named_reviewer_obligation(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIs(
                    False,
                    review["reviewer"]["satisfies_mps_mat_009_named_reviewer_obligation"])

    def test_no_reviewer_has_been_given_an_invented_identity(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIn("unnamed", review["reviewer"]["identity"].casefold())

    def test_the_named_reviewer_obligation_is_still_open(self):
        import sys

        sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
        import check_evidence_reconciliation as reconciler

        state, _ = reconciler.states()["MPS-MAT-009#0"]
        self.assertEqual("OPEN", state)


class TheFailedReviewIsFirstClass(unittest.TestCase):
    """A population of only passes cannot be told apart from a process that ratifies."""

    def test_the_round_one_failure_is_retained_as_its_own_result(self):
        reviews = {r["review_id"]: r for r in register()["reviews"]}
        failed = reviews["REV-MI-EXIT-01-R1"]
        self.assertEqual("FAIL", failed["verdict"])
        self.assertEqual("ae475138c77f9bcc6fb6508d90b4dafcc10a5cba",
                         failed["reviewed_object"]["sha"])
        self.assertTrue(failed.get("first_class_result"))

    def test_the_failed_and_passing_objects_are_different_commits(self):
        reviews = {r["review_id"]: r for r in register()["reviews"]}
        self.assertNotEqual(reviews["REV-MI-EXIT-01-R1"]["reviewed_object"]["sha"],
                            reviews["REV-MI-EXIT-01-R2"]["reviewed_object"]["sha"])

    def test_the_population_retains_an_adverse_verdict(self):
        """Stronger than asserting the population is non-empty."""
        self.assertIn("FAIL", {r["verdict"] for r in register()["reviews"]})


class EvidenceProvenanceIsPreserved(unittest.TestCase):

    def test_every_review_states_whether_its_primaries_were_retained(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIn(review["primary_artifact_retention"],
                              {"retained", "external_not_retained", "reproduction"})

    def test_controlled_support_paths_resolve(self):
        for review in register()["reviews"]:
            for cited in review.get("controlled_support") or []:
                with self.subTest(review=review["review_id"], path=cited):
                    self.assertTrue((REPO_ROOT / cited).exists(), cited)

    def test_the_verbatim_review_sentence_is_preserved(self):
        reviews = {r["review_id"]: r for r in register()["reviews"]}
        self.assertEqual(
            "The verification apparatus became correct; no assurance number moved because "
            "of it.",
            reviews["REV-MI-EXIT-01-R2"]["verbatim_review_statement"].strip())



# ---------------------------------------------------------------------------------------
# Second property: an open finding must be actionable from a clone.
#
# The review register says which reviews happened. It says nothing about whether the findings
# those reviews produced were transported with enough substance to be disposed of. RT-F-01,
# RT-F-02 and RT-F-07 were carried for a checkpoint as an id, a class and a state -- which
# records that something exists without recording what, and leaves a future actor unable to
# begin. The external review report is not retained and will not be; the fix is therefore not
# to retain it but to require the finding itself to carry its proposition.
#
#     controlled finding is semantically actionable from a clone
#         !=
#     complete external review history is clone-contained
#
# The rule is scoped to OPEN findings on purpose: an open finding is work someone must do, a
# closed one is a record of work done and is read through its disposition. Both the field
# vocabulary and the threshold are declared in findings.yaml rather than written here, so the
# control reads the register's own convention instead of imposing a second one.

FINDINGS = RECORD_DIR / "findings.yaml"


def findings_register() -> dict:
    return yaml.safe_load(FINDINGS.read_text(encoding="utf-8"))


def retention_vocabulary() -> set[str]:
    """One vocabulary, declared once, in the review register. Not re-declared here."""
    return set(register()["evidence_retention_vocabulary"])


def finding_completeness_problems(body: dict) -> list[str]:
    """Derived entirely from the register's declaration. Empty means complete."""
    rules = body["finding_record_completeness"]
    substance_fields = tuple(rules["substance_fields"])
    minimum = int(rules["minimum_substance_characters"])
    vocabulary = retention_vocabulary()

    problems: list[str] = []
    for finding in body["findings"]:
        identifier = finding.get("id", "<unidentified finding>")
        if finding.get("state") == "OPEN":
            carried = [field for field in substance_fields
                       if str(finding.get(field) or "").strip()]
            if not carried:
                problems.append(
                    f"{identifier}: open with no substance field; one of "
                    f"{list(substance_fields)} is required, because an id, a class and a "
                    f"state say that a finding exists without saying what it is")
            elif max(len(str(finding[field]).strip()) for field in carried) < minimum:
                problems.append(
                    f"{identifier}: open, and its substance is shorter than the declared "
                    f"minimum of {minimum} characters")
        if "reviewed_object" in finding:
            retention = finding.get("primary_artifact_retention")
            if retention is None:
                problems.append(
                    f"{identifier}: names a reviewed object but does not state whether that "
                    f"review's primary artifacts were retained")
            elif retention not in vocabulary:
                problems.append(
                    f"{identifier}: primary_artifact_retention {retention!r} is outside the "
                    f"vocabulary declared in independent-reviews.yaml")
    return problems


class OpenFindingsAreActionableFromAClone(unittest.TestCase):

    def test_the_register_as_committed_is_complete(self):
        self.assertEqual([], finding_completeness_problems(findings_register()))

    def test_the_rule_has_open_findings_to_bite_on(self):
        """A completeness rule over an empty population passes without observing anything."""
        body = findings_register()
        self.assertTrue([f for f in body["findings"] if f.get("state") == "OPEN"])

    def test_removing_the_proposition_from_an_open_finding_fails(self):
        """The specified mutation control. RT-F-01 is the witness, not the population."""
        body = copy.deepcopy(findings_register())
        victim = next(f for f in body["findings"] if f["id"] == "RT-F-01")
        for field in body["finding_record_completeness"]["substance_fields"]:
            victim.pop(field, None)
        problems = finding_completeness_problems(body)
        self.assertTrue(any("RT-F-01" in p and "no substance field" in p for p in problems),
                        problems)

    def test_the_same_holds_for_every_open_finding_not_just_the_witness(self):
        """Otherwise the control would be an assertion about one id."""
        base = findings_register()
        open_ids = [f["id"] for f in base["findings"] if f.get("state") == "OPEN"]
        for identifier in open_ids:
            with self.subTest(finding=identifier):
                body = copy.deepcopy(base)
                victim = next(f for f in body["findings"] if f["id"] == identifier)
                for field in body["finding_record_completeness"]["substance_fields"]:
                    victim.pop(field, None)
                self.assertTrue(
                    any(identifier in p and "no substance field" in p
                        for p in finding_completeness_problems(body)))

    def test_a_placeholder_does_not_satisfy_the_rule(self):
        """'To be determined' is an absence with a longer spelling."""
        body = copy.deepcopy(findings_register())
        victim = next(f for f in body["findings"] if f["id"] == "RT-F-01")
        for field in body["finding_record_completeness"]["substance_fields"]:
            victim.pop(field, None)
        victim["claim"] = "TBD"
        problems = finding_completeness_problems(body)
        self.assertTrue(any("RT-F-01" in p and "shorter than the declared minimum" in p
                            for p in problems), problems)

    def test_a_finding_naming_a_reviewed_object_must_state_primary_retention(self):
        body = copy.deepcopy(findings_register())
        victim = next(f for f in body["findings"] if f["id"] == "RT-F-02")
        victim.pop("primary_artifact_retention")
        problems = finding_completeness_problems(body)
        self.assertTrue(any("RT-F-02" in p and "retained" in p for p in problems), problems)

    def test_retention_status_comes_from_the_one_declared_vocabulary(self):
        body = copy.deepcopy(findings_register())
        victim = next(f for f in body["findings"] if f["id"] == "RT-F-02")
        victim["primary_artifact_retention"] = "probably_somewhere"
        self.assertTrue(any("outside the vocabulary" in p
                            for p in finding_completeness_problems(body)))
        self.assertEqual({"retained", "external_not_retained", "reproduction"},
                         retention_vocabulary())

    def test_a_closed_finding_is_not_required_to_carry_a_proposition(self):
        """The rule's scope is a decision, so it is exercised rather than assumed."""
        body = copy.deepcopy(findings_register())
        victim = next(f for f in body["findings"] if f["id"] == "RT-F-08")
        self.assertNotEqual("OPEN", victim["state"])
        for field in body["finding_record_completeness"]["substance_fields"]:
            victim.pop(field, None)
        self.assertEqual([], [p for p in finding_completeness_problems(body)
                              if "RT-F-08" in p and "substance" in p])


class TheExternalPrimaryBoundaryIsStated(unittest.TestCase):
    """What is retained and what is not must be answerable without this session."""

    def test_the_transported_findings_declare_that_their_primary_is_not_retained(self):
        body = findings_register()
        transported = [f for f in body["findings"] if f["id"].startswith("RT-F-")]
        self.assertTrue(transported)
        for finding in transported:
            with self.subTest(finding=finding["id"]):
                self.assertEqual("external_not_retained",
                                 finding["primary_artifact_retention"])

    def test_the_boundary_is_written_and_claims_no_more_than_it_should(self):
        body = findings_register()
        boundary = body["transported_finding_records"]
        for key in ("what_this_is", "the_boundary", "primary_retention",
                    "what_this_does_not_claim"):
            self.assertTrue(str(boundary.get(key) or "").strip(), key)
        self.assertIn("clone-contained", boundary["what_this_does_not_claim"])

    def test_the_retained_009_report_is_not_confused_with_the_unretained_one(self):
        """findings.yaml retains the MPS-MAT-009 report. It does not retain the RT-F one."""
        body = findings_register()
        retained = body["source_review"]["report"]["retained_as"]
        self.assertTrue((REPO_ROOT / retained).is_file(), retained)
        for finding in body["findings"]:
            if finding["id"].startswith("RT-F-"):
                with self.subTest(finding=finding["id"]):
                    self.assertNotIn("review-report.html", str(finding))

if __name__ == "__main__":
    unittest.main()
