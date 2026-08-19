#!/usr/bin/env python3
"""Validate the implementation-neutral NL-TPS four-language MPS skeleton."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from schema_subset import validate_json_schema


REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"
ARCHITECTURE_SPEC = REPO_ROOT / "spec" / "architecture.yaml"
TERMINOLOGY_SPEC = REPO_ROOT / "spec" / "terminology.yaml"
SKELETON_SCHEMA = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.schema.json"


def validate_concept_collections(languages: list[dict[str, object]]) -> tuple[list[str], dict[str, str]]:
    errors: list[str] = []
    concept_owner: dict[str, str] = {}
    for language in languages:
        name = str(language.get("name"))
        if "concepts" in language:
            errors.append(f"{name} uses ambiguous legacy collection 'concepts'")
        roots = list(language.get("root_concepts", []))
        non_roots = list(language.get("non_root_concepts", []))
        overlap = sorted(set(roots) & set(non_roots))
        if overlap:
            errors.append(f"{name} declares concepts as both root and non-root: {overlap}")
        if len(roots) != len(set(roots)):
            errors.append(f"{name} has duplicate root concepts")
        if len(non_roots) != len(set(non_roots)):
            errors.append(f"{name} has duplicate non-root concepts")
        if not roots:
            errors.append(f"{name} has no root concepts")
        if not non_roots:
            errors.append(f"{name} has no non-root concepts")
        for concept in roots + non_roots:
            if concept in concept_owner:
                errors.append(
                    f"concept {concept} has multiple owners: {concept_owner[concept]} and {name}"
                )
            else:
                concept_owner[concept] = name
    return errors, concept_owner


def main() -> int:
    document = json.loads(SKELETON.read_text(encoding="utf-8"))
    schema = json.loads(SKELETON_SCHEMA.read_text(encoding="utf-8"))
    validate_json_schema(document, schema)
    architecture = yaml.safe_load(ARCHITECTURE_SPEC.read_text(encoding="utf-8"))
    terminology = yaml.safe_load(TERMINOLOGY_SPEC.read_text(encoding="utf-8"))
    constraints = architecture["mps_language_constraints"]
    baseline = architecture["baseline"]
    identity = terminology["identity"]
    expected_languages = constraints["ordered_languages"]
    allowed_dependencies = constraints["allowed_dependencies"]
    errors: list[str] = []
    if document.get("schema_version") != constraints["skeleton_schema_version"]:
        errors.append("unsupported skeleton schema_version")
    languages = document.get("languages", [])
    names = [language.get("name") for language in languages]

    if names != expected_languages:
        errors.append(f"language order/names differ: {names}")
    if len(set(names)) != len(names):
        errors.append("duplicate language name")

    known = set(names)
    dependency_graph: dict[str, list[str]] = {}
    collection_errors, concept_owner = validate_concept_collections(languages)
    errors.extend(collection_errors)
    for language in languages:
        name = language.get("name")
        # Dependencies are typed. Acyclicity and layering are checked over the flat
        # module set; the EXTENDS/DEFAULT distinction is enforced against the live
        # MPS graph by tools/mps/check_module_graph.py.
        dependencies = [entry["module"] for entry in language.get("dependencies", [])]
        dependency_graph[name] = dependencies
        missing = sorted(set(dependencies) - known)
        if missing:
            errors.append(f"{name} has unknown dependencies: {missing}")
        expected_dependencies = allowed_dependencies.get(name)
        if dependencies != expected_dependencies:
            errors.append(
                f"{name} dependencies differ: expected {expected_dependencies}, found {dependencies}"
            )
        if not language.get("required_constraints"):
            errors.append(f"{name} has no required constraints")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visiting:
            errors.append(f"dependency cycle includes {name}")
            return
        if name in visited:
            return
        visiting.add(name)
        for dependency in dependency_graph.get(name, []):
            visit(dependency)
        visiting.remove(name)
        visited.add(name)

    for language_name in names:
        visit(language_name)

    project = document.get("project", {})
    expected_baseline = f"{baseline['document_id']}-v{baseline['version']}"
    if document.get("architecture_baseline") != expected_baseline:
        errors.append(f"architecture_baseline is not {expected_baseline}")
    if project.get("technology_name") != identity["technology"]["name"]:
        errors.append("technology_name does not match ADR-002")
    if project.get("technology_acronym") != identity["technology"]["acronym"]:
        errors.append("technology_acronym does not match ADR-002")
    if project.get("implementation_alias") != identity["implementation"]["acronym"]:
        errors.append("implementation_alias does not match ADR-002")
    if project.get("default_model_persistence") != constraints["default_model_persistence"]:
        errors.append("normative persistence default is not file-per-root")
    for prohibited_flag, expected_value in constraints["prohibited_project_flags"].items():
        if project.get(prohibited_flag) is not expected_value:
            errors.append(f"{prohibited_flag} must be {expected_value}")
    if document.get("implementation_state") != constraints["implementation_state"]:
        errors.append("implementation_state must distinguish the blueprint from live MPS serialization")

    if errors:
        print("ERROR: language skeleton validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"PASS: {len(languages)} languages, {len(concept_owner)} uniquely owned concepts, "
        "disjoint root/non-root collections, ADR-001 dependency layering, "
        "file-per-root policy, and prohibited-data controls"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
