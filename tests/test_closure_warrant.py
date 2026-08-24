"""Closure warrant must resolve to a registered review, over a controlled population.

NF-05 and NF-06: a finding was moved to CLOSED by writing prose in `closed_by` describing an
independent review, and nothing resolved it. The string was sufficient on its own -- it did
not have to name a review that existed, that had reviewed the object the finding claimed as
its repair, or that had returned a passing verdict.

NF-09: and a closure rule keyed on state would not have been enough on its own, because the
state representation was heterogeneous. Two field names, canonical values in one and
lowercase or prose in the other, and 20 of 34 records carrying neither. A correct rule over
that population would have passed -- not because every finding was substantiated, but because
most were invisible to it. Population definition precedes closure substantiation, so the
controls come in that order and the second depends on the first.

    layer 1   every finding carries a canonical state, or is declared state debt with a reason
    layer 2   every canonically CLOSED finding has exactly one resolving closure warrant

Both read controlled declarations rather than restating them. `canonical_states` and
`closing_verdicts` are data; a control carrying its own copy of a rule stops testing the rule
and starts testing the copy, and the two agree right up until they do not. Two mutations below
change those declarations and require the observers to follow.

Neither observer parses prose. `closure_note` is explicitly non-authoritative, and a state
exception confers no disposition whatever -- it means only that the controlled representation
is absent or legacy. Prose cannot move controlled finding state.
"""
from __future__ import annotations

import collections
import contextlib
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = REPO_ROOT / "mps" / "materialization" / "mps-mat-009"
REVIEWS = RECORD_DIR / "independent-reviews.yaml"
FINDINGS = RECORD_DIR / "findings.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def legacy_value_digest(value) -> str:
    """The declared encoding of a legacy field's value, hashed.

    Stated once, here, because a digest is only exact if both sides agree on what was
    hashed. A present-but-null field is a real state -- someone wrote the key -- so it needs
    an encoding of its own rather than being folded into absence: null encodes to the literal
    four characters `null`, and every other value to its string form. Using Python's str(None)
    would have leaked "None" into a controlled record as the canonical spelling of nothing.
    """
    import hashlib

    text = "null" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(*args: str) -> tuple[int, str]:
    import subprocess

    result = subprocess.run(["git", *args], capture_output=True, text=True,
                            cwd=str(REPO_ROOT))
    return result.returncode, result.stdout.strip()


def closure_target(finding: dict) -> str | None:
    """The object a closure review must have reviewed, EXACTLY.

    C6. A repair introduced at one commit can only become complete at a later one -- NF-06's
    mechanism landed at C1 and its population defects were repaired at C3 and C4. Before
    this, the record could say where a repair was introduced or where it became complete but
    not both, so the closure rule had nothing correct to match.

    The target moves to the declared completion object when one exists. What does NOT change
    is the match: it remains exact object identity. Ancestry is a validity precondition on a
    declaration a person wrote, never a way of satisfying the match, and no descendant is
    ever substituted for a target that was not declared.
    """
    return finding.get("repair_completion_object") or finding.get("repair")


def completion_declaration_problems(findings_body: dict, register_body: dict) -> list[str]:
    """Validity of every declared repair-completion relationship."""
    rule = register_body["repair_completion_rule"]
    closing = set(register_body["closure_rule"]["closing_verdicts"])
    reviews = register_body.get("reviews") or []

    problems: list[str] = []
    for finding in findings_body["findings"]:
        if "repair_completion_object" not in finding:
            continue
        fid = finding["id"]
        completion = finding["repair_completion_object"]
        # Declared-but-unusable is a failure, never a skip. An all-digit sha is parsed by
        # YAML as an integer, and an integer is falsy, so a truthiness test would drop the
        # finding out of the population silently -- the declaration would be present and
        # unobserved, which is the shape of every finding in this register.
        if not isinstance(completion, str) or not completion.strip():
            problems.append(f"{fid}: repair_completion_object is not a commit-object string "
                            f"({completion!r}); a declaration that cannot be read must fail "
                            f"rather than remove the finding from the population")
            continue

        if not str(finding.get("repair", "")).strip():
            problems.append(f"{fid}: declares a completion object while its original repair "
                            f"field is absent; the completion must not replace it")
        introduced = finding.get("repair_introduced_object")
        if not introduced:
            problems.append(f"{fid}: declares a completion object with no "
                            f"repair_introduced_object, so the ancestry precondition cannot "
                            f"be evaluated")
        if not str(finding.get("repair_completion_reason", "")).strip():
            problems.append(f"{fid}: declares a completion object with no completion reason")

        for label, sha in (("completion", completion), ("introduced", introduced)):
            if not sha:
                continue
            code, kind = git("cat-file", "-t", sha)
            if code != 0 or kind != "commit":
                problems.append(f"{fid}: {label} object {str(sha)[:12]} does not resolve to a "
                                f"commit in this repository")

        if introduced and completion:
            code, _ = git("merge-base", "--is-ancestor", introduced, completion)
            if code != 0:
                problems.append(
                    f"{fid}: repair_introduced_object {introduced[:12]} is not an ancestor of "
                    f"or identical to the completion object {completion[:12]}; a completion "
                    f"object must not be an unrelated convenient commit")

        # Exactly one registered review must BOTH have verified this finding's repair and
        # have reviewed the completion object. A generic review of a commit is never
        # reinterpreted as verification of every finding in the repository.
        supporting = [r for r in reviews
                      if fid in (r.get("verified_repairs_of") or [])
                      and reviewed_sha(r) == completion]
        if not supporting:
            problems.append(f"{fid}: no registered review both verified this finding's repair "
                            f"and reviewed {completion[:12]}; prose asserting cumulative "
                            f"verification is not the typed relationship")
            continue
        if len(supporting) > 1:
            problems.append(f"{fid}: {len(supporting)} registered reviews claim to verify this "
                            f"repair at {completion[:12]}; ambiguity is surfaced, not resolved")
            continue
        review = supporting[0]
        if review.get("verdict") not in closing:
            problems.append(f"{fid}: the completion review returned "
                            f"{review.get('verdict')!r}, which is not a closing verdict")
        if review.get("primary_artifact_retention") not in {
                "retained", "external_not_retained", "reproduction"}:
            problems.append(f"{fid}: the completion review declares no valid evidence "
                            f"retention status")
        reviewer = review.get("reviewer") or {}
        if reviewer.get("satisfies_mps_mat_009_named_reviewer_obligation") is not False:
            problems.append(f"{fid}: the completion review misrepresents its reviewer "
                            f"authority")
    return problems


