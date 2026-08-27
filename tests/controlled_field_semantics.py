"""One interpretation of the controlled presence fields, for every consumer that reads them.

NF-23. C8 repaired review-object identity inside the closure observer and left a second live
implementation in tests/test_review_records.py, still spelling the withdrawn semantics
`obj.get("sha") or obj.get("later_committed_as")`. The two disagreed on seven of ten cases,
including a falsy `sha` with a usable `later_committed_as`, a `commit` carrying only
`later_committed_as`, and a `working_tree` carrying only `sha`. One controlled representation
had two interpretations, and a control asserting that every review identifies the object it
reviewed was accepting shapes the closure rule rejects.

So the semantics live here, once, and both consumers import them. This module is deliberately
not named `test_*`: it is the shared meaning, not a suite, and unittest discovery does not
collect it.

NF-27. The uniformity observer that guards those semantics reads the module's PARSE TREE
rather than a walk of its functions. C8 derived its units from module functions and class
methods, which silently excluded every executable statement at module scope -- and a module
scope assignment is executable code that runs on import, so it was the one place a consumer
could sit unobserved. The gap was prospective, not occupied: no module-scope violation existed
at 0db0213. It is closed anyway, because an observer whose population is narrower than its
claim is the defect this register keeps finding one level down.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# The fields whose presence semantics are controlled. Read from here by every consumer, so
# adding one is a single edit rather than a search.
IDENTITY_FIELDS = ("sha", "later_committed_as")
COMPLETION_FIELD = "repair_completion_object"
CONTROLLED_PRESENCE_FIELDS = (COMPLETION_FIELD, *IDENTITY_FIELDS)

# Which identity field each declared review-object kind carries. Derived from the controlled
# register's own shape: a `commit` review names the commit it reviewed; a `working_tree` review
# reviewed something uncommitted and can only say what it was afterwards committed as. They are
# different propositions about different things, which is why neither substitutes for the other.
IDENTITY_FIELD_BY_KIND = {
    "commit": "sha",
    "working_tree": "later_committed_as",
}

FULL_OBJECT = re.compile(r"^[0-9a-f]{40}$")


def usable_object(value) -> bool:
    """A value that could name a git object. Not that it does -- that needs the repository."""
    return isinstance(value, str) and bool(value.strip())


def reviewed_identity(review: dict) -> tuple:
    """The object a review reviewed, and why it is unusable when it is.

    Returns (value, problem). `problem` is None exactly when the identity is declared once,
    matches its declared kind, and could name an object.

    Declaration is key membership, never truthiness. A field written with no value, or as "",
    0 or false, is a field somebody wrote: present, declared and invalid. Truthiness collapsed
    that case into absence and then redirected to the other field, which does not name the
    same thing.
    """
    obj = review.get("reviewed_object")
    rid = review.get("review_id", "<unnamed review>")

    if isinstance(obj, str):
        return (obj, None) if usable_object(obj) else (
            None, f"{rid}: reviewed_object is a string that cannot name an object")
    if not isinstance(obj, dict):
        return None, f"{rid}: declares no reviewed_object"

    declared = [f for f in IDENTITY_FIELDS if f in obj]
    if not declared:
        return None, (f"{rid}: reviewed_object declares neither "
                      f"{' nor '.join(IDENTITY_FIELDS)}")
    if len(declared) > 1:
        return None, (f"{rid}: reviewed_object declares both {' and '.join(declared)}; they "
                      f"name different things and the ambiguity is surfaced, not resolved by "
                      f"precedence")

    field = declared[0]
    kind = obj.get("kind")
    if kind not in IDENTITY_FIELD_BY_KIND:
        return None, (f"{rid}: reviewed_object kind {kind!r} is not a controlled kind, so "
                      f"which field carries its identity is undefined")
    expected = IDENTITY_FIELD_BY_KIND[kind]
    if field != expected:
        return None, (f"{rid}: kind {kind!r} carries its identity in {expected!r}, but the "
                      f"record declares {field!r}; the wrong-kind field never substitutes")

    value = obj[field]
    if not usable_object(value):
        return None, (f"{rid}: {field} is declared but cannot name an object ({value!r}); a "
                      f"declared identity is never replaced by the other field")
    return value, None


def reviewed_sha(review: dict):
    """The reviewed identity, or None when it is absent, ambiguous, wrong-kind or unusable.

    Fails closed by construction: every rejected case yields None, and None never equals a
    closure target, so no rejected identity can produce a match.
    """
    value, problem = reviewed_identity(review)
    return None if problem else value


def identity_declaration_problems(register_body: dict) -> list[str]:
    """Every review declares its object identity once, correctly for its kind, and usably."""
    problems = []
    for review in register_body.get("reviews") or []:
        _, problem = reviewed_identity(review)
        if problem:
            problems.append(problem)
    return problems


# --------------------------------------------------------------------------------------
# uniformity: no consumer may reinstate the withdrawn truthiness reading
# --------------------------------------------------------------------------------------

def _controlled_field_name(node) -> str | None:
    """The controlled field a call argument names, spelled literally or through a constant."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value if node.value in CONTROLLED_PRESENCE_FIELDS else None
    if isinstance(node, ast.Name) and node.id in ("COMPLETION_FIELD",):
        return COMPLETION_FIELD
    return None


