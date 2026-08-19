#!/usr/bin/env python3
"""Verify the live MPS module graph against the controlled blueprint.

Read-only. MPS owns its persistence and this tool never writes to it; ADR-001 and
ADR1-R-05 prohibit any text tool from authoring or patching MPS files.

MPS records inter-language relationships in two places, and both are part of the
dependency graph:

  extendedLanguages  concept-level extension; the extended language's concepts are
                     visible in this language's structure aspect
  dependencies       module-level dependency, for behavior and classes

The blueprint declares the exact kind per dependency, so this gate compares each kind
separately. A dependency silently changed from Default to Extends in the IDE, or the
reverse, is rejected: EXTENDS decides whether a concept may take a superconcept from the
target, which is a structural decision, not an IDE convenience. The gate also checks
acyclicity and the concept counts that distinguish one checkpoint from the next.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"
PROJECT_ROOT = REPO_ROOT / "mps" / "NLTPSGovernance"
LANGUAGES_ROOT = PROJECT_ROOT / "languages"

NAMESPACE_RE = re.compile(r'namespace="([^"]+)"')
MODULE_REF_RE = re.compile(r"\(([^)]+)\)")
NODE_RE = re.compile(r"<node ")


def block(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.S)
    return match.group(1) if match else ""


def module_refs(text: str, tag: str, own_name: str) -> set[str]:
    found = {ref for ref in MODULE_REF_RE.findall(block(text, tag)) if ref.startswith("nltps.")}
    found.discard(own_name)
    return found


def read_modules() -> dict[str, dict[str, set[str]]]:
    modules: dict[str, dict[str, set[str]]] = {}
    for descriptor in sorted(LANGUAGES_ROOT.glob("*/*.mpl")):
        text = descriptor.read_text(encoding="utf-8")
        match = NAMESPACE_RE.search(text)
        if match is None:
            raise ValueError(f"{descriptor} has no language namespace")
        name = match.group(1)
        modules[name] = {
            "extends": module_refs(text, "extendedLanguages", name),
            "depends": module_refs(text, "dependencies", name),
        }
    return modules


def concept_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for structure in sorted(LANGUAGES_ROOT.glob("*/models/*.structure.mps")):
        name = structure.name.removesuffix(".structure.mps")
        counts[name] = len(NODE_RE.findall(structure.read_text(encoding="utf-8")))
    return counts


def find_cycle(graph: dict[str, set[str]]) -> list[str]:
    visited: set[str] = set()
    stack: list[str] = []
    on_stack: set[str] = set()

    def visit(node: str) -> list[str]:
        if node in on_stack:
            return stack[stack.index(node):] + [node]
        if node in visited:
            return []
        on_stack.add(node)
        stack.append(node)
        for child in sorted(graph.get(node, ())):
            found = visit(child)
            if found:
                return found
        stack.pop()
        on_stack.discard(node)
        visited.add(node)
        return []

    for node in sorted(graph):
        found = visit(node)
        if found:
            return found
    return []


def check(max_concepts: int | None) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    expected: dict[str, dict[str, set[str]]] = {}
    for entry in blueprint["languages"]:
        by_kind: dict[str, set[str]] = {"extends": set(), "depends": set()}
        for dependency in entry["dependencies"]:
            key = "extends" if dependency["kind"] == "EXTENDS" else "depends"
            by_kind[key].add(dependency["module"])
        expected[entry["name"]] = by_kind

    if not PROJECT_ROOT.exists():
        return ([f"MPS project not found at {PROJECT_ROOT.relative_to(REPO_ROOT)}"], {})

    project_name = blueprint["project"]["name"]
    if PROJECT_ROOT.name != project_name:
        errors.append(f"project directory is {PROJECT_ROOT.name}, expected {project_name}")

    modules = read_modules()
    if set(modules) != set(expected):
        errors.append(
            f"module set differs: found {sorted(modules)}, expected {sorted(expected)}"
        )

    combined: dict[str, set[str]] = {}
    for name, relations in modules.items():
        combined[name] = relations["extends"] | relations["depends"]
        if name not in expected:
            continue
        for kind, label in (("extends", "EXTENDS"), ("depends", "DEFAULT")):
            actual = relations[kind]
            wanted = expected[name][kind]
            if actual == wanted:
                continue
            promoted = sorted(actual - wanted)
            demoted = sorted(wanted - actual)
            detail = []
            if promoted:
                detail.append(f"unexpected {label} on {promoted}")
            if demoted:
                detail.append(f"missing {label} on {demoted}")
            errors.append(f"{name}: " + "; ".join(detail))

    cycle = find_cycle(combined)
    if cycle:
        errors.append(f"module dependency cycle: {' -> '.join(cycle)}")

    counts = concept_counts()
    missing_aspects = sorted(set(expected) - set(counts))
    if missing_aspects:
        errors.append(f"languages without a structure aspect: {missing_aspects}")

    total_concepts = sum(counts.values())
    if max_concepts is not None and total_concepts > max_concepts:
        errors.append(
            f"structure aspects hold {total_concepts} concept nodes, but this checkpoint "
            f"permits at most {max_concepts}"
        )

    summary = {
        "modules": modules,
        "concepts": counts,
        "total_concepts": total_concepts,
        "acyclic": not cycle,
    }
    return errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-concepts",
        type=int,
        default=None,
        help="fail if structure aspects hold more concept nodes than this (MPS-0 uses 0)",
    )
    args = parser.parse_args()
    errors, summary = check(args.max_concepts)
    if errors:
        print("ERROR: MPS module graph gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(summary['modules'])} language modules match the blueprint dependency "
        f"graph; acyclic; {summary['total_concepts']} concept nodes in structure aspects"
    )
    for name in sorted(summary["modules"]):
        relations = summary["modules"][name]
        print(
            f"       {name:<22} extends={sorted(relations['extends']) or '[]'} "
            f"depends={sorted(relations['depends']) or '[]'}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