def reviewed_sha(review: dict):
    obj = review.get("reviewed_object") or {}
    if isinstance(obj, str):
        return obj
    return obj.get("sha") or obj.get("later_committed_as")


# --------------------------------------------------------------------------------------
# layer 1: state representation completeness
# --------------------------------------------------------------------------------------

def state_completeness_problems(findings_body: dict) -> list[str]:
    """Every finding is canonically stated, or is state debt that describes itself truthfully.

    NF-10. The second clause used to be an unchecked assertion: an exception said
    `observed_state: absent` and nothing compared that to the record. Six declarations were
    false -- five records carrying `disposition: closed` and one carrying a prose disposition
    were all exempted by declarations stating that no representation existed. A legacy
    closure claim could therefore sit inside declared state debt, invisible to the state
    layer and invisible to the closure layer, which only ranges over canonical CLOSED.

    So the declaration is now mechanically checked against the record, per legacy field, by
    digest of the exact value. `state` remains the sole authoritative lifecycle field:
    whatever a legacy field says, including the word closed, confers nothing.
    """
    import hashlib

    control = findings_body["finding_state_control"]
    canonical = set(control["canonical_states"])
    field = control["canonical_field"]
    legacy_fields = control["legacy_fields"]
    exceptions = control.get("exceptions") or {}

    problems: list[str] = []
    known = {f["id"] for f in findings_body["findings"]}

    for finding in findings_body["findings"]:
        fid = finding["id"]
        value = finding.get(field)
        if value in canonical:
            if fid in exceptions:
                problems.append(f"{fid}: has canonical state {value!r} and is also declared a "
                                f"state exception; it must be one or the other")
            continue
        entry = exceptions.get(fid)
        if entry is None:
            problems.append(f"{fid}: carries no canonical {field} and is not declared a state "
                            f"exception; a state-scoped observer would silently omit it")
            continue
        if not str(entry.get("reason", "")).strip():
            problems.append(f"{fid}: declared a state exception with no reason")

        declared = entry.get("legacy_representation")
        if not isinstance(declared, dict):
            problems.append(f"{fid}: state exception declares no legacy_representation, so "
                            f"what the record actually says is unchecked")
            continue
        for legacy in legacy_fields:
            claim = declared.get(legacy)
            if not isinstance(claim, dict) or "present" not in claim:
                problems.append(f"{fid}: legacy_representation does not say whether "
                                f"{legacy!r} is present")
                continue
            # NF-11. Presence is KEY MEMBERSHIP, not "the value is not None". The first
            # implementation used finding.get(legacy), which conflates a field that is absent
            # with a field that is physically present and null -- so `disposition:` written
            # with no value satisfied a declaration of absent, and the record's own shape was
            # again unobserved. The distinction matters because a present-but-null key is a
            # field someone wrote.
            actual_present = legacy in finding
            actual = finding.get(legacy)
            if claim["present"] is False:
                if actual_present:
                    shown = "null" if actual is None else " ".join(str(actual).split())[:48]
                    problems.append(
                        f"{fid}: exception declares {legacy!r} absent, but the record carries "
                        f"the key ({shown}); a declaration that does not correspond to its "
                        f"record conceals what the record says")
                continue
            if not actual_present:
                problems.append(f"{fid}: exception declares {legacy!r} present, but the "
                                f"record does not carry the key")
                continue
            if claim.get("sha256") != legacy_value_digest(actual):
                problems.append(f"{fid}: declared {legacy!r} value does not match the record")

    for fid in exceptions:
        if fid not in known:
            problems.append(f"state exception declared for {fid!r}, which is not a finding")
    return problems


# --------------------------------------------------------------------------------------
# register integrity: review ids are unique, independently of closure
# --------------------------------------------------------------------------------------

def register_integrity_problems(register_body: dict) -> list[str]:
    problems: list[str] = []
    counts = collections.Counter(r.get("review_id") for r in register_body.get("reviews") or [])
    for review_id, n in sorted(counts.items()):
        if n > 1:
            problems.append(f"review id {review_id!r} appears {n} times in the register; a "
                            f"review reference must resolve to exactly one entry")
    return problems


# --------------------------------------------------------------------------------------
# layer 2: closure substantiation, over the canonically CLOSED population
# --------------------------------------------------------------------------------------

