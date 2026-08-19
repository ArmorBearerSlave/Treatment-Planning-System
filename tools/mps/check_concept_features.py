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
  * every property, child, and reference target resolves and carries a cardinality;
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
PRIMITIVE_TYPES = {"string", "integer", "real", "boolean", "date"}
CARDINALITIES = {"1", "0..1", "1..n", "0..n"}


def check() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    features = yaml.safe_load(FEATURES_PATH.read_text(encoding="utf-8"))

    extends_targets: dict[str, set[str]] = {}
    for entry in blueprint["languages"]:
        extends_targets[entry["name"]] = {
            dependency["module"]
            for dependency in entry["dependencies"]
            if dependency["kind"] == "EXTENDS"
        }

    blueprint_concepts = {
        entry["name"]: {
            "root": set(entry["root_concepts"]),
            "nonroot": set(entry["non_root_concepts"]),
            "constraints": list(entry["required_constraints"]),
        }
        for entry in blueprint["languages"]
    }

    spec_languages = features.get("languages", {})
    declared_types = {item["name"] for item in features.get("datatypes", [])}
    used_types: set[str] = set()

    concept_owner: dict[str, str] = {}
    for language, body in spec_languages.items():
        for concept in body.get("concepts", []):
            name = concept["name"]
            if name in concept_owner:
                errors.append(f"{name} is specified in {concept_owner[name]} and {language}")
            concept_owner[name] = language

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
                        f"{label} extends {superconcept} from {owner}, but {language} "
                        f"declares {owner} with kind DEFAULT; a superconcept requires EXTENDS"
                    )

            for prop in concept.get("properties", []):
                kind = prop.get("type")
                if kind in PRIMITIVE_TYPES:
                    pass
                elif kind in declared_types:
                    used_types.add(kind)
                else:
                    errors.append(f"{label}.{prop.get('name')} has unknown type {kind!r}")
                if prop.get("cardinality") not in CARDINALITIES:
                    errors.append(
                        f"{label}.{prop.get('name')} has unsupported cardinality "
                        f"{prop.get('cardinality')!r}"
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
                    if link.get("cardinality") not in CARDINALITIES:
                        errors.append(
                            f"{label}.{link.get('name')} has unsupported cardinality "
                            f"{link.get('cardinality')!r}"
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

    unused = sorted(declared_types - used_types)
    if unused:
        errors.append(f"declared datatypes never used: {unused}")

    if features.get("status") == "approved":
        errors.append(
            "the feature specification claims approved status; approval is recorded by "
            "governance, not asserted in the artifact"
        )

    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors, counts = check()
    if errors:
        print("ERROR: concept feature specification gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {counts['concepts']} concepts across {counts['languages']} languages carry "
        f"a feature specification; superconcepts respect EXTENDS discipline; "
        f"{counts['constraints']} constraints realize every blueprint requirement"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