def _enclosing_units(tree: ast.AST) -> dict:
    """Line number -> the qualified name of the definition containing it, or '<module scope>'.

    NF-27. The default is module scope rather than "not covered". A site that belongs to no
    function still belongs to the module, and the previous observer treated exactly that case
    as outside its population.
    """
    owners = {}

    def walk(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}{child.name}"
                # Descend FIRST, so the innermost definition claims a line. Claiming on the
                # way down attributes a method's body to its class, which reads as though the
                # method were not observed at all.
                walk(child, prefix=f"{name}.")
                for sub in ast.walk(child):
                    line = getattr(sub, "lineno", None)
                    if line is not None:
                        owners.setdefault(line, name)
            else:
                walk(child, prefix=prefix)

    walk(tree)
    return owners


def truthiness_declaration_sites(source: str, unit: str) -> list[str]:
    """Every `.get(<controlled field>)` in `source`: a declaration test by truthiness.

    The whole parse tree is walked, so module-scope statements, functions, methods,
    comprehensions and nested definitions are all in the population by construction rather
    than by enumeration.

    What is reported is the `.get(field)` CALL. That is the defect whether its result is
    branched on, filtered on or compared, because all three read a field that may not be there
    and answer with a value indistinguishable from a declared falsy one.

    Deliberately not reported, so the correct pattern is not pushed back toward the wrong one:
    indexing after presence is established (`obj[field]`), `.get()` on any other field where
    truthiness is semantically fine, and string literals naming the forbidden syntax -- a
    literal is an ast.Constant and never an ast.Call, so a control describing this rule in
    prose or asserting on its text is not flagged by it. This is the reason the check is an
    AST walk and not a text search: a text search flags its own negative controls.
    """
    tree = ast.parse(source)
    owners = _enclosing_units(tree)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute) and node.func.attr == "get"):
            continue
        if not node.args:
            continue
        field = _controlled_field_name(node.args[0])
        if field is None:
            continue
        owner = owners.get(node.lineno, "<module scope>")
        found.append(f"{unit}:{node.lineno} ({owner}): .get({field!r}) tests declaration by "
                     f"truthiness; use key membership, then index")
    return found


def identity_consumer_modules() -> list[Path]:
    """Every controlled Python module that mentions a controlled presence field.

    Derived by parsing, not by a maintained list of the two modules that happen to be known.
    A third consumer added tomorrow is in this population the moment it names a field.
    """
    consumers = []
    for path in sorted((*(REPO_ROOT / "tests").rglob("*.py"),
                        *(REPO_ROOT / "tools").rglob("*.py"))):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):        # pragma: no cover - none present
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value in CONTROLLED_PRESENCE_FIELDS:
                consumers.append(path)
                break
    return consumers


def uniformity_problems(target=None) -> list[str]:
    """No consumer reads a controlled presence field by truthiness.

    With no argument the population is the whole derived consumer set. A module object or a
    path narrows it to one, which is what the per-module controls use.
    """
    if target is None:
        paths = identity_consumer_modules()
    elif isinstance(target, Path):
        paths = [target]
    else:
        paths = [Path(target.__file__).resolve()]

    problems = []
    for path in paths:
        unit = path.relative_to(REPO_ROOT).as_posix()
        problems.extend(truthiness_declaration_sites(
            path.read_text(encoding="utf-8"), unit))
    return problems


