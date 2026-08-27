"""Per-finding review authority, and verification of a changed mechanism before it is used.

NF-33 / IR-03. At 00c6e2f four findings were moved to CLOSED against REV-3188A11-PER-FINDING,
whose own retained artifact states its scope as "repair support only; not lifecycle disposition"
and which grants closure authority to nothing. Every control reported clean, because closure
authority was never asked for per finding: the observer required a resolving reference, exact
object identity and a closing review-LEVEL verdict, and a review-level verdict says the review
passed, not that it authorized anything about a particular finding. An arbitrary pairing was
accepted too -- NF-12 set CLOSED against the same review returned zero problems.

NF-36 / IR-06. Repair support was read from REV-C5-CUMULATIVE.verified_repairs_of: a list written
after the fact by the remediation actor, over a review whose primary artifact was never retained,
whose per-finding claims the independent reviewer classified INDETERMINATE at C7, C8 and C9. The
one review that does carry determinations extracted from its own retained bytes was read by
nothing.

NF-31 / IR-01. The rule that a changed closure model must be independently verified before it
next moves lifecycle state had no mechanism at all. No review declared what it verified, so the
condition could only be satisfied by implication from a cumulative review of a descendant object
-- ancestry reasoning, which this register refuses everywhere else.

The controls here are all in-memory. Nothing on disk is mutated, which is deliberate: NF-35 /
IR-05 records that the committed mutation helper restores only in a Python finally block, so a
terminated process leaves controlled files modified. A new observer written in that style would
enlarge a defect this checkpoint is recording.
"""
from __future__ import annotations

import ast
import copy
import inspect
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from controlled_field_semantics import (  # noqa: E402
    AUTHORITY_SOURCE_FIELD,
    DERIVED_GRANT_FIELD,
    LEGACY_SUPPORT_FIELD,
    authority_model,
    authority_reconciliation_problems,
    authority_vocabulary_problems,
    closure_authority_problems,
    grants_closure,
    mechanism_verification_problems,
    per_finding_authority,
    verifies_repair,
)

RECORD_DIR = REPO_ROOT / "mps" / "materialization" / "mps-mat-009"
REVIEWS = RECORD_DIR / "independent-reviews.yaml"
FINDINGS = RECORD_DIR / "findings.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class _DuplicateKeyLoader(yaml.SafeLoader):
    """PyYAML silently keeps the last of two identical mapping keys.

    A second authority determination for the same finding would therefore overwrite the first and
    leave no trace, so a duplicate is invisible to every observer that reads the parsed document.
    This loader is the only place that can see it, because it looks at the mapping before the
    dictionary exists.
    """


