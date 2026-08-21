#!/usr/bin/env python3
"""Validate the concept feature specification against the language blueprint.

The blueprint names concepts; this specification gives each one a superconcept,
properties, children, references, cardinalities, datatypes, and an editor sketch. The
two must agree exactly, or MPS-1 would be transcribing a design that no longer matches
the inventory it was derived from.

Enforced here:

  * every blueprint concept has exactly one feature specification and no others exist;
  * rootable matches the blueprint's root and non-root split;
  * every superconcept resolves to BaseConcept, a concept in the same language, or a
    concept in a language reachable by an EXTENDS dependency -- a DEFAULT dependency
    does not make a concept available as a superconcept;
  * properties and references are single-valued and children may be multi-valued,
    matching what the MPS metamodel can actually express;
  * every declared datatype is used and every used datatype is declared;
  * every blueprint required_constraint is realized by at least one specified constraint,
    and every specified constraint carries a negative example.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"
FEATURES_PATH = REPO_ROOT / "mps" / "bootstrap" / "mps1-concept-features.yaml"

BUILTIN_SUPERCONCEPTS = {"BaseConcept"}
# MPS offers exactly three primitive datatypes. real and date are deliberately absent:
# MPS-1 declared them, discovered during materialization that no such primitive exists,
# and resolved them to string carrying a pattern. Accepting them here would let the same
# discovery recur at MPS-2 authoring time instead of at freeze time. A logical type that
# differs from its storage type is recorded on the property as logical_type.
PRIMITIVE_TYPES = {"string", "integer", "boolean"}
UNREPRESENTABLE_PRIMITIVES = {
    "real": "string carrying a numeric pattern",
    "date": "string carrying a YYYY-MM-DD pattern plus a calendar-validity rule",
}
# MPS admits multi-cardinality only on children. A PropertyDeclaration has no
# cardinality feature at all -- properties are single-valued -- and a reference
# LinkDeclaration is 1 or 0..1, because multi-valued links are aggregations.
# Modelling a list therefore requires a child of an entry concept, not a property
# or reference with an n cardinality.
CARDINALITIES = {"1", "0..1", "1..n", "0..n"}
SINGLE_VALUED = {"1", "0..1"}


def extends_closure(blueprint: dict) -> dict[str, set[str]]:
    """Every language reachable from each language by following EXTENDS transitively.

    Role languages inherit through a chain: roles.radonc EXTENDS roles.common EXTENDS
    foundation, so a foundation superconcept sits two hops away and is legal even though
    no direct edge exists. Resolving only direct targets would reject it.

    The result excludes the language itself, so callers keep "own language" and
    "inherited from an ancestor" as separate, readable cases. A cycle in the declared
    EXTENDS graph terminates instead of recursing forever; the module graph gate is what
    reports the cycle itself.
    """
    direct: dict[str, set[str]] = {}
    for entry in blueprint["languages"]:
        direct[entry["name"]] = {
            dependency["module"]
            for dependency in entry["dependencies"]
            if dependency["kind"] == "EXTENDS"
        }

    closure: dict[str, set[str]] = {}
    for name in direct:
        seen: set[str] = set()
        frontier = list(direct.get(name, ()))
        while frontier:
            ancestor = frontier.pop()
            if ancestor in seen:
                continue
            seen.add(ancestor)
            frontier.extend(direct.get(ancestor, ()))
        seen.discard(name)
        closure[name] = seen
    return closure


def check(features_path: Path | None = None) -> tuple[list[str], dict[str, int]]:
    """Validate one checkpoint's feature specification against the blueprint.

    Only the named specification's languages are compared to the blueprint inventory, but
    concept ownership and datatypes are resolved across every specification present. A
    later checkpoint inherits from an earlier one -- an MPS-2 concept takes GovernedElement
    as superconcept -- so resolving names against one file alone would report a legal
    inheritance as an unknown concept.
    """
    errors: list[str] = []
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    target = features_path or FEATURES_PATH
    features = yaml.safe_load(target.read_text(encoding="utf-8"))
    # The specification under test is always visible, even when it is not on the standard
    # glob path, so a caller may point this at any file and still get name resolution.
    visible = load_features()
    for language, body in features.get("languages", {}).items():
        known = {c["name"] for c in visible["languages"].get(language, {}).get("concepts", [])}
        slot = visible["languages"].setdefault(language, {"concepts": [], "constraints": []})
        slot["concepts"].extend(c for c in body.get("concepts", []) if c["name"] not in known)
    visible["datatypes"].extend(
        d for d in features.get("datatypes", [])
        if d["name"] not in {x["name"] for x in visible["datatypes"]}
    )

    # One closure, two call sites: superconcept legality and containment legality.
    extends_targets = extends_closure(blueprint)

    blueprint_concepts = {
        entry["name"]: {
            "root": set(entry["root_concepts"]),
            "nonroot": set(entry["non_root_concepts"]),
            "constraints": list(entry["required_constraints"]),
        }
        for entry in blueprint["languages"]
    }

    spec_languages = features.get("languages", {})
    declared_types = {item["name"] for item in visible.get("datatypes", [])}
    used_types: set[str] = set()

    # Ownership spans specifications; duplicate ownership within one is still a defect.
    concept_owner: dict[str, str] = {}
    for language, body in visible.get("languages", {}).items():
        for concept in body.get("concepts", []):
            concept_owner[concept["name"]] = language
    seen_here: dict[str, str] = {}
    for language, body in spec_languages.items():
        for concept in body.get("concepts", []):
            name = concept["name"]
            if name in seen_here:
                errors.append(f"{name} is specified in {seen_here[name]} and {language}")
            seen_here[name] = language

    counts = {"concepts": 0, "constraints": 0, "languages": len(spec_languages)}

    for language, body in spec_languages.items():
        if language not in blueprint_concepts:
            errors.append(f"specification covers unknown language {language}")
            continue
        expected_root = blueprint_concepts[language]["root"]
        expected_nonroot = blueprint_concepts[language]["nonroot"]
        expected_all = expected_root | expected_nonroot

        specified = {concept["name"] for concept in body.get("concepts", [])}
        missing = sorted(expected_all - specified)
        extra = sorted(specified - expected_all)
        if missing:
            errors.append(f"{language}: blueprint concepts without a feature spec: {missing}")
        if extra:
            errors.append(f"{language}: feature specs with no blueprint concept: {extra}")

        for concept in body.get("concepts", []):
            counts["concepts"] += 1
            name = concept["name"]
            label = f"{language}.{name}"

            if name in expected_root and concept.get("rootable") is not True:
                errors.append(f"{label} is a blueprint root concept but rootable is not true")
            if name in expected_nonroot and concept.get("rootable") is not False:
                errors.append(f"{label} is a blueprint non-root concept but rootable is not false")

            superconcept = concept.get("superconcept")
            if not superconcept:
                errors.append(f"{label} declares no superconcept")
            elif superconcept not in BUILTIN_SUPERCONCEPTS:
                owner = concept_owner.get(superconcept)
                if owner is None:
                    errors.append(f"{label} extends unknown concept {superconcept}")
                elif owner != language and owner not in extends_targets.get(language, set()):
                    errors.append(
                        f"{label} extends {superconcept} from {owner}, but {owner} is not "
                        f"{language} nor any of its transitive EXTENDS ancestors "
                        f"{sorted(extends_targets.get(language, set())) or '[]'}; a "
                        f"superconcept requires EXTENDS, a DEFAULT dependency permits "
                        f"references only"
                    )

            for prop in concept.get("properties", []):
                kind = prop.get("type")
                if kind in PRIMITIVE_TYPES:
                    pass
                elif kind in declared_types:
                    used_types.add(kind)
                elif kind in UNREPRESENTABLE_PRIMITIVES:
                    errors.append(
                        f"{label}.{prop.get('name')} declares type {kind!r}, which MPS has "
                        f"no primitive for; store it as "
                        f"{UNREPRESENTABLE_PRIMITIVES[kind]} and record logical_type: {kind}"
                    )
                else:
                    errors.append(f"{label}.{prop.get('name')} has unknown type {kind!r}")
                cardinality = prop.get("cardinality")
                if cardinality not in CARDINALITIES:
                    errors.append(
                        f"{label}.{prop.get('name')} has unsupported cardinality "
                        f"{cardinality!r}"
                    )
                elif cardinality not in SINGLE_VALUED:
                    errors.append(
                        f"{label}.{prop.get('name')} declares cardinality {cardinality!r}, "
                        f"but an MPS property is single-valued; model the list as a child "
                        f"of an entry concept"
                    )
                pattern = prop.get("pattern")
                if pattern is not None:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        errors.append(f"{label}.{prop.get('name')} pattern is invalid: {exc}")

            for kind_name in ("children", "references"):
                for link in concept.get(kind_name, []):
                    target = link.get("target")
                    if target not in concept_owner:
                        errors.append(
                            f"{label}.{link.get('name')} targets unknown concept {target!r}"
                        )
                    elif kind_name == "children":
                        # Containment is stronger than reference. A concept may hold only
                        # what its own language or an EXTENDS ancestor owns; a DEFAULT
                        # dependency makes a concept referable, never containable.
                        target_owner = concept_owner[target]
                        permitted = {language} | extends_targets.get(language, set())
                        if target_owner not in permitted:
                            errors.append(
                                f"{label}.{link.get('name')} contains {target} owned by "
                                f"{target_owner}, which is neither {language} nor one of "
                                f"its transitive EXTENDS ancestors "
                                f"{sorted(extends_targets.get(language, set())) or '[]'}; "
                                f"a DEFAULT dependency permits references, not containment"
                            )
                    cardinality = link.get("cardinality")
                    if cardinality not in CARDINALITIES:
                        errors.append(
                            f"{label}.{link.get('name')} has unsupported cardinality "
                            f"{cardinality!r}"
                        )
                    elif kind_name == "references" and cardinality not in SINGLE_VALUED:
                        errors.append(
                            f"{label}.{link.get('name')} declares cardinality "
                            f"{cardinality!r}, but an MPS reference link is single-valued; "
                            f"model the collection as a child of a reference-holder concept"
                        )

            if not concept.get("editor"):
                errors.append(f"{label} has no editor projection")
            if not concept.get("intent"):
                errors.append(f"{label} has no stated intent")

        specified_constraints = body.get("constraints", [])
        counts["constraints"] += len(specified_constraints)
        realized = {entry.get("source_constraint") for entry in specified_constraints}
        for required in blueprint_concepts[language]["constraints"]:
            if required not in realized:
                errors.append(
                    f"{language}: blueprint constraint is not realized: {required!r}"
                )
        constraint_ids = {entry["id"] for entry in specified_constraints}
        for entry in specified_constraints:
            if not entry.get("negative_example"):
                errors.append(f"{entry['id']} has no negative example")
        for concept in body.get("concepts", []):
            for referenced in concept.get("constraints", []):
                if referenced not in constraint_ids:
                    errors.append(
                        f"{language}.{concept['name']} references unknown constraint {referenced}"
                    )

    own_types = {item["name"] for item in features.get("datatypes", [])}
    unused = sorted(own_types - used_types)
    if unused:
        errors.append(f"declared datatypes never used: {unused}")

    if features.get("status") == "approved":
        errors.append(
            "the feature specification claims approved status; approval is recorded by "
            "governance, not asserted in the artifact"
        )

    return errors, counts


def feature_specs() -> list[Path]:
    """Every checkpoint feature specification present, in checkpoint order."""
    return sorted(FEATURES_PATH.parent.glob("mps*-concept-features.yaml"))


def load_features(paths: list[Path] | None = None) -> dict:
    """Merge the feature specifications into one view of the declared model.

    Reachability has to span checkpoints. A container introduced at MPS-2 makes an
    MPS-1 concept instantiable, which is exactly the event the non-instantiability
    deferrals are keyed to; reading only the MPS-1 specification would leave the lapse
    rule blind at the checkpoint it exists for, and it would fail silently, by not
    firing. Callers that mean one specific specification pass it explicitly.
    """
    merged: dict = {"datatypes": [], "languages": {}}
    for path in paths if paths is not None else feature_specs():
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        merged["datatypes"].extend(document.get("datatypes", []))
        for language, body in document.get("languages", {}).items():
            target = merged["languages"].setdefault(language, {"concepts": [], "constraints": []})
            target["concepts"].extend(body.get("concepts", []))
            target["constraints"].extend(body.get("constraints", []))
    return merged


def compute_reachability(features: dict | None = None) -> dict[str, object]:
    """Which specified concepts can actually hold an instance under some root.

    A constraint that cannot be instantiated cannot be behaviourally proven, so the
    checkpoint needs to know which concrete concepts no legal containment path reaches.
    With no argument this spans every feature specification present, so a container added
    at a later checkpoint is seen.
    Traversal starts at the rootable concepts and follows child containment, counting
    children inherited from superconcepts and allowing any subconcept to stand where its
    superconcept is declared as the target. Abstract concepts are never instantiated
    directly and are therefore exempt from the orphan report.
    """
    if features is None:
        features = load_features()

    meta: dict[str, dict[str, object]] = {}
    for language, body in features.get("languages", {}).items():
        for concept in body.get("concepts", []):
            meta[concept["name"]] = {
                "language": language,
                "abstract": bool(concept.get("abstract")),
                "rootable": bool(concept.get("rootable")),
                "superconcept": concept.get("superconcept"),
                "children": [c["target"] for c in concept.get("children", [])],
            }

    # name -> the concept plus everything that descends from it, so a child role
    # declared against a superconcept also admits every subconcept.
    substitutes: dict[str, set[str]] = {name: {name} for name in meta}
    for name in meta:
        parent = meta[name]["superconcept"]
        while parent in meta:
            substitutes[parent].add(name)
            parent = meta[parent]["superconcept"]

    def effective_children(name: str) -> list[str]:
        targets: list[str] = []
        current = name
        while current in meta:
            targets.extend(meta[current]["children"])
            current = meta[current]["superconcept"]
        return targets

    reachable = {name for name, info in meta.items() if info["rootable"]}
    frontier = list(reachable)
    while frontier:
        current = frontier.pop()
        for target in effective_children(current):
            for candidate in substitutes.get(target, {target}):
                if candidate in meta and candidate not in reachable:
                    reachable.add(candidate)
                    frontier.append(candidate)

    unreachable = sorted(
        name
        for name, info in meta.items()
        if not info["rootable"] and not info["abstract"] and name not in reachable
    )

    # Whether an instance can exist at all, which is a different question from the orphan
    # report. An abstract concept is never instantiated directly, so it is instantiable
    # only through a concrete subconcept that is itself reachable. A deferral justified by
    # non-instantiability must key on this, not on the orphan report: an abstract concept
    # never appears there and would otherwise look as though its deferral had gone stale.
    instantiable = set()
    for name, info in meta.items():
        candidates = (
            {c for c in substitutes[name] if not meta[c]["abstract"]}
            if info["abstract"]
            else {name}
        )
        if any(c in reachable for c in candidates):
            instantiable.add(name)

    return {
        "reachable": reachable,
        "unreachable": unreachable,
        "instantiable": instantiable,
        "concepts": meta,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    total = {"concepts": 0, "constraints": 0, "languages": 0}
    failed = False
    for spec in feature_specs():
        errors, counts = check(spec)
        if errors:
            failed = True
            print(
                f"ERROR: concept feature specification gate failed for {spec.name}",
                file=sys.stderr,
            )
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            continue
        for key in total:
            total[key] += counts[key]
        print(
            f"PASS: {spec.name}: {counts['concepts']} concepts across "
            f"{counts['languages']} languages carry a feature specification; "
            f"superconcepts respect EXTENDS discipline; {counts['constraints']} "
            f"constraints realize every blueprint requirement"
        )
    if failed:
        return 1
    counts = total
    unreachable = compute_reachability()["unreachable"]
    if unreachable:
        # Reported, not failed: a concept with no containment path is a known and
        # recorded state at this checkpoint. check_materialization_plan.py is what
        # turns that state into an obligation, by expiring any proof deferral whose
        # affected concept has since become reachable.
        print(
            f"       no containment path from any root reaches: {', '.join(unreachable)} "
            f"-- constraints over these concepts cannot be behaviourally proven yet"
        )
    else:
        print("       every non-rootable concrete concept is reachable from some root")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
