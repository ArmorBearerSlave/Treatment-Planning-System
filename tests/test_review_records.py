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
import re
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



class RetainedReviewArtifactBinding(unittest.TestCase):
    """A review declaring `retained` must be bound to the bytes it was read from.

    Every earlier review in this register is external_not_retained, and the consequence is the
    condition REV-C5-CUMULATIVE is in: its per-finding claims cannot be checked against
    anything, because the thing they were read from does not exist here. Retention only fixes
    that if the binding is mechanical. A path and a hash written beside each other in a record
    are two strings until something reads the file and compares.

    So the determinations are not trusted as transcribed. They are extracted from the retained
    bytes TWICE, by independent routes -- the per-finding section headings and the summary
    table -- required to agree with each other, and then required to equal the record's typed
    population exactly, in both directions. A determination the record adds and the artifact
    does not make fails here, and so does one the artifact makes and the record drops.

    The control ranges over every review declaring `retained`, derived from the register, so a
    second retained review is bound the moment it is registered rather than when someone
    remembers to extend a list.
    """

    DETERMINATIONS = {"SUPPORTED", "NOT SUPPORTED", "INDETERMINATE"}

    def retained_reviews(self):
        return [r for r in register()["reviews"]
                if r.get("primary_artifact_retention") == "retained"]

    def artifact_path(self, review) -> Path:
        return REPO_ROOT / review["retained_artifact"]["path"].strip()

    def artifact_bytes(self, review) -> bytes:
        return self.artifact_path(review).read_bytes()

    # ---------------------------------------------------------------- the population is real

    def test_at_least_one_retained_review_exists(self):
        """Otherwise every assertion below is vacuous and would pass over an empty set."""
        self.assertTrue(self.retained_reviews(),
                        "no review declares retained; this control would pass vacuously")

    # ---------------------------------------------------------------- identity of the bytes

    def test_the_artifact_exists_at_the_controlled_locator(self):
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                path = self.artifact_path(review)
                self.assertTrue(path.is_file(), f"{path} is not a file in this repository")

    def test_the_artifact_is_tracked_so_a_clone_resolves_it(self):
        """Retention that a clone cannot obtain is external retention with extra steps."""
        import subprocess

        tracked = subprocess.run(["git", "ls-files", "-z"], capture_output=True,
                                 cwd=str(REPO_ROOT)).stdout.decode().split("\0")
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                rel = review["retained_artifact"]["path"].strip()
                # assertTrue, not assertIn: assertIn renders the entire tracked-file list on
                # failure, which buries the one path that matters in several hundred lines.
                self.assertTrue(rel in tracked,
                                f"{rel} is declared retained but is not tracked, so a clone "
                                f"would not carry it")

    def test_the_digest_matches_the_retained_bytes(self):
        import hashlib

        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                declared = review["retained_artifact"]["sha256"]
                actual = hashlib.sha256(self.artifact_bytes(review)).hexdigest()
                self.assertEqual(declared, actual, "declared digest is not of these bytes")

    def test_the_byte_size_matches(self):
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                self.assertEqual(review["retained_artifact"]["byte_size"],
                                 len(self.artifact_bytes(review)))

    def test_the_retained_bytes_are_what_a_clone_would_carry(self):
        """CLAUDE.md's standing rule: hash what a clone gets, not the working copy.

        MPS writes CRLF and .gitattributes declares eol=lf, so a working-copy digest can
        verify on the machine that computed it and nowhere else. This artifact is pure LF, so
        normalisation is a no-op -- asserted rather than assumed, because the assumption is the
        one that failed at three scales in one session.
        """
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                raw = self.artifact_bytes(review)
                self.assertNotIn(b"\r\n", raw,
                                 "CRLF in a retained artifact makes its digest host-local")

    # ---------------------------------------------------------------- identity of the object

    def test_the_reviewed_object_matches_the_artifact_header(self):
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                sha = reviewed_identity(review)[0]
                self.assertIsNotNone(sha)
                text = self.artifact_bytes(review).decode("utf-8")
                header = text.split("## 1.", 1)[0]
                self.assertIn(sha, header,
                              "the artifact's own header does not name the object the record "
                              "says it reviewed")

    # ---------------------------------------------------------------- the determinations

    def from_section_headings(self, text: str) -> dict:
        found = {}
        blocks = re.split(r"^### Finding:\s*", text, flags=re.M)[1:]
        for block in blocks:
            fid = block.split("\n", 1)[0].strip()
            match = re.search(r"\*\*Determination:\s*([A-Z ]+?)\*\*", block)
            if match:
                found[fid] = match.group(1).strip()
        return found

    def from_summary_table(self, text: str) -> dict:
        found = {}
        for line in text.splitlines():
            cells = [c.strip() for c in line.split("|")]
            if len(cells) < 4:
                continue
            fid, determination = cells[1], cells[2]
            if re.fullmatch(r"NF-\d+", fid) and determination in self.DETERMINATIONS:
                found[fid] = determination
        return found

    def test_the_two_extraction_routes_agree(self):
        """Two independent readings of the same artifact, required to say the same thing."""
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                text = self.artifact_bytes(review).decode("utf-8")
                headings = self.from_section_headings(text)
                table = self.from_summary_table(text)
                self.assertTrue(headings, "no per-finding sections extracted")
                self.assertTrue(table, "no summary table extracted")
                self.assertEqual(headings, table,
                                 "the artifact's own two statements of its determinations "
                                 "disagree, so neither can be transported")

    def test_the_record_population_equals_the_artifact_population(self):
        """Both directions. No extra determination introduced, none omitted."""
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                text = self.artifact_bytes(review).decode("utf-8")
                artifact = self.from_section_headings(text)
                recorded = {d["finding"]: d["determination"]
                            for d in review["per_finding_determinations"]["determinations"]}
                self.assertEqual(set(artifact), set(recorded),
                                 "the record's finding population differs from the artifact's")
                self.assertEqual(artifact, recorded,
                                 "a determination in the record differs from the artifact's")

    def test_every_determination_is_from_the_controlled_vocabulary(self):
        for review in self.retained_reviews():
            for entry in review["per_finding_determinations"]["determinations"]:
                with self.subTest(finding=entry["finding"]):
                    self.assertIn(entry["determination"], self.DETERMINATIONS)

    def test_every_determination_names_a_finding_that_exists(self):
        known = {f["id"] for f in findings_register()["findings"]}
        for review in self.retained_reviews():
            for entry in review["per_finding_determinations"]["determinations"]:
                with self.subTest(finding=entry["finding"]):
                    self.assertIn(entry["finding"], known)

    def test_every_determination_states_a_residual(self):
        """A determination without a residual statement is half an answer."""
        for review in self.retained_reviews():
            for entry in review["per_finding_determinations"]["determinations"]:
                with self.subTest(finding=entry["finding"]):
                    self.assertTrue(str(entry.get("residual", "")).strip(),
                                    "no residual recorded; NONE must be said, not omitted")

    # ---------------------------------------------------------------- support is not closure

    def test_a_supported_determination_confers_no_closure_by_itself(self):
        """Support never moves state on its own. A typed, resolving warrant does.

        AMENDED AT THE DISPOSITION STEP, and the amendment is disclosed rather than quiet.
        The transport-step version asserted that no finding may cite a retained per-finding
        review as its closure_review, and that every SUPPORTED finding must still be OPEN.
        Both were true of the transport commit and neither is a rule of the model: the closure
        rule expressly contemplates a finding naming a review whose reviewed object equals its
        closure target, and a governance actor deciding lifecycle is exactly the authority the
        transport step was deferring to. A control written at one step had encoded that step's
        own invariant as a permanent one -- the same shape as NF-20 and NF-27, in a control
        rather than an observer.

        What is permanent, and is what this now asserts, is the separation of authorities: a
        SUPPORTED determination alone never moves a finding out of OPEN. A finding that has
        left OPEN must carry a typed closure_review that resolves under the closure rule, and
        the closure observer -- untouched by this amendment -- is what decides whether it
        resolves. The substantive guard is therefore stronger here than before, because it
        fails on a SUPPORTED finding closed WITHOUT a resolving warrant, which the previous
        version could not distinguish from one closed with a good one.

        AMENDED AGAIN AT C10B, and this amendment is the third instance of one shape. The
        disposition-step version asserted that a SUPPORTED finding which has left OPEN must name
        THIS review as its warrant. That was true of the disposition and is not a rule: a
        SUPPORTED finding may legitimately close against a different review that grants closure
        authority for it, and this review grants none, so the old clause would have required the
        one warrant the model now forbids. The relation between the two propositions is
        INCOMPARABLE and is stated as such rather than as a strengthening -- NF-34 / IR-04 is
        precisely the finding about describing such a change inaccurately. The old clause accepts
        a SUPPORTED finding closed against this review, which the new one refuses; the new one
        accepts a SUPPORTED finding closed against another granting review, which the old one
        refused. Neither implies the other.
        """
        import sys as _sys

        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_closure_warrant import closure_problems  # noqa: E402
        from controlled_field_semantics import (  # noqa: E402
            closure_authority_problems, grants_closure)

        body, register_body = findings_register(), register()
        states = {f["id"]: f.get("state") for f in body["findings"]}
        warrants = {f["id"]: f.get("closure_review") for f in body["findings"]}
        by_id = {r["review_id"]: r for r in register_body["reviews"]}

        for review in self.retained_reviews():
            rid = review["review_id"]
            with self.subTest(review=rid):
                supported = {d["finding"] for d in
                             review["per_finding_determinations"]["determinations"]
                             if d["determination"] == "SUPPORTED"}
                self.assertTrue(supported, "no SUPPORTED determination to bite on")
                for fid in sorted(supported):
                    self.assertFalse(
                        grants_closure(review, fid, register_body),
                        f"{rid} determines {fid} SUPPORTED and also grants it closure "
                        f"authority; the artifact declares repair support only")
                    if states[fid] == "OPEN":
                        continue
                    warrant = by_id.get(warrants[fid])
                    self.assertIsNotNone(
                        warrant,
                        f"{fid} left OPEN with no resolving warrant; support alone cannot "
                        f"move state")
                    self.assertTrue(
                        grants_closure(warrant, fid, register_body),
                        f"{fid} left OPEN on a warrant that grants it no closure authority")
        # and the warrant must actually resolve, judged by the observers themselves
        self.assertEqual([], closure_problems(body, register_body))
        self.assertEqual([], closure_authority_problems(body, register_body))

    def test_the_retained_determinations_bind_to_the_typed_authority_reading(self):
        """Section 12. The typed reading is DERIVED from the retained bytes, not authored.

        NF-36 / IR-06. per_finding_authority.repair_support is what the completion observer now
        consumes, so if it could drift from the artifact it would be the same defect one level
        along: a remediation-authored value standing where retained reviewer substance belongs.
        The determinations are extracted from the artifact and mapped through the register's own
        controlled retained_determination_to_repair_support table, and the result must equal the
        typed reading exactly, in both directions.
        """
        register_body = register()
        mapping = register_body["per_finding_authority_model"][
            "derived_and_reconciled_fields"]["retained_determination_to_repair_support"]
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                text = self.artifact_bytes(review).decode("utf-8")
                artifact = self.from_section_headings(text)
                self.assertEqual(artifact, self.from_summary_table(text),
                                 "the artifact's two statements disagree")
                expected = {fid: mapping[d] for fid, d in artifact.items()}
                typed = {fid: e["repair_support"]
                         for fid, e in (review.get("per_finding_authority") or {}).items()}
                self.assertEqual(expected, typed,
                                 "the typed repair_support reading is not the retained "
                                 "determination mapped through the controlled table")

    def test_the_binding_fails_when_the_typed_reading_diverges(self):
        """Failure sensitivity for the binding above, in memory.

        Not an on-disk mutation: NF-35 / IR-05 records that restoring a controlled file only in a
        Python finally block leaves it modified if the process dies, and a control added to
        observe that defect should not enlarge it.
        """
        import copy as _copy

        register_body = _copy.deepcopy(register())
        mapping = register_body["per_finding_authority_model"][
            "derived_and_reconciled_fields"]["retained_determination_to_repair_support"]
        review = next(r for r in register_body["reviews"]
                      if r.get("primary_artifact_retention") == "retained")
        text = self.artifact_bytes(review).decode("utf-8")
        artifact = self.from_section_headings(text)
        subject = sorted(artifact)[0]
        review["per_finding_authority"][subject]["repair_support"] = "INDETERMINATE"
        expected = {fid: mapping[d] for fid, d in artifact.items()}
        typed = {fid: e["repair_support"] for fid, e in review["per_finding_authority"].items()}
        self.assertNotEqual(expected, typed,
                            "altering the typed reading must break the binding")

    def test_a_retained_review_grants_no_closure_authority(self):
        """The artifact says repair support only; the typed record must say the same.

        This is the proposition 00c6e2f contradicted. It used this review as the closure warrant
        for four findings while the artifact it is bound to disclaimed exactly that, and nothing
        could see the contradiction because closure authority was never asked for per finding.
        """
        import sys as _sys

        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        from controlled_field_semantics import closure_authority_problems  # noqa: E402

        register_body = register()
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                table = review.get("per_finding_authority") or {}
                self.assertTrue(table, "a retained review declares no per-finding authority")
                for fid, entry in table.items():
                    self.assertNotEqual(
                        "GRANTED", entry.get("closure_authority"),
                        f"{review['review_id']} grants closure authority for {fid} while its "
                        f"retained artifact declares no lifecycle disposition")
                self.assertNotIn("warrants_closure_of", review)
                self.assertEqual([], closure_authority_problems(findings_register(),
                                                                register_body))

    def test_the_reviewer_obligation_is_not_discharged_by_retention(self):
        for review in self.retained_reviews():
            with self.subTest(review=review["review_id"]):
                self.assertIs(
                    False,
                    review["reviewer"]["satisfies_mps_mat_009_named_reviewer_obligation"],
                    "retaining an artifact does not name its reviewer")


if __name__ == "__main__":
    unittest.main()