def closure_problems(findings_body: dict, register_body: dict) -> list[str]:
    rule = register_body["closure_rule"]
    applicable_state = rule["applies_to_finding_state"]
    required_field = rule["requires_field"]
    closing = set(rule["closing_verdicts"])
    state_field = findings_body["finding_state_control"]["canonical_field"]
    reviews = register_body.get("reviews") or []
    registered_units = {u["review"] for u in register_body["population"]["reviewable_units"]}

    problems: list[str] = []
    for finding in findings_body["findings"]:
        if finding.get(state_field) != applicable_state:
            continue
        fid = finding["id"]
        reference = finding.get(required_field)
        if not reference:
            problems.append(f"{fid}: is {applicable_state} with no {required_field}; prose "
                            f"cannot constitute closure warrant")
            continue

        matches = [r for r in reviews if r.get("review_id") == reference]
        if not matches:
            problems.append(f"{fid}: {required_field} names {reference!r}, which is not in "
                            f"the review register")
            continue
        if len(matches) > 1:
            # Surfaced, never resolved by choosing. No first match, no latest match, no
            # deduplication: the ambiguity is itself the defect.
            problems.append(f"{fid}: {reference!r} appears {len(matches)} times in the review "
                            f"register; a closure warrant must resolve to exactly one review")
            continue

        review = matches[0]
        if reference not in registered_units:
            problems.append(f"{fid}: {reference!r} has a review entry but is not declared as "
                            f"a reviewable unit, so it is not a registered review")
        # C6: the target is the declared completion object when one exists, and the
        # ORIGINAL repair otherwise. The match itself is unchanged -- exact object identity,
        # no ancestry, no descendant substitution, no promotion.
        claimed = closure_target(finding)
        actual = reviewed_sha(review)
        if not claimed:
            problems.append(f"{fid}: names no closure target for the review to have reviewed")
        elif actual != claimed:
            problems.append(f"{fid}: closure review {reference} reviewed {str(actual)[:12]} "
                            f"but the finding's closure target is {str(claimed)[:12]}")
        if review.get("verdict") not in closing:
            problems.append(f"{fid}: closure review {reference} returned "
                            f"{review.get('verdict')!r}, which is not a closing verdict")
        if review.get("primary_artifact_retention") not in {
                "retained", "external_not_retained", "reproduction"}:
            problems.append(f"{fid}: closure review {reference} declares no valid evidence "
                            f"retention status")
    return problems


@contextlib.contextmanager
def mutated(path: Path, old: str, new: str):
    """Mutate a controlled file on disk, then restore it byte-identically."""
    original = path.read_bytes()
    text = original.decode("utf-8")
    assert old in text, f"mutation anchor not present in {path.name}"
    try:
        path.write_bytes(text.replace(old, new, 1).encode("utf-8"))
        yield
    finally:
        path.write_bytes(original)
        assert path.read_bytes() == original, f"{path.name} not restored byte-identically"


NOVEL_ANCHOR = "  - id: RT-F-01\n"


class TheRecordAsCommitted(unittest.TestCase):

    def test_state_representation_is_complete(self):
        self.assertEqual([], state_completeness_problems(load(FINDINGS)))

    def test_the_state_population_partitions_exactly(self):
        body = load(FINDINGS)
        control = body["finding_state_control"]
        canonical = {f["id"] for f in body["findings"]
                     if f.get(control["canonical_field"]) in set(control["canonical_states"])}
        exceptions = set(control["exceptions"])
        everything = {f["id"] for f in body["findings"]}
        self.assertEqual(everything, canonical | exceptions)
        self.assertEqual(set(), canonical & exceptions)

    def test_register_review_ids_are_unique(self):
        self.assertEqual([], register_integrity_problems(load(REVIEWS)))

    def test_every_closed_finding_has_a_resolving_closure_warrant(self):
        self.assertEqual([], closure_problems(load(FINDINGS), load(REVIEWS)))

    def test_the_closed_population_is_not_empty(self):
        body, register = load(FINDINGS), load(REVIEWS)
        state_field = body["finding_state_control"]["canonical_field"]
        closed = [f for f in body["findings"]
                  if f.get(state_field) == register["closure_rule"]["applies_to_finding_state"]]
        self.assertTrue(closed, "with no CLOSED finding the closure observer asserts nothing")

    def test_the_observers_do_not_enumerate_finding_ids(self):
        """Scoped to the observer functions, not the whole module.

        An earlier version scanned this file's entire source and failed on its own mutation
        anchors, which legitimately name findings in order to perturb them. The property
        being protected is narrower: the OBSERVERS must derive applicability from state and
        the controlled rule, never from a list of ids.
        """
        import inspect

        for observer in (state_completeness_problems, closure_problems,
                         register_integrity_problems):
            source = inspect.getsource(observer)
            with self.subTest(observer=observer.__name__):
                for fid in ("RT-F-0", "MI-R-0", "NF-0"):
                    self.assertNotIn(fid, source)

    def test_the_observers_do_not_read_the_prose_field(self):
        import inspect

        for observer in (state_completeness_problems, closure_problems,
                         register_integrity_problems):
            with self.subTest(observer=observer.__name__):
                self.assertNotIn("closure_note", inspect.getsource(observer))