def _no_duplicates(loader, node, deep=False):
    seen, mapping = set(), {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key {key!r}", key_node.start_mark)
        seen.add(key)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_DuplicateKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


class TheRecordAsCommitted(unittest.TestCase):
    """The committed register satisfies every authority predicate."""

    def setUp(self):
        self.findings, self.register = load(FINDINGS), load(REVIEWS)

    def test_the_authority_vocabulary_is_respected(self):
        self.assertEqual([], authority_vocabulary_problems(self.register))

    def test_the_convenience_lists_reconcile(self):
        self.assertEqual([], authority_reconciliation_problems(self.register))

    def test_every_closed_finding_carries_a_positive_grant(self):
        self.assertEqual([], closure_authority_problems(self.findings, self.register))

    def test_mechanism_verification_holds_for_every_non_grandfathered_closure(self):
        self.assertEqual([], mechanism_verification_problems(self.findings, self.register))

    def test_the_register_declares_no_duplicate_keys_anywhere(self):
        yaml.load(REVIEWS.read_text(encoding="utf-8"), Loader=_DuplicateKeyLoader)
        yaml.load(FINDINGS.read_text(encoding="utf-8"), Loader=_DuplicateKeyLoader)

    def test_the_closed_population_is_not_empty(self):
        """Otherwise every control above is vacuous and would stay green while empty."""
        state = self.findings["finding_state_control"]["canonical_field"]
        closed = [f["id"] for f in self.findings["findings"] if f.get(state) == "CLOSED"]
        self.assertTrue(closed, "no CLOSED finding: the authority controls have nothing to bite on")

    def test_the_grandfathered_population_is_exactly_the_pre_c10_closures(self):
        """A grandfather list is an exemption, so it may not quietly acquire members."""
        state = self.findings["finding_state_control"]["canonical_field"]
        closed = {f["id"] for f in self.findings["findings"] if f.get(state) == "CLOSED"}
        model = self.register["mechanism_verification_model"]
        grandfathered = set(model["grandfathered_closures"]["findings"])
        self.assertTrue(grandfathered <= closed,
                        "the exemption names a finding that is not CLOSED")
        completion = "repair_completion_object"
        for finding in self.findings["findings"]:
            if finding["id"] in grandfathered:
                self.assertNotIn(
                    completion, finding,
                    f"{finding['id']} is exempted from mechanism verification while declaring a "
                    f"completion object; the stated basis for the exemption is that none of them "
                    f"depends on the closure-completion model")


class ClosureRequiresAPositiveGrant(unittest.TestCase):
    """NF-33 / IR-03. Every shape the review left open, each refused.

    The population is never a hard-coded list of finding ids: each control selects its subject
    from the record and asserts on the observer's behaviour, so a rename or a new finding does not
    silently empty the control.
    """

    def setUp(self):
        self.findings, self.register = load(FINDINGS), load(REVIEWS)

    def fixtures(self):
        return copy.deepcopy(self.findings), copy.deepcopy(self.register)

    @staticmethod
    def close(findings: dict, fid: str, review_id: str):
        for finding in findings["findings"]:
            if finding["id"] == fid:
                finding["state"] = "CLOSED"
                finding["closure_review"] = review_id
                return finding
        raise AssertionError(f"{fid} not in the register")

    def a_review_granting_nothing(self, register: dict) -> str:
        """A registered review whose declared scope refuses lifecycle disposition."""
        for review in register["reviews"]:
            table = review.get(AUTHORITY_SOURCE_FIELD) or {}
            if table and not any(e.get("closure_authority") == "GRANTED"
                                 for e in table.values()):
                return review["review_id"]
        raise AssertionError("no repair-only review in the register to reproduce with")

    def an_open_finding(self, findings: dict) -> str:
        for finding in findings["findings"]:
            if finding.get("state") == "OPEN":
                return finding["id"]
        raise AssertionError("no OPEN finding to use as a subject")

    # ------------------------------------------------------------------ the historical shape

    def test_a_repair_only_review_cannot_serve_as_closure_warrant(self):
        findings, register = self.fixtures()
        review_id = self.a_review_granting_nothing(register)
        table = [r for r in register["reviews"] if r["review_id"] == review_id][0]
        subject = next(iter(table[AUTHORITY_SOURCE_FIELD]))
        self.close(findings, subject, review_id)
        problems = closure_authority_problems(findings, register)
        self.assertTrue(any(subject in p for p in problems),
                        f"a review that grants nothing closed {subject}: {problems}")

    def test_the_exact_00c6e2f_pairing_is_refused(self):
        """The historical record itself, reproduced rather than described.

        Read from the object, not reconstructed: the four transitions are taken from the committed
        findings register at 00c6e2f and run against the model as it stands now.
        """
        import subprocess
        raw = subprocess.run(
            ["git", "show", "00c6e2f097f2fbc58371ca7d019c3d0a5610eee1:"
             "mps/materialization/mps-mat-009/findings.yaml"],
            capture_output=True, cwd=REPO_ROOT)
        self.assertEqual(0, raw.returncode, "the historical object must resolve")
        historical = yaml.safe_load(raw.stdout.decode("utf-8"))
        closed = {f["id"] for f in historical["findings"] if f.get("state") == "CLOSED"}
        self.assertTrue({"NF-05", "NF-06", "NF-10", "NF-11"} <= closed,
                        "the historical object must actually carry the four transitions")
        problems = closure_authority_problems(historical, self.register)
        for fid in ("NF-05", "NF-06", "NF-10", "NF-11"):
            self.assertTrue(any(fid in p for p in problems),
                            f"{fid}'s historical closure is not refused: {problems}")

    def test_a_finding_absent_from_the_authority_population_cannot_close(self):
        findings, register = self.fixtures()
        review_id = self.a_review_granting_nothing(register)
        table = [r for r in register["reviews"] if r["review_id"] == review_id][0]
        outsider = next(f["id"] for f in findings["findings"]
                        if f.get("state") == "OPEN"
                        and f["id"] not in table[AUTHORITY_SOURCE_FIELD])
        self.close(findings, outsider, review_id)
        self.assertTrue(any(outsider in p and "declares no per-finding authority" in p
                            for p in closure_authority_problems(findings, register)))

    def test_closure_authority_denied_is_refused(self):
        self.assertRefused("DENIED")

    def test_closure_authority_indeterminate_is_refused(self):
        self.assertRefused("INDETERMINATE")

    def assertRefused(self, value: str):
        findings, register = self.fixtures()
        review = next(r for r in register["reviews"]
                      if any(e.get("closure_authority") == "GRANTED"
                             for e in (r.get(AUTHORITY_SOURCE_FIELD) or {}).values()))
        subject = next(f for f, e in review[AUTHORITY_SOURCE_FIELD].items()
                       if e.get("closure_authority") == "GRANTED")
        review[AUTHORITY_SOURCE_FIELD][subject]["closure_authority"] = value
        problems = closure_authority_problems(findings, register)
        self.assertTrue(any(subject in p and value in p for p in problems),
                        f"{value} authorized a closure: {problems}")

    def test_a_closing_review_level_verdict_with_no_finding_authority_is_refused(self):
        """The precise inference 00c6e2f made: a passing verdict read as a per-finding grant."""
        findings, register = self.fixtures()
        closing = set(register["closure_rule"]["closing_verdicts"])
        review = next(r for r in register["reviews"]
                      if r.get("verdict") in closing and AUTHORITY_SOURCE_FIELD not in r)
        subject = self.an_open_finding(findings)
        self.close(findings, subject, review["review_id"])
        problems = closure_authority_problems(findings, register)
        self.assertTrue(any(subject in p for p in problems),
                        f"a review-level {review['verdict']} closed {subject} on its own: {problems}")

    def test_a_review_granting_only_another_finding_is_refused(self):
        findings, register = self.fixtures()
        review = next(r for r in register["reviews"]
                      if any(e.get("closure_authority") == "GRANTED"
                             for e in (r.get(AUTHORITY_SOURCE_FIELD) or {}).values()))
        outsider = next(f["id"] for f in findings["findings"]
                        if f.get("state") == "OPEN"
                        and f["id"] not in review[AUTHORITY_SOURCE_FIELD])
        self.close(findings, outsider, review["review_id"])
        self.assertTrue(any(outsider in p for p in closure_authority_problems(findings, register)))

    # ------------------------------------------------------------------ the positive control

    def test_an_explicit_grant_at_the_exact_object_is_accepted(self):
        """A valid closure must remain possible, or the control forbids rather than measures.

        This is the shape NF-34 records: a control that refuses every transition would be
        satisfied forever by never dispositioning anything, and would not be a strong control.
        """
        findings, register = self.fixtures()
        review = next(r for r in register["reviews"]
                      if any(e.get("closure_authority") == "GRANTED"
                             for e in (r.get(AUTHORITY_SOURCE_FIELD) or {}).values()))
        subject = self.an_open_finding(findings)
        review[AUTHORITY_SOURCE_FIELD][subject] = {
            "repair_support": "VERIFIED",
            "closure_authority": "GRANTED",
            "basis": "synthetic positive control",
        }
        review[DERIVED_GRANT_FIELD] = sorted(
            f for f, e in review[AUTHORITY_SOURCE_FIELD].items()
            if e.get("closure_authority") == "GRANTED")
        self.close(findings, subject, review["review_id"])
        self.assertEqual([], closure_authority_problems(findings, register),
                         "an explicit grant must be accepted by the authority observer")
        self.assertEqual([], authority_reconciliation_problems(register))


class TheConvenienceListsAreDerivedNotAuthoritative(unittest.TestCase):
    """NF-36 / IR-06 and section 9: one authoritative source per question."""

    def setUp(self):
        self.register = load(REVIEWS)

    def test_the_derived_grant_list_may_not_diverge(self):
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"] if DERIVED_GRANT_FIELD in r)
        review[DERIVED_GRANT_FIELD] = list(review[DERIVED_GRANT_FIELD]) + ["NF-14"]
        self.assertTrue(any("does not equal" in p
                            for p in authority_reconciliation_problems(register)))

    def test_dropping_a_grant_from_the_derived_list_also_fails(self):
        """Both directions. A subset is as much a divergence as a superset."""
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"] if len(r.get(DERIVED_GRANT_FIELD) or []) > 1)
        review[DERIVED_GRANT_FIELD] = review[DERIVED_GRANT_FIELD][:-1]
        self.assertTrue(any("does not equal" in p
                            for p in authority_reconciliation_problems(register)))

    def test_the_legacy_list_must_declare_itself_non_authoritative(self):
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"] if LEGACY_SUPPORT_FIELD in r)
        review.pop(f"{LEGACY_SUPPORT_FIELD}_authority")
        self.assertTrue(any("must say so" in p
                            for p in authority_reconciliation_problems(register)))

    def test_an_undeclared_legacy_divergence_fails(self):
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"] if LEGACY_SUPPORT_FIELD in r)
        review[f"{LEGACY_SUPPORT_FIELD}_authority"][
            "declared_divergence_from_canonical"]["diverges_on"] = []
        self.assertTrue(any("undeclared divergence" in p
                            for p in authority_reconciliation_problems(register)))

    def test_the_legacy_list_answers_neither_controlled_question(self):
        """Executed, not asserted from source: emptying it must change no determination."""
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"] if LEGACY_SUPPORT_FIELD in r)
        before = {(r["review_id"], f): (verifies_repair(r, f, register),
                                        grants_closure(r, f, register))
                  for r in register["reviews"]
                  for f in (r.get(AUTHORITY_SOURCE_FIELD) or {})}
        review[LEGACY_SUPPORT_FIELD] = []
        after = {(r["review_id"], f): (verifies_repair(r, f, register),
                                       grants_closure(r, f, register))
                 for r in register["reviews"]
                 for f in (r.get(AUTHORITY_SOURCE_FIELD) or {})}
        self.assertEqual(before, after,
                         "emptying the historical list changed a controlled determination")

    def test_the_deciding_predicates_name_only_the_canonical_field(self):
        """A source scan over the two predicates that decide, not over the whole module.

        Both answers must come from one place. A predicate that also consulted the legacy list,
        a determination list or any prose field would be a second authority source, which is the
        drift this model exists to remove.
        """
        forbidden = {LEGACY_SUPPORT_FIELD, DERIVED_GRANT_FIELD, "per_finding_determinations",
                     "independent_review_support", "closure_note", "scope_note",
                     "verdict_scope", "governance_disposition"}
        for predicate in (grants_closure, verifies_repair, per_finding_authority):
            source = inspect.getsource(predicate)
            for name in sorted(forbidden):
                self.assertNotIn(
                    name, source,
                    f"{predicate.__name__} consults {name}, making it a second authority source")

    def test_a_contradictory_determination_is_reported(self):
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"]
                      if any(e.get("closure_authority") == "GRANTED"
                             for e in (r.get(AUTHORITY_SOURCE_FIELD) or {}).values()))
        subject = next(f for f, e in review[AUTHORITY_SOURCE_FIELD].items()
                       if e.get("closure_authority") == "GRANTED")
        review[AUTHORITY_SOURCE_FIELD][subject]["repair_support"] = "NOT_VERIFIED"
        self.assertTrue(any("contradict" in p for p in authority_vocabulary_problems(register)))

    def test_a_value_outside_the_controlled_vocabulary_is_reported(self):
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"] if AUTHORITY_SOURCE_FIELD in r)
        subject = next(iter(review[AUTHORITY_SOURCE_FIELD]))
        review[AUTHORITY_SOURCE_FIELD][subject]["closure_authority"] = "YES"
        self.assertTrue(any("not in the controlled vocabulary" in p
                            for p in authority_vocabulary_problems(register)))

    def test_a_determination_with_no_basis_is_reported(self):
        register = copy.deepcopy(self.register)
        review = next(r for r in register["reviews"] if AUTHORITY_SOURCE_FIELD in r)
        subject = next(iter(review[AUTHORITY_SOURCE_FIELD]))
        review[AUTHORITY_SOURCE_FIELD][subject]["basis"] = "   "
        self.assertTrue(any("states no basis" in p
                            for p in authority_vocabulary_problems(register)))

    def test_a_duplicate_determination_is_visible_at_the_text_layer(self):
        """PyYAML keeps the last of two identical keys, so a duplicate leaves no parsed trace."""
        source = REVIEWS.read_text(encoding="utf-8")
        marker = "      NF-13:\n        repair_support: VERIFIED\n"
        self.assertIn(marker, source, "the duplication anchor must exist")
        with self.assertRaises(yaml.constructor.ConstructorError):
            yaml.load(source.replace(marker, marker + marker, 1), Loader=_DuplicateKeyLoader)