# ==========================================================================================
# per-finding review authority -- NF-33 / IR-03, NF-36 / IR-06, NF-31 / IR-01
#
# One implementation, imported by every consumer, for the same reason the identity semantics
# above live here: NF-23 recorded what happens when one controlled representation acquires two
# readings, and the answer was that the more permissive reading survives and the register calls
# it verified.
#
# Two questions, deliberately separate, each with exactly one machine-authoritative answer:
#
#   "Did this review verify this finding's repair?"    -> repair_support
#   "Did this review authorize closing this finding?"  -> closure_authority
#
# Both are read ONLY from reviews[].per_finding_authority. verified_repairs_of is historical and
# non-authoritative, warrants_closure_of is derived and reconciled, and no prose field is ever
# consulted. AUTHORITY_SOURCE_FIELD names the one location, so a consumer that reads anything
# else is visible to the uniformity control rather than merely discouraged.
# ==========================================================================================

AUTHORITY_SOURCE_FIELD = "per_finding_authority"
LEGACY_SUPPORT_FIELD = "verified_repairs_of"
DERIVED_GRANT_FIELD = "warrants_closure_of"
RETAINED_DETERMINATION_FIELD = "per_finding_determinations"


def authority_model(register_body: dict) -> dict:
    """The controlled model. Read from the register, never duplicated as literals in code.

    The closing value, both vocabularies and the retained-determination mapping are controlled
    data. A control that carries its own copy of a rule stops testing the rule and starts
    testing its copy, and the two agree until they do not -- closing_verdicts is already
    handled this way and this follows it.
    """
    return register_body["per_finding_authority_model"]


def per_finding_authority(review: dict, finding_id: str):
    """What this review declares about this finding, or None if it declares nothing.

    Absence is not a grant and not a denial. A review that says nothing about a finding has
    answered neither question, and the caller must treat that as unauthorized rather than as
    permission -- which is what makes the requirement positive.
    """
    table = review.get(AUTHORITY_SOURCE_FIELD)
    if not isinstance(table, dict):
        return None
    entry = table.get(finding_id)
    return entry if isinstance(entry, dict) else None


def grants_closure(review: dict, finding_id: str, register_body: dict) -> bool:
    """The one predicate that decides whether a review authorizes closing a finding."""
    entry = per_finding_authority(review, finding_id)
    if entry is None:
        return False
    return entry.get("closure_authority") == authority_model(register_body)["closure_requires"]


def verifies_repair(review: dict, finding_id: str, register_body: dict) -> bool:
    """The one predicate that decides whether a review verified a finding's repair."""
    entry = per_finding_authority(review, finding_id)
    if entry is None:
        return False
    return entry.get("repair_support") == "VERIFIED"


def authority_vocabulary_problems(register_body: dict) -> list[str]:
    """Every declared value comes from the controlled vocabulary, and the shape is a mapping."""
    model = authority_model(register_body)
    support = set(model["repair_support_values"])
    grants = set(model["closure_authority_values"])
    problems: list[str] = []
    for review in register_body.get("reviews") or []:
        rid = review.get("review_id")
        table = review.get(AUTHORITY_SOURCE_FIELD)
        if table is None:
            continue
        if not isinstance(table, dict):
            problems.append(f"{rid}: {AUTHORITY_SOURCE_FIELD} is not a finding-keyed mapping")
            continue
        for fid, entry in table.items():
            if not isinstance(entry, dict):
                problems.append(f"{rid}/{fid}: authority entry is not a record")
                continue
            rs, ca = entry.get("repair_support"), entry.get("closure_authority")
            if rs not in support:
                problems.append(f"{rid}/{fid}: repair_support {rs!r} is not in the controlled "
                                f"vocabulary")
            if ca not in grants:
                problems.append(f"{rid}/{fid}: closure_authority {ca!r} is not in the "
                                f"controlled vocabulary")
            if not str(entry.get("basis", "")).strip():
                problems.append(f"{rid}/{fid}: authority determination states no basis")
            # A grant over a repair the same review could not verify is self-contradictory.
            if ca == model["closure_requires"] and rs == "NOT_VERIFIED":
                problems.append(f"{rid}/{fid}: grants closure authority while recording the "
                                f"repair NOT_VERIFIED; the determinations contradict")
    return problems