class StateCompletenessMutations(unittest.TestCase):

    def observe(self):
        return state_completeness_problems(load(FINDINGS))

    def test_a_novel_finding_with_no_state_and_no_exception_fails(self):
        novel = ("  - id: NOVEL-NOSTATE-01\n"
                 "    origin: synthetic mutation control\n")
        with mutated(FINDINGS, NOVEL_ANCHOR, novel + NOVEL_ANCHOR):
            problems = self.observe()
        self.assertTrue(any("NOVEL-NOSTATE-01" in p and "not declared a state exception" in p
                            for p in problems))

    def test_a_novel_finding_with_a_noncanonical_state_fails(self):
        novel = ("  - id: NOVEL-BADSTATE-01\n"
                 "    origin: synthetic mutation control\n"
                 "    state: closed\n")
        with mutated(FINDINGS, NOVEL_ANCHOR, novel + NOVEL_ANCHOR):
            problems = self.observe()
        self.assertTrue(any("NOVEL-BADSTATE-01" in p for p in problems),
                        "a lowercase value is not a canonical state")

    ABSENT = ("      legacy_representation:\n"
              "        status:\n          present: false\n"
              "        disposition:\n          present: false\n")

    def test_a_novel_stateless_finding_with_a_truthful_declaration_passes(self):
        """Positive control: truthfully described state debt is legitimate."""
        novel = ("  - id: NOVEL-DEBT-01\n"
                 "    origin: synthetic mutation control\n")
        declared = ("    NOVEL-DEBT-01:\n" + self.ABSENT +
                    "      reason: synthetic control; representation deliberately incomplete\n")
        original = FINDINGS.read_bytes()
        text = original.decode("utf-8")
        try:
            text = text.replace(NOVEL_ANCHOR, novel + NOVEL_ANCHOR, 1)
            text = text.replace("  exceptions:\n", "  exceptions:\n" + declared, 1)
            FINDINGS.write_bytes(text.encode("utf-8"))
            self.assertEqual([], self.observe())
        finally:
            FINDINGS.write_bytes(original)
            self.assertEqual(original, FINDINGS.read_bytes())

    def test_a_novel_finding_with_a_truthfully_declared_legacy_disposition_passes(self):
        """Positive control, NF-10: a legacy `disposition: closed`, truthfully declared,
        remains state debt and acquires no lifecycle disposition whatever."""
        import hashlib

        digest = hashlib.sha256(b"closed").hexdigest()
        novel = ("  - id: NOVEL-LEGACY-01\n"
                 "    origin: synthetic mutation control\n"
                 "    disposition: closed\n")
        declared = ("    NOVEL-LEGACY-01:\n"
                    "      legacy_representation:\n"
                    "        status:\n          present: false\n"
                    "        disposition:\n          present: true\n"
                    f"          sha256: {digest}\n"
                    "      reason: legacy disposition, not adjudicated; still state debt\n")
        original = FINDINGS.read_bytes()
        text = original.decode("utf-8")
        try:
            text = text.replace(NOVEL_ANCHOR, novel + NOVEL_ANCHOR, 1)
            text = text.replace("  exceptions:\n", "  exceptions:\n" + declared, 1)
            FINDINGS.write_bytes(text.encode("utf-8"))
            self.assertEqual([], self.observe())
            # And it confers no lifecycle state: the closure layer never sees it.
            self.assertEqual([], closure_problems(load(FINDINGS), load(REVIEWS)))
        finally:
            FINDINGS.write_bytes(original)
            self.assertEqual(original, FINDINGS.read_bytes())

    def test_declaring_absent_while_the_record_carries_a_legacy_disposition_fails(self):
        """The RED counterexample, preserved: it was true of the committed record.

        Five MI-R findings carried `disposition: closed` under exceptions declaring that no
        representation existed. This drives the same shape and requires refusal.
        """
        with mutated(FINDINGS,
                     "        disposition:\n          present: true\n"
                     "          sha256: c3eefb58d7c42440a9d4abec51d629544d635a6d936ff3c4d3fca96d611b3cf3",
                     "        disposition:\n          present: false"):
            problems = self.observe()
        self.assertTrue(any("declares 'disposition' absent" in p and "conceals" in p
                            for p in problems), problems[:3])

    def test_declaring_present_while_the_record_lacks_it_fails(self):
        import hashlib

        digest = hashlib.sha256(b"nothing").hexdigest()
        with mutated(FINDINGS,
                     "    F1:\n      legacy_representation:\n"
                     "        status:\n          present: false",
                     "    F1:\n      legacy_representation:\n"
                     f"        status:\n          present: true\n          sha256: {digest}"):
            problems = self.observe()
        self.assertTrue(any(p.startswith("F1:") and "does not carry the key" in p
                            for p in problems))

    def _with_novel(self, record_lines: str, exception_lines: str):
        """Insert a synthetic finding and its exception, restoring byte-identically."""
        original = FINDINGS.read_bytes()
        text = original.decode("utf-8")
        try:
            text = text.replace(NOVEL_ANCHOR, record_lines + NOVEL_ANCHOR, 1)
            text = text.replace("  exceptions:\n", "  exceptions:\n" + exception_lines, 1)
            FINDINGS.write_bytes(text.encode("utf-8"))
            return self.observe()
        finally:
            FINDINGS.write_bytes(original)
            assert FINDINGS.read_bytes() == original

    def test_a_present_but_null_key_declared_absent_fails(self):
        """NF-11, the independent RED: `disposition:` with no value is a key someone wrote.

        The first implementation asked whether the value was None, which cannot tell an
        absent field from a present empty one, so this declaration passed.
        """
        record = ("  - id: NOVEL-NULLKEY-01\n"
                  "    origin: synthetic mutation control\n"
                  "    disposition:\n")
        exception = ("    NOVEL-NULLKEY-01:\n" + self.ABSENT +
                     "      reason: claims the disposition key is absent\n")
        problems = self._with_novel(record, exception)
        self.assertTrue(any("NOVEL-NULLKEY-01" in p and "carries the key (null)" in p
                            for p in problems), problems[:3])

    def test_a_present_but_null_key_declared_truthfully_passes(self):
        """Null is an allowed legacy value, and declaring it honestly is legitimate."""
        record = ("  - id: NOVEL-NULLOK-01\n"
                  "    origin: synthetic mutation control\n"
                  "    status:\n")
        exception = ("    NOVEL-NULLOK-01:\n"
                     "      legacy_representation:\n"
                     "        status:\n          present: true\n"
                     f"          sha256: {legacy_value_digest(None)}\n"
                     "        disposition:\n          present: false\n"
                     "      reason: legacy status key present and empty; still state debt\n")
        self.assertEqual([], self._with_novel(record, exception))

    def test_an_absent_key_declared_absent_passes(self):
        record = ("  - id: NOVEL-ABSENT-01\n"
                  "    origin: synthetic mutation control\n")
        exception = ("    NOVEL-ABSENT-01:\n" + self.ABSENT +
                     "      reason: no legacy representation of any kind\n")
        self.assertEqual([], self._with_novel(record, exception))

    def test_an_absent_key_declared_present_fails(self):
        record = ("  - id: NOVEL-GHOSTKEY-01\n"
                  "    origin: synthetic mutation control\n")
        exception = ("    NOVEL-GHOSTKEY-01:\n"
                     "      legacy_representation:\n"
                     "        status:\n          present: true\n"
                     f"          sha256: {legacy_value_digest('open')}\n"
                     "        disposition:\n          present: false\n"
                     "      reason: claims a status the record does not carry\n")
        problems = self._with_novel(record, exception)
        self.assertTrue(any("NOVEL-GHOSTKEY-01" in p and "does not carry the key" in p
                            for p in problems), problems[:3])

    def test_a_present_non_null_key_with_a_wrong_digest_fails(self):
        record = ("  - id: NOVEL-BADDIGEST-01\n"
                  "    origin: synthetic mutation control\n"
                  "    disposition: closed\n")
        exception = ("    NOVEL-BADDIGEST-01:\n"
                     "      legacy_representation:\n"
                     "        status:\n          present: false\n"
                     "        disposition:\n          present: true\n"
                     f"          sha256: {legacy_value_digest('something else')}\n"
                     "      reason: declares a value the record does not hold\n")
        problems = self._with_novel(record, exception)
        self.assertTrue(any("NOVEL-BADDIGEST-01" in p and "does not match the record" in p
                            for p in problems), problems[:3])

    def test_presence_is_key_membership_not_value_nullness(self):
        """The property directly, so a regression to finding.get() is caught."""
        import inspect

        source = inspect.getsource(state_completeness_problems)
        self.assertIn("legacy in finding", source)
        self.assertNotIn("finding.get(legacy) is not None", source)

    def test_a_declared_value_that_does_not_match_the_record_fails(self):
        with mutated(FINDINGS,
                     "          sha256: c3eefb58d7c42440a9d4abec51d629544d635a6d936ff3c4d3fca96d611b3cf3",
                     "          sha256: " + "0" * 64):
            problems = self.observe()
        self.assertTrue(any("does not match the record" in p for p in problems))

    def test_an_exception_with_no_representation_declaration_fails(self):
        with mutated(FINDINGS,
                     "    F1:\n      legacy_representation:\n"
                     "        status:\n          present: false\n"
                     "        disposition:\n          present: false\n",
                     "    F1:\n"):
            problems = self.observe()
        self.assertTrue(any(p.startswith("F1:") and "no legacy_representation" in p
                            for p in problems))

    def test_an_exception_referring_to_no_finding_fails(self):
        orphan = ("    NO-SUCH-FINDING:\n" + self.ABSENT +
                  "      reason: synthetic control\n")
        with mutated(FINDINGS, "  exceptions:\n", "  exceptions:\n" + orphan):
            problems = self.observe()
        self.assertTrue(any("NO-SUCH-FINDING" in p and "not a finding" in p
                            for p in problems))

    def test_an_exception_with_an_empty_reason_fails(self):
        with mutated(FINDINGS,
                     "    F1:\n" + self.ABSENT + "      reason: >-",
                     "    F1:\n" + self.ABSENT + "      reason: ''\n      unused: >-"):
            problems = self.observe()
        self.assertTrue(any(p.startswith("F1:") and "no reason" in p for p in problems))

    def test_a_finding_both_canonical_and_excepted_fails(self):
        both = ("    RT-F-03:\n" + self.ABSENT + "      reason: synthetic control\n")
        with mutated(FINDINGS, "  exceptions:\n", "  exceptions:\n" + both):
            problems = self.observe()
        self.assertTrue(any("RT-F-03" in p and "one or the other" in p for p in problems))

    def test_legacy_fields_confer_no_lifecycle_state(self):
        """`state` is the sole authoritative field, asserted over the committed record."""
        body = load(FINDINGS)
        control = body["finding_state_control"]
        legacy = set(control["legacy_fields"])
        self.assertEqual({"status", "disposition"}, legacy)
        self.assertEqual("state", control["canonical_field"])
        closed_ids = {f["id"] for f in body["findings"]
                      if f.get("state") == "CLOSED"}
        legacy_closed = {f["id"] for f in body["findings"]
                         if str(f.get("disposition", "")).strip() == "closed"}
        self.assertTrue(legacy_closed, "the counterexample population must still exist")
        self.assertEqual(set(), legacy_closed & closed_ids,
                         "no legacy disposition was converted into canonical CLOSED")

    def test_the_observer_follows_the_controlled_state_vocabulary(self):
        with mutated(FINDINGS,
                     "  canonical_states:\n    - OPEN\n    - CLOSED\n    - ACCEPTED",
                     "  canonical_states:\n    - OPEN\n    - ACCEPTED"):
            problems = self.observe()
        self.assertTrue(any("RT-F-03" in p for p in problems),
                        "removing CLOSED from the declared vocabulary must make the "
                        "CLOSED records non-conforming; the observer must read the rule")