class AChangedMechanismIsVerifiedBeforeItIsUsed(unittest.TestCase):
    """NF-31 / IR-01. The safety property, kept, with the over-strict reading dropped."""

    def setUp(self):
        self.findings, self.register = load(FINDINGS), load(REVIEWS)

    def fixtures(self):
        return copy.deepcopy(self.findings), copy.deepcopy(self.register)

    def close_a_new_finding(self, findings, register):
        """Close something that is not grandfathered, with a valid per-finding grant."""
        model = register["mechanism_verification_model"]
        grandfathered = set(model["grandfathered_closures"]["findings"])
        review = next(r for r in register["reviews"]
                      if any(e.get("closure_authority") == "GRANTED"
                             for e in (r.get(AUTHORITY_SOURCE_FIELD) or {}).values()))
        subject = next(f["id"] for f in findings["findings"]
                       if f.get("state") == "OPEN" and f["id"] not in grandfathered)
        review[AUTHORITY_SOURCE_FIELD][subject] = {
            "repair_support": "VERIFIED", "closure_authority": "GRANTED",
            "basis": "synthetic"}
        review[DERIVED_GRANT_FIELD] = sorted(
            f for f, e in review[AUTHORITY_SOURCE_FIELD].items()
            if e.get("closure_authority") == "GRANTED")
        for finding in findings["findings"]:
            if finding["id"] == subject:
                finding["state"] = "CLOSED"
                finding["closure_review"] = review["review_id"]
        return subject, review

    def test_a_new_closure_fails_while_the_mechanism_is_unverified(self):
        findings, register = self.fixtures()
        subject, _ = self.close_a_new_finding(findings, register)
        problems = mechanism_verification_problems(findings, register)
        self.assertTrue(any(subject in p and "declares verified" in p for p in problems),
                        f"an unverified mechanism closed {subject}: {problems}")

    def test_a_generic_cumulative_review_does_not_satisfy_the_requirement(self):
        """The exact inference this repair refuses.

        A closing cumulative review of a descendant of the introducing object, saying nothing
        about the mechanism, must not satisfy the pre-use condition. Ancestry establishes that the
        mechanism was PRESENT at the reviewed object; it establishes nothing about whether the
        review looked at it.
        """
        findings, register = self.fixtures()
        subject, _ = self.close_a_new_finding(findings, register)
        register["reviews"].append({
            "review_id": "REV-SYNTHETIC-CUMULATIVE",
            "reviewed_object": {"kind": "commit", "sha": "0" * 39 + "1"},
            "verdict": register["closure_rule"]["closing_verdicts"][0],
            "primary_artifact_retention": "external_not_retained",
            "reviewer": {"satisfies_mps_mat_009_named_reviewer_obligation": False},
        })
        problems = mechanism_verification_problems(findings, register)
        self.assertTrue(any(subject in p for p in problems),
                        "a cumulative review with no mechanism declaration satisfied the "
                        "pre-use requirement")

    def test_an_explicit_mechanism_declaration_does_satisfy_it(self):
        """And the relaxation is real: a scoped cumulative review is accepted."""
        findings, register = self.fixtures()
        subject, review = self.close_a_new_finding(findings, register)
        for name, mechanism in register["mechanisms"].items():
            review.setdefault("mechanisms_verified", []).append({
                "mechanism": name,
                "introduced_at": mechanism["introduced_at"],
                "verified_at_checkpoint": "a" * 40,
                "present_and_effective_at_checkpoint": True,
                "verdict": register["closure_rule"]["closing_verdicts"][0],
            })
        self.assertEqual([], mechanism_verification_problems(findings, register))

    def test_a_partial_mechanism_declaration_verifies_nothing(self):
        """All five clauses or none. A declaration missing one is not a weaker verification."""
        required = ("introduced_at", "verified_at_checkpoint", "verdict",
                    "present_and_effective_at_checkpoint")
        for omitted in required:
            with self.subTest(omitted=omitted):
                findings, register = self.fixtures()
                subject, review = self.close_a_new_finding(findings, register)
                for name, mechanism in register["mechanisms"].items():
                    entry = {
                        "mechanism": name,
                        "introduced_at": mechanism["introduced_at"],
                        "verified_at_checkpoint": "a" * 40,
                        "present_and_effective_at_checkpoint": True,
                        "verdict": register["closure_rule"]["closing_verdicts"][0],
                    }
                    entry.pop(omitted)
                    review.setdefault("mechanisms_verified", []).append(entry)
                self.assertTrue(mechanism_verification_problems(findings, register),
                                f"omitting {omitted} still verified the mechanism")

    def test_a_non_verifying_verdict_on_the_mechanism_verifies_nothing(self):
        findings, register = self.fixtures()
        subject, review = self.close_a_new_finding(findings, register)
        for name, mechanism in register["mechanisms"].items():
            review.setdefault("mechanisms_verified", []).append({
                "mechanism": name,
                "introduced_at": mechanism["introduced_at"],
                "verified_at_checkpoint": "a" * 40,
                "present_and_effective_at_checkpoint": True,
                "verdict": "FAIL",
            })
        self.assertTrue(mechanism_verification_problems(findings, register))

    def test_an_abbreviated_checkpoint_verifies_nothing(self):
        findings, register = self.fixtures()
        subject, review = self.close_a_new_finding(findings, register)
        for name, mechanism in register["mechanisms"].items():
            review.setdefault("mechanisms_verified", []).append({
                "mechanism": name,
                "introduced_at": mechanism["introduced_at"],
                "verified_at_checkpoint": "aaaaaaa",
                "present_and_effective_at_checkpoint": True,
                "verdict": register["closure_rule"]["closing_verdicts"][0],
            })
        self.assertTrue(any("not a full object" in p
                            for p in mechanism_verification_problems(findings, register)))

    def test_declaring_a_different_introduction_object_verifies_nothing(self):
        """A review that verified a mechanism somewhere else has not verified this one."""
        findings, register = self.fixtures()
        subject, review = self.close_a_new_finding(findings, register)
        name = "closure-completion-model"
        review["mechanisms_verified"] = [{
            "mechanism": name,
            "introduced_at": "b" * 40,
            "verified_at_checkpoint": "a" * 40,
            "present_and_effective_at_checkpoint": True,
            "verdict": register["closure_rule"]["closing_verdicts"][0],
        }]
        self.assertTrue(any("must be the same object" in p
                            for p in mechanism_verification_problems(findings, register)))

    def test_every_declared_mechanism_is_currently_unverified(self):
        """The state C10 is required to be in, asserted rather than assumed.

        C10 introduces the model; it must not also be the checkpoint that uses it. If any
        mechanism reads verified here, something has declared its own work reviewed.
        """
        for name, mechanism in self.register["mechanisms"].items():
            self.assertEqual("UNVERIFIED", mechanism["verification_state"], name)
        for review in self.register["reviews"]:
            self.assertNotIn("mechanisms_verified", review,
                             f"{review['review_id']} declares a mechanism verified; no review in "
                             f"this register has yet assessed one")

    def test_the_unresolvable_half_is_stated_rather_than_observed(self):
        """The observer must not pretend to establish transition ordering it cannot see."""
        model = self.register["mechanism_verification_model"]
        self.assertIn("what_this_observer_cannot_establish", model)
        source = inspect.getsource(mechanism_verification_problems)
        for forbidden in ("committer", "author_date", "%ci", "%ai", "time.time"):
            self.assertNotIn(forbidden, source,
                             "the observer reads a timestamp, which no controlled process here "
                             "declares authoritative")


class ExactObjectIdentityIsUnweakened(unittest.TestCase):
    """Section 11. The new requirement is additive; nothing about identity is relaxed."""

    def test_the_authority_model_declares_identity_unchanged(self):
        model = authority_model(load(REVIEWS))
        self.assertIn("exact_object_identity_is_unchanged", model)

    def test_no_authority_predicate_performs_object_comparison(self):
        """Identity stays in the closure observer. Two implementations is how NF-23 happened."""
        for predicate in (grants_closure, verifies_repair, closure_authority_problems):
            tree = ast.parse(inspect.getsource(predicate))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, {"startswith", "lower", "casefold"},
                                     f"{predicate.__name__} performs prefix or case matching on "
                                     f"an object identity")


if __name__ == "__main__":
    unittest.main()