def authority_reconciliation_problems(register_body: dict) -> list[str]:
    """The convenience lists may not diverge from the canonical structure.

    warrants_closure_of is DERIVED: it must equal exactly the set of findings this review grants,
    in both directions. verified_repairs_of is HISTORICAL: it is permitted to disagree, because
    deleting it would destroy the provenance record that makes NF-36 legible, but the
    disagreement must be declared on the review rather than sitting there looking like authority.
    """
    model = authority_model(register_body)
    derived = model["derived_and_reconciled_fields"]
    problems: list[str] = []
    for review in register_body.get("reviews") or []:
        rid = review.get("review_id")
        table = review.get(AUTHORITY_SOURCE_FIELD) or {}
        granted = {f for f, e in table.items()
                   if isinstance(e, dict)
                   and e.get("closure_authority") == model["closure_requires"]}

        if DERIVED_GRANT_FIELD in review:
            listed = set(review[DERIVED_GRANT_FIELD] or [])
            if listed != granted:
                problems.append(
                    f"{rid}: {DERIVED_GRANT_FIELD} {sorted(listed)} does not equal the findings "
                    f"this review grants closure authority {sorted(granted)}; the convenience "
                    f"list is derived and may not diverge")
        elif granted:
            problems.append(f"{rid}: grants closure authority for {sorted(granted)} but declares "
                            f"no {DERIVED_GRANT_FIELD}; the derived list must be present when "
                            f"the review grants anything")

        if LEGACY_SUPPORT_FIELD in review:
            status = (review.get(f"{LEGACY_SUPPORT_FIELD}_authority") or {})
            if status.get("status") != derived[LEGACY_SUPPORT_FIELD]["status"]:
                problems.append(
                    f"{rid}: carries {LEGACY_SUPPORT_FIELD} without declaring it "
                    f"{derived[LEGACY_SUPPORT_FIELD]['status']}; a field that answers no "
                    f"controlled question must say so")
                continue
            verified = {f for f, e in table.items()
                        if isinstance(e, dict) and e.get("repair_support") == "VERIFIED"}
            listed = set(review[LEGACY_SUPPORT_FIELD] or [])
            declared = status.get("declared_divergence_from_canonical") or {}
            actual = listed - verified
            stated = set(declared.get("diverges_on") or [])
            if actual != stated:
                problems.append(
                    f"{rid}: {LEGACY_SUPPORT_FIELD} diverges from the canonical structure on "
                    f"{sorted(actual)}, but the record declares the divergence as "
                    f"{sorted(stated)}; an undeclared divergence is how this field became "
                    f"authority in the first place")
    return problems


def closure_authority_problems(findings_body: dict, register_body: dict) -> list[str]:
    """NF-33 / IR-03. Closure requires a POSITIVE per-finding grant from the selected review.

    A closing review-LEVEL verdict is necessary and never sufficient. Every one of these fails:
    a review that verifies the repair and grants nothing; a review whose scope declares it makes
    no lifecycle disposition; a review silent about the finding; a review that grants only some
    other finding. Each of those returned zero problems at 00c6e2f, and the four transitions this
    checkpoint is recovering from went through the first two.
    """
    model = authority_model(register_body)
    required = model["closure_requires"]
    rule = register_body["closure_rule"]
    state_field = findings_body["finding_state_control"]["canonical_field"]
    by_id = {r.get("review_id"): r for r in register_body.get("reviews") or []}

    problems: list[str] = []
    for finding in findings_body["findings"]:
        if finding.get(state_field) != rule["applies_to_finding_state"]:
            continue
        fid = finding["id"]
        reference = finding.get(rule["requires_field"])
        review = by_id.get(reference)
        if review is None:
            continue  # absent or unresolvable warrant is closure_problems' report, not restated
        entry = per_finding_authority(review, fid)
        if entry is None:
            problems.append(
                f"{fid}: closure warrant {reference} declares no per-finding authority for it. "
                f"A review-level verdict is not a closure grant, and silence is not permission")
            continue
        actual = entry.get("closure_authority")
        if actual != required:
            problems.append(
                f"{fid}: closure warrant {reference} records closure_authority {actual!r}; only "
                f"{required!r} authorizes a closure")
    return problems