class ClosureWarrantMutations(unittest.TestCase):

    def observe(self):
        return closure_problems(load(FINDINGS), load(REVIEWS))

    def test_unknown_review_id_fails(self):
        with mutated(FINDINGS, "closure_review: REV-RT-F-CLOSURE",
                     "closure_review: REV-DOES-NOT-EXIST"):
            problems = self.observe()
        self.assertTrue(any("not in the review register" in p for p in problems))

    def test_removing_the_referenced_review_entry_fails(self):
        with mutated(REVIEWS, "  - review_id: REV-RT-F-CLOSURE",
                     "  - review_id: REV-RT-F-CLOSURE-RENAMED"):
            problems = self.observe()
        self.assertTrue(any("not in the review register" in p for p in problems))

    def test_reviewed_object_pointing_at_the_wrong_commit_fails(self):
        with mutated(REVIEWS,
                     "      sha: 7ad9b81e3bd7f67f7b1e87ef2cc0eafb76c349a7",
                     "      sha: " + "0" * 40):
            problems = self.observe()
        self.assertTrue(any("closure target is" in p for p in problems))

    def test_a_non_closing_verdict_fails(self):
        with mutated(REVIEWS,
                     "      sha: 7ad9b81e3bd7f67f7b1e87ef2cc0eafb76c349a7\n"
                     "    verdict: INDEPENDENTLY VERIFIED",
                     "      sha: 7ad9b81e3bd7f67f7b1e87ef2cc0eafb76c349a7\n"
                     "    verdict: FAIL"):
            problems = self.observe()
        self.assertTrue(any("not a closing verdict" in p for p in problems))

    def test_removing_the_closure_reference_fails(self):
        with mutated(FINDINGS, "    closure_review: REV-RT-F-CLOSURE\n", ""):
            problems = self.observe()
        self.assertTrue(any("with no closure_review" in p for p in problems))

    def test_two_reviews_sharing_the_referenced_id_fails(self):
        """Exactly once. The condition most easily implemented as at-least-once."""
        duplicate = ("  - review_id: REV-RT-F-CLOSURE\n"
                     "    subject: duplicate\n"
                     "    reviewed_object:\n"
                     "      kind: commit\n"
                     "      sha: 7ad9b81e3bd7f67f7b1e87ef2cc0eafb76c349a7\n"
                     "    verdict: INDEPENDENTLY VERIFIED\n"
                     "    reviewer:\n"
                     "      relationship: r\n"
                     "      identity: unnamed\n"
                     "      satisfies_mps_mat_009_named_reviewer_obligation: false\n"
                     "    primary_artifact_retention: external_not_retained\n\n")
        with mutated(REVIEWS, "  - review_id: REV-RT-F-CLOSURE",
                     duplicate + "  - review_id: REV-RT-F-CLOSURE"):
            closure = self.observe()
            integrity = register_integrity_problems(load(REVIEWS))
        self.assertTrue(any("exactly one review" in p for p in closure))
        self.assertTrue(integrity, "uniqueness must also fail as a register-integrity "
                                   "invariant, not only as a side effect of closure")

    def test_a_novel_closed_finding_with_no_warrant_fails(self):
        novel = ("  - id: NOVEL-CLOSED-01\n"
                 "    origin: synthetic mutation control\n"
                 "    state: CLOSED\n"
                 "    repair: " + "0" * 40 + "\n"
                 "    closure_note: >-\n"
                 "      An entirely convincing sentence asserting that an independent review\n"
                 "      took place and warranted this closure.\n")
        with mutated(FINDINGS, NOVEL_ANCHOR, novel + NOVEL_ANCHOR):
            problems = self.observe()
        self.assertTrue(any("NOVEL-CLOSED-01" in p and "no closure_review" in p
                            for p in problems),
                        "a new CLOSED finding is subject to the rule without being listed")

    def test_an_open_finding_with_no_warrant_passes(self):
        novel = ("  - id: NOVEL-OPEN-01\n"
                 "    origin: synthetic mutation control\n"
                 "    state: OPEN\n")
        with mutated(FINDINGS, NOVEL_ANCHOR, novel + NOVEL_ANCHOR):
            self.assertEqual([], self.observe())

    def test_a_state_exception_finding_with_no_warrant_passes(self):
        """A state exception must not accidentally acquire closure semantics."""
        problems = self.observe()
        self.assertEqual([], problems)
        body = load(FINDINGS)
        excepted = set(body["finding_state_control"]["exceptions"])
        self.assertIn("MI-R-01", excepted,
                      "MI-R-01 reports closure in prose and has no controlled state; it must "
                      "be state debt, not an inferred closure")
        self.assertTrue(all("MI-R-01" not in p for p in problems))

    def test_the_observer_follows_the_controlled_verdict_vocabulary(self):
        with mutated(REVIEWS,
                     "  closing_verdicts:\n    - INDEPENDENTLY VERIFIED",
                     "  closing_verdicts:\n    - SOME OTHER VERDICT"):
            problems = self.observe()
        self.assertTrue(any("not a closing verdict" in p for p in problems))

    def test_every_mutation_restored_the_files(self):
        self.assertEqual([], state_completeness_problems(load(FINDINGS)))
        self.assertEqual([], self.observe())
        self.assertEqual([], register_integrity_problems(load(REVIEWS)))


