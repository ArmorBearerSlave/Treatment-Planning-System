#!/usr/bin/env python3
"""Validate the implementation-neutral NL-TPS four-language MPS skeleton."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"
EXPECTED_LANGUAGES = [
    "nltps.foundation",
    "nltps.governance",
    "nltps.clinicalintent",
    "nltps.realization",
]


def main() -> int:
    document = json.loads(SKELETON.read_text(encoding="utf-8"))
    errors: list[str] = []
    if document.get("schema_version") != "0.1":
        errors.append("unsupported skeleton schema_version")
    languages = document.get("languages", [])
    names = [language.get("name") for language in languages]

    if names != EXPECTED_LANGUAGES:
        errors.append(f"language order/names differ: {names}")
    if len(set(names)) != len(names):
        errors.append("duplicate language name")

    known = set(names)
    dependency_graph: dict[str, list[str]] = {}
    concept_owner: dict[str, str] = {}
    for language in languages:
        name = language.get("name")
        dependencies = language.get("depends_on", [])
        dependency_graph[name] = dependencies
        missing = sorted(set(dependencies) - known)
        if missing:
            errors.append(f"{name} has unknown dependencies: {missing}")
        for concept in language.get("concepts", []):
            if concept in concept_owner:
                errors.append(
                    f"concept {concept} has multiple owners: {concept_owner[concept]} and {name}"
                )
            concept_owner[concept] = name
        if not language.get("root_concepts"):
            errors.append(f"{name} has no root concepts")
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
    if project.get("default_model_persistence") != "file-per-root":
        errors.append("normative persistence default is not file-per-root")
    for prohibited_flag in (
        "patient_data_permitted",
        "clinical_credentials_permitted",
        "direct_persistence_xml_edit_permitted",
    ):
        if project.get(prohibited_flag) is not False:
            errors.append(f"{prohibited_flag} must be false")
    if document.get("implementation_state") != "blueprint_not_live_mps_serialization":
        errors.append("implementation_state must distinguish the blueprint from live MPS serialization")

    if errors:
        print("ERROR: language skeleton validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"PASS: {len(languages)} languages, {len(concept_owner)} uniquely owned concepts, "
        "acyclic dependencies, file-per-root policy, and prohibited-data controls"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
