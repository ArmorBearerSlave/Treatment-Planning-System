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