class RegistrationDoesNotConferAuthority(unittest.TestCase):

    def test_the_three_new_reviews_are_registered(self):
        register = load(REVIEWS)
        ids = {r["review_id"] for r in register["reviews"]}
        units = {u["review"] for u in register["population"]["reviewable_units"]}
        for review_id in ("REV-RECORD-TRANSPORT", "REV-RT-F-CLOSURE", "REV-RT-F-SUBSTANCE"):
            with self.subTest(review=review_id):
                self.assertIn(review_id, ids)
                self.assertIn(review_id, units)

    def test_every_registered_review_is_unnamed_and_says_so(self):
        for review in load(REVIEWS)["reviews"]:
            with self.subTest(review=review["review_id"]):
                self.assertIn("unnamed", review["reviewer"]["identity"].casefold())
                self.assertIs(
                    False,
                    review["reviewer"]["satisfies_mps_mat_009_named_reviewer_obligation"])

    def test_registering_reviews_does_not_discharge_the_named_reviewer_obligation(self):
        import sys

        sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
        import check_evidence_reconciliation as reconciler

        state, _ = reconciler.states()["MPS-MAT-009#0"]
        self.assertEqual("OPEN", state)


class CompletionObjectMutations(unittest.TestCase):
    """C6. Rule-driven over every finding declaring a completion object, never an ID list.

    The central invariant is unchanged and is what these protect: a closure review must have
    reviewed the closure target EXACTLY. C6 only changes what that target is when a
    completion object has been declared; it never lets ancestry, a descendant, a prefix, or a
    later review stand in for the match.
    """

    ORIGIN = "c2175bbcb798cf1a12a69d26a1504d973e76c284"
    COMPLETION = "3188a11443e33c8c4f68933cf73282108957f356"

    def observe(self):
        return completion_declaration_problems(load(FINDINGS), load(REVIEWS))

    def test_the_record_as_committed_is_valid(self):
        self.assertEqual([], self.observe())

    def test_the_population_is_not_a_hard_coded_id_list(self):
        import inspect

        source = inspect.getsource(completion_declaration_problems)
        for fid in ("NF-01", "NF-05", "NF-06", "NF-10", "NF-11", "NF-12"):
            self.assertNotIn(fid, source)

    def test_exact_match_to_the_registered_review_object_passes(self):
        declared = {f["id"] for f in load(FINDINGS)["findings"]
                    if f.get("repair_completion_object") == self.COMPLETION}
        self.assertTrue(declared)
        self.assertEqual([], self.observe())

    def test_a_review_of_the_original_repair_only_fails(self):
        """The review verified the repair, but reviewed the introduction commit."""
        with mutated(REVIEWS,
                     "      sha: " + self.COMPLETION + "\n    verdict: INDEPENDENTLY VERIFIED\n"
                     "    reviewer:",
                     "      sha: " + self.ORIGIN + "\n    verdict: INDEPENDENTLY VERIFIED\n"
                     "    reviewer:"):
            problems = self.observe()
        self.assertTrue(any("no registered review both verified" in p for p in problems),
                        problems[:2])

    def test_a_descendant_with_no_completion_field_is_not_the_target(self):
        """Ancestry alone never satisfies the match."""
        finding = {"id": "SYN", "repair": self.ORIGIN}
        self.assertEqual(self.ORIGIN, closure_target(finding),
                         "with no declared completion object the target stays the repair")
        code, _ = git("merge-base", "--is-ancestor", self.ORIGIN, self.COMPLETION)
        self.assertEqual(0, code, "the descendant relation genuinely holds")
        self.assertNotEqual(self.COMPLETION, closure_target(finding),
                            "and it still does not become the target")

    def test_a_completion_object_that_is_not_a_commit_fails(self):
        absent = "deadbeef" * 5  # well-formed, unambiguously a string, resolves to nothing
        code, _ = git("cat-file", "-t", absent)
        self.assertNotEqual(0, code, "the fixture sha must genuinely be absent")
        with mutated(FINDINGS,
                     "    repair_completion_object: " + self.COMPLETION,
                     "    repair_completion_object: " + absent):
            problems = self.observe()
        self.assertTrue(any("does not resolve to a commit" in p for p in problems), problems[:2])

    def test_a_completion_object_yaml_reads_as_a_non_string_fails(self):
        """An all-digit sha is loaded as an integer, and an integer is falsy.

        This case was found by the control above failing for the wrong reason: the observer
        skipped the finding rather than rejecting it, so a declaration that could not be read
        removed itself from the population. That is the defect this register keeps finding one
        level down, so it is now a named case rather than a footnote.
        """
        with mutated(FINDINGS,
                     "    repair_completion_object: " + self.COMPLETION,
                     "    repair_completion_object: " + "0" * 40):
            body = load(FINDINGS)
            problems = self.observe()
        mutant = [f for f in body["findings"] if f["id"] == "NF-01"][0]
        self.assertNotIsInstance(mutant["repair_completion_object"], str,
                                 "the fixture must actually reproduce the coercion")
        self.assertFalse(mutant["repair_completion_object"],
                         "and the coerced value must actually be falsy")
        self.assertTrue(any("NF-01" in p and "is not a commit-object string" in p
                            for p in problems), problems[:2])

    def test_an_origin_that_is_not_an_ancestor_of_the_completion_fails(self):
        """A completion object must not be an arbitrary convenient reviewed commit."""
        code, unrelated = git("rev-parse", "349f2dc")
        self.assertEqual(0, code)
        with mutated(FINDINGS,
                     "    repair_introduced_object: " + self.ORIGIN + "\n"
                     "    repair_completion_object: " + self.COMPLETION,
                     "    repair_introduced_object: " + unrelated + "\n"
                     "    repair_completion_object: " + self.COMPLETION):
            problems = self.observe()
        self.assertTrue(any("is not an ancestor of" in p for p in problems), problems[:2])

    def test_a_completion_object_without_a_reason_fails(self):
        empty = "    repair_completion_reason: " + chr(39) * 2 + "\n    unused_reason: >-"
        with mutated(FINDINGS, "    repair_completion_reason: >-", empty):
            problems = self.observe()
        self.assertTrue(any("no completion reason" in p for p in problems))

    def test_a_completion_reference_resolving_zero_times_fails(self):
        with mutated(REVIEWS, "    verified_repairs_of:\n      - NF-01\n",
                     "    verified_repairs_of:\n"):
            problems = self.observe()
        self.assertTrue(any("NF-01" in p and "no registered review both verified" in p
                            for p in problems))

    def test_a_completion_reference_resolving_more_than_once_fails(self):
        duplicate = ("  - review_id: REV-C5-DUPLICATE\n"
                     "    subject: synthetic duplicate verifier\n"
                     "    reviewed_object:\n"
                     "      kind: commit\n"
                     "      sha: " + self.COMPLETION + "\n"
                     "    verdict: INDEPENDENTLY VERIFIED\n"
                     "    verified_repairs_of:\n      - NF-01\n"
                     "    reviewer:\n"
                     "      relationship: r\n"
                     "      identity: unnamed\n"
                     "      satisfies_mps_mat_009_named_reviewer_obligation: false\n"
                     "    primary_artifact_retention: external_not_retained\n\n")
        with mutated(REVIEWS, "  - review_id: REV-C5-CUMULATIVE",
                     duplicate + "  - review_id: REV-C5-CUMULATIVE"):
            problems = self.observe()
        self.assertTrue(any("ambiguity is surfaced" in p for p in problems), problems[:2])

    def test_a_completion_review_with_a_non_closing_verdict_fails(self):
        with mutated(REVIEWS,
                     "      sha: " + self.COMPLETION + "\n    verdict: INDEPENDENTLY VERIFIED",
                     "      sha: " + self.COMPLETION + "\n    verdict: FAIL"):
            problems = self.observe()
        self.assertTrue(any("not a closing verdict" in p for p in problems), problems[:2])

    def test_a_completion_object_one_commit_away_fails(self):
        code, neighbour = git("rev-parse", "c2175bb")
        self.assertEqual(0, code)
        with mutated(FINDINGS,
                     "    repair_completion_object: " + self.COMPLETION,
                     "    repair_completion_object: " + neighbour):
            problems = self.observe()
        self.assertTrue(any("no registered review both verified" in p for p in problems),
                        "off by one commit is not a match")

    def test_prose_without_the_typed_field_confers_nothing(self):
        """A sentence is not the relationship."""
        with mutated(FINDINGS,
                     "    repair_completion_object: " + self.COMPLETION + "\n", ""):
            declared = [f["id"] for f in load(FINDINGS)["findings"]
                        if f.get("repair_completion_object")]
            closure = closure_problems(load(FINDINGS), load(REVIEWS))
        self.assertNotIn("NF-01", declared,
                         "removing the typed field must remove it from the population")
        self.assertEqual([], closure,
                         "and the finding falls back to its original repair target")

    def test_the_original_repair_field_was_never_rewritten(self):
        """History preservation, checked against the record as committed at 349f2dc."""
        code, previous = git("show",
                             "349f2dc:mps/materialization/mps-mat-009/findings.yaml")
        self.assertEqual(0, code)
        before = {f["id"]: f for f in yaml.safe_load(previous)["findings"]}
        for finding in load(FINDINGS)["findings"]:
            completion = finding.get("repair_completion_object")
            if not completion:
                continue
            with self.subTest(finding=finding["id"]):
                self.assertNotEqual(finding["repair"], completion,
                                    "a repair field equal to the completion object would be "
                                    "manufactured equality, not a completion relationship")
                self.assertNotEqual(finding["repair_introduced_object"], completion)
                self.assertEqual(before[finding["id"]]["repair"], finding["repair"])

    def test_no_completion_declaration_moved_a_finding_to_closed(self):
        """C6 changes the model; it performs no closure transition."""
        for finding in load(FINDINGS)["findings"]:
            if finding.get("repair_completion_object"):
                with self.subTest(finding=finding["id"]):
                    self.assertEqual("OPEN", finding.get("state"))

    def test_nf_09_has_no_completion_object(self):
        """Its mechanism was verified; its state-debt queue was not discharged."""
        body, register = load(FINDINGS), load(REVIEWS)
        nf09 = [f for f in body["findings"] if f["id"] == "NF-09"][0]
        self.assertNotIn("repair_completion_object", nf09)
        self.assertEqual("OPEN", nf09["state"])
        review = [r for r in register["reviews"]
                  if r["review_id"] == "REV-C5-CUMULATIVE"][0]
        self.assertNotIn("NF-09", review.get("verified_repairs_of") or [])
        self.assertIn("NF-09", review.get("not_verified_repairs_of") or [])

    def test_nf_13_closure_is_undisturbed(self):
        body = load(FINDINGS)
        nf13 = [f for f in body["findings"] if f["id"] == "NF-13"][0]
        self.assertEqual("CLOSED", nf13["state"])
        self.assertNotIn("repair_completion_object", nf13)
        self.assertEqual(nf13["repair"], closure_target(nf13))
        self.assertEqual([], closure_problems(body, load(REVIEWS)))

    def test_every_mutation_restored_the_files(self):
        self.assertEqual([], self.observe())
        self.assertEqual([], closure_problems(load(FINDINGS), load(REVIEWS)))
        self.assertEqual([], state_completeness_problems(load(FINDINGS)))


if __name__ == "__main__":
    unittest.main()
