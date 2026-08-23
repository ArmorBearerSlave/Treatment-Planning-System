"""The first mechanical reader of the MPS-MAT-009 remediation record.

Nothing in tools/, tests/ or .github/ read anything under mps/materialization/mps-mat-009/.
Nine files -- the controlled finding register, every adjudication, every repair record, every
observation and every review disposition -- and not one reader, while the neighbouring
registers had between two and fifteen. The record that argues most insistently that a
declaration without an observer is worth nothing was itself the part of the repository
nothing observed. REC-OBS-01.

This closes one property of that gap and no more: that the independently reviewed population
is represented consistently. The substance of the adjudications, dispositions and findings
remains unobserved, and REC-OBS-01 stays open to keep that visible.

The property is worth stating precisely. It is NOT "every repair must carry a verdict" --
PENDING is a legitimate state and a review that has not happened must not be forced to
produce one. It is that a reviewed population must be represented uniformly, because the
moment the field exists on some members and not others, absence starts carrying meaning it
was never given. A reader is then entitled to infer "not reviewed" from silence, and that
inference was false for F1, F5 and MI-EXIT-01, all of which had been reviewed.

The population is content-defined and enumerated, deliberately. A *-repair.yaml glob would
have matched f1-repair and f5-repair and missed f2-observability -- the single record that
already carried a verdict. A pattern-based population would have excluded the one member
that already had what the others lacked, and a file added later would escape by not matching,
which is the same silence the control exists to end.
"""
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = REPO_ROOT / "mps" / "materialization" / "mps-mat-009"
REVIEWS = RECORD_DIR / "independent-reviews.yaml"

LEGITIMATE_VERDICTS = {"PENDING", "FAIL", "INDEPENDENTLY VERIFIED"}

REQUIRED_REVIEWER_FIELDS = (
    "relationship",
    "identity",
    "satisfies_mps_mat_009_named_reviewer_obligation",
)


def register() -> dict:
    return yaml.safe_load(REVIEWS.read_text(encoding="utf-8"))


class ThePopulationIsDefinedAndComplete(unittest.TestCase):

    def test_every_record_in_the_directory_is_classified(self):
        """Unclassified is an error, so a new file cannot escape by not matching a pattern."""
        body = register()
        population = body["population"]
        classified = {entry["record"] for entry in population["reviewable_units"]}
        classified |= set(population["supporting_records"]["records"])

        on_disk = {
            str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            for path in RECORD_DIR.glob("*.yaml")
        }
        self.assertEqual(
            set(), on_disk - classified,
            "records present in the remediation record directory but classified neither as "
            "reviewable units nor as supporting records")
        self.assertEqual(
            set(), classified - on_disk,
            "records classified in the register that do not exist on disk")

    def test_a_record_is_not_classified_twice(self):
        population = register()["population"]
        units = [entry["record"] for entry in population["reviewable_units"]]
        supporting = population["supporting_records"]["records"]
        self.assertEqual(set(), set(units) & set(supporting))

    def test_the_population_is_not_derivable_from_a_filename_pattern(self):
        """The reason the population is enumerated rather than globbed."""
        units = {entry["record"] for entry in register()["population"]["reviewable_units"]}
        glob_would_match = {
            str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            for path in RECORD_DIR.glob("*-repair.yaml")
        }
        missed = units - glob_would_match
        self.assertTrue(
            missed,
            "if a *-repair.yaml glob covered the whole population, this control would be "
            "asserting a property that no longer holds and should be revisited")
        self.assertIn("mps/materialization/mps-mat-009/f2-observability.yaml", missed)


class EveryReviewableUnitIsRepresented(unittest.TestCase):

    def test_each_reviewable_unit_names_a_review(self):
        body = register()
        known = {entry["review_id"] for entry in body["reviews"]}
        for unit in body["population"]["reviewable_units"]:
            with self.subTest(record=unit["record"]):
                self.assertIn(unit["review"], known)

    def test_no_reviewable_unit_is_silently_absent(self):
        """The asymmetry this control exists to prevent."""
        body = register()
        represented = {unit["review"] for unit in body["population"]["reviewable_units"]}
        self.assertEqual(len(represented), len(body["population"]["reviewable_units"]),
                         "two reviewable units share one review record")


class VerdictsAreFromAnExplicitStateSpace(unittest.TestCase):

    def test_every_review_carries_a_legitimate_verdict(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIn(review["verdict"], LEGITIMATE_VERDICTS)

    def test_pending_is_legitimate(self):
        """A review that has not happened must not be forced to produce a verdict."""
        self.assertIn("PENDING", LEGITIMATE_VERDICTS)
        self.assertIn("PENDING", register()["verdict_vocabulary"])

    def test_every_review_names_the_object_it_reviewed(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertTrue(str(review.get("reviewed_object", "")).strip())


class IndependenceIsNotNamedAuthority(unittest.TestCase):
    """The distinction that stops a technical verdict discharging a human obligation."""

    def test_every_review_separates_relationship_from_identity(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                reviewer = review["reviewer"]
                for field in REQUIRED_REVIEWER_FIELDS:
                    self.assertIn(field, reviewer)

    def test_no_review_claims_to_satisfy_the_named_reviewer_obligation(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIs(
                    False,
                    review["reviewer"]["satisfies_mps_mat_009_named_reviewer_obligation"],
                    "an unnamed reviewer cannot satisfy an obligation whose whole content is "
                    "that the reviewer be named")

    def test_no_reviewer_has_been_given_an_invented_identity(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIn("unnamed", review["reviewer"]["identity"].casefold())

    def test_the_named_reviewer_obligation_is_still_open(self):
        """A verified review population must not have moved MPS-MAT-009#0."""
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
                         failed["reviewed_object"])
        self.assertTrue(failed.get("first_class_result"))

    def test_the_failed_and_passing_objects_are_different_commits(self):
        reviews = {r["review_id"]: r for r in register()["reviews"]}
        self.assertNotEqual(reviews["REV-MI-EXIT-01-R1"]["reviewed_object"],
                            reviews["REV-MI-EXIT-01-R2"]["reviewed_object"])

    def test_at_least_one_verdict_in_the_population_is_not_a_pass(self):
        verdicts = {r["verdict"] for r in register()["reviews"]}
        self.assertIn("FAIL", verdicts,
                      "a review record containing only passes is evidence about the record, "
                      "not about the work")


class EvidenceProvenanceIsPreserved(unittest.TestCase):

    def test_every_review_states_whether_its_primaries_were_retained(self):
        for review in register()["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIn(review["primary_artifact_retention"],
                              {"retained", "external_not_retained", "reproduction"})

    def test_controlled_support_paths_resolve(self):
        """Nothing may cite a path a clone cannot open."""
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


if __name__ == "__main__":
    unittest.main()