def _mechanism_applies(mechanism: dict, finding: dict, completion_field: str) -> bool:
    when = mechanism.get("depends_when")
    if when == "always":
        return True
    if when == "finding_declares_completion_object":
        return completion_field in finding
    return True  # an unrecognised dependency rule fails closed: assume it applies


def mechanism_verification_problems(findings_body: dict, register_body: dict) -> list[str]:
    """NF-31 / IR-01. A changed mechanism must be DECLARED verified before it closes anything.

    The safety property is kept and the over-strict reading is dropped: no dedicated review of
    every intermediate commit is required, and an explicitly scoped cumulative review satisfies
    the condition. What is no longer permitted is satisfying it silently. A review verifies a
    mechanism only by declaring, in mechanisms_verified, which mechanism, where it was introduced,
    the exact checkpoint reviewed, that it is present and effective there, and its verdict.

    Ancestry is never sufficient. REV-C9-CUMULATIVE returned a closing verdict against 5ec6b5f,
    a descendant of the object that introduced the closure-completion model, and says nothing
    about that mechanism -- so it verifies nothing about it, which is exactly the inference
    00c6e2f made and this refuses.
    """
    model = register_body["mechanism_verification_model"]
    mechanisms = register_body.get("mechanisms") or {}
    closing = set(register_body["closure_rule"]["closing_verdicts"])
    state_field = findings_body["finding_state_control"]["canonical_field"]
    applicable = register_body["closure_rule"]["applies_to_finding_state"]
    completion_field = COMPLETION_FIELD
    grandfathered = set(model["grandfathered_closures"]["findings"])

    verified_by: dict[str, list[str]] = {}
    unresolved: list[str] = []
    for review in register_body.get("reviews") or []:
        for entry in review.get("mechanisms_verified") or []:
            name = entry.get("mechanism")
            problem = _mechanism_declaration_problem(entry, mechanisms, closing)
            if problem:
                unresolved.append(f"{review.get('review_id')}: {problem}")
                continue
            verified_by.setdefault(name, []).append(review.get("review_id"))

    problems = list(unresolved)
    for finding in findings_body["findings"]:
        if finding.get(state_field) != applicable:
            continue
        fid = finding["id"]
        if fid in grandfathered:
            continue
        for name, mechanism in sorted(mechanisms.items()):
            if not _mechanism_applies(mechanism, finding, completion_field):
                continue
            if not verified_by.get(name):
                problems.append(
                    f"{fid}: its closure depends on mechanism {name!r}, which no registered "
                    f"review declares verified. A cumulative review of a descendant object does "
                    f"not verify a mechanism it does not name")
    return problems


def _mechanism_declaration_problem(entry: dict, mechanisms: dict, closing: set):
    """All five clauses, typed. A partial declaration verifies nothing rather than something."""
    name = entry.get("mechanism")
    if name not in mechanisms:
        return f"mechanisms_verified names {name!r}, which is not a declared mechanism"
    for key in ("introduced_at", "verified_at_checkpoint", "verdict"):
        if not str(entry.get(key, "")).strip():
            return f"mechanism {name!r} declares no {key}"
    if entry.get("present_and_effective_at_checkpoint") is not True:
        return (f"mechanism {name!r} does not assert it is present and effective at the "
                f"checkpoint; a review of an object where a mechanism is absent verifies nothing")
    if entry.get("verdict") not in closing:
        return f"mechanism {name!r} carries verdict {entry.get('verdict')!r}, which is not verifying"
    declared = mechanisms[name].get("introduced_at")
    if FULL_OBJECT.match(str(declared or "")) and entry["introduced_at"] != declared:
        return (f"mechanism {name!r} is declared introduced at {entry['introduced_at']!r} but the "
                f"register records {declared!r}; the two must be the same object")
    if not FULL_OBJECT.match(str(entry["verified_at_checkpoint"])):
        return (f"mechanism {name!r} names a checkpoint that is not a full object; an "
                f"abbreviation can never establish which object was reviewed")
    return None
