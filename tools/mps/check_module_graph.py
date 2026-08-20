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
import xml.etree.ElementTree as ElementTree
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"
PROJECT_ROOT = REPO_ROOT / "mps" / "NLTPSGovernance"
LANGUAGES_ROOT = PROJECT_ROOT / "languages"

NAMESPACE_RE = re.compile(r'namespace="([^"]+)"')
MODULE_REF_RE = re.compile(r"\(([^)]+)\)")
# A structure aspect represents every element as <node>: a ConceptDeclaration is one,
# and so is each of its properties, children, and references. Counting raw <node>
# elements therefore counts features, not concepts, and overshoots by roughly an order
# of magnitude. The registry maps a per-file index alias to each concept type, so the
# declarations are resolved through it instead.
CONCEPT_DECLARATION_TYPES = {
    "jetbrains.mps.lang.structure.structure.ConceptDeclaration",
    "jetbrains.mps.lang.structure.structure.InterfaceConceptDeclaration",
}


def block(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.S)
    return match.group(1) if match else ""


def module_refs(text: str, tag: str, own_name: str) -> set[str]:
    found = {ref for ref in MODULE_REF_RE.findall(block(text, tag)) if ref.startswith("nltps.")}
    found.discard(own_name)
    return found


def external_refs(text: str, own_name: str) -> set[str]:
    """Explicit non-NL-TPS entries in the .mpl <dependencies> block.

    MPS re-added lang.core and JDK three times during MPS-1, each time unnecessary and
    each time invisible because the NL-TPS filter dropped them. This deliberately does
    not filter. Devkits are declared in the model files under <languages><devkit> and
    never appear in the module descriptor, so nothing new has to be parsed and a devkit
    is not mistaken for an undeclared dependency.
    """
    found = {
        ref
        for ref in MODULE_REF_RE.findall(block(text, "dependencies"))
        if not ref.startswith("nltps.")
    }
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
            "external": external_refs(text, name),
        }
    return modules


def concept_declaration_indices(root: ElementTree.Element) -> set[str]:
    """Resolve the index aliases this file uses for concept declarations."""
    indices: set[str] = set()
    for registry in root.iter("registry"):
        for language in registry.iter("language"):
            for concept in language.findall("concept"):
                if concept.get("name") in CONCEPT_DECLARATION_TYPES:
                    index = concept.get("index")
                    if index:
                        indices.add(index)
    return indices


def count_declared_concepts(text: str) -> tuple[int, int]:
    """Return (concept declarations, total nodes) for one structure aspect."""
    root = ElementTree.fromstring(text)
    nodes = list(root.iter("node"))
    if not nodes:
        return 0, 0
    indices = concept_declaration_indices(root)
    if not indices:
        # Nodes exist but no concept declaration type is registered. The count cannot
        # be verified, so fail closed rather than reporting a reassuring zero.
        raise ValueError(
            "structure aspect contains nodes but registers no ConceptDeclaration "
            "index; concept count cannot be verified"
        )
    declared = sum(1 for node in nodes if node.get("concept") in indices)
    return declared, len(nodes)


def concept_counts() -> tuple[dict[str, int], dict[str, int]]:
    concepts: dict[str, int] = {}
    nodes: dict[str, int] = {}
    for structure in sorted(LANGUAGES_ROOT.glob("*/models/*.structure.mps")):
        name = structure.name.removesuffix(".structure.mps")
        try:
            declared, total = count_declared_concepts(structure.read_text(encoding="utf-8"))
        except ElementTree.ParseError as exc:
            raise ValueError(f"{structure} is not parseable: {exc}") from exc
        concepts[name] = declared
        nodes[name] = total
    return concepts, nodes


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


def checkpoint_ordinal(label: str) -> int:
    """MPS-3 sorts after MPS-1; a malformed label is a blueprint defect, not a zero."""
    match = re.fullmatch(r"MPS-(\d+)", label.strip())
    if match is None:
        raise ValueError(f"checkpoint label must look like MPS-N, got {label!r}")
    return int(match.group(1))


def languages_at(blueprint: dict, checkpoint: str | None) -> list[dict]:
    """Blueprint languages that should exist on disk at the given checkpoint.

    A language declared for a later checkpoint is an expected absence, which is what
    lets the blueprint describe the architecture ahead of materializing it. With no
    checkpoint the whole declared inventory is in scope.
    """
    if checkpoint is None:
        return list(blueprint["languages"])
    limit = checkpoint_ordinal(checkpoint)
    return [
        entry
        for entry in blueprint["languages"]
        if checkpoint_ordinal(entry["materialized_at"]) <= limit
    ]


def expected_concept_count(blueprint: dict, checkpoint: str | None) -> int:
    """The ceiling is the declared inventory, never a literal repeated in CI.

    Scoped by concepts_materialized_at rather than materialized_at: every original
    module exists from MPS-0, but an empty module contributes no concepts. Counting by
    module presence would charge MPS-1 for inventories that do not arrive until later.
    """
    entries = blueprint["languages"]
    if checkpoint is not None:
        limit = checkpoint_ordinal(checkpoint)
        entries = [
            entry
            for entry in entries
            if checkpoint_ordinal(entry["concepts_materialized_at"]) <= limit
        ]
    return sum(
        len(entry["root_concepts"]) + len(entry["non_root_concepts"]) for entry in entries
    )


def declared_checkpoints(blueprint: dict) -> list[str]:
    """Every checkpoint the blueprint mentions, in order."""
    labels = set()
    for entry in blueprint["languages"]:
        labels.add(entry["materialized_at"])
        labels.add(entry["concepts_materialized_at"])
    return sorted(labels, key=checkpoint_ordinal)


def explain(checkpoint: str | None) -> int:
    """Print the checkpoint -> inventory -> ceiling derivation without asserting presence.

    The module-presence check fails first for any checkpoint whose languages are not on
    disk yet, so the ceiling was unobservable until the checkpoint arrived. That is how a
    misallocated inventory survived review: nothing printed the number it would enforce.
    """
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    targets = [checkpoint] if checkpoint else declared_checkpoints(blueprint)
    print("checkpoint  expected  contributing language inventories")
    for label in targets:
        limit = checkpoint_ordinal(label)
        contributing = [
            entry["name"]
            for entry in blueprint["languages"]
            if checkpoint_ordinal(entry["concepts_materialized_at"]) <= limit
        ]
        total = expected_concept_count(blueprint, label)
        print(f"{label:<11} {total:>8}  {', '.join(contributing) or '(none)'}")
    return 0


def check(
    max_concepts: int | None, checkpoint: str | None = None
) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    in_scope = languages_at(blueprint, checkpoint)
    deferred = sorted(
        entry["name"] for entry in blueprint["languages"] if entry not in in_scope
    )
    expected: dict[str, dict[str, set[str]]] = {}
    for entry in in_scope:
        by_kind: dict[str, set[str]] = {"extends": set(), "depends": set()}
        for dependency in entry["dependencies"]:
            key = "extends" if dependency["kind"] == "EXTENDS" else "depends"
            by_kind[key].add(dependency["module"])
        by_kind["external"] = set(entry.get("external_explicit", []))
        expected[entry["name"]] = by_kind

    if checkpoint is not None and max_concepts is None:
        max_concepts = expected_concept_count(blueprint, checkpoint)

    if not PROJECT_ROOT.exists():
        return ([f"MPS project not found at {PROJECT_ROOT.relative_to(REPO_ROOT)}"], {})

    project_name = blueprint["project"]["name"]
    if PROJECT_ROOT.name != project_name:
        errors.append(f"project directory is {PROJECT_ROOT.name}, expected {project_name}")

    modules = read_modules()
    # A language whose checkpoint has not arrived is legitimately absent. Anything on
    # disk that the blueprint does not declare, or declared-and-due but missing, is not.
    undeclared = sorted(set(modules) - set(expected) - set(deferred))
    if undeclared:
        errors.append(
            f"languages present on disk but not declared in the blueprint: {undeclared}"
        )
    premature = sorted(set(modules) & set(deferred))
    if premature:
        errors.append(
            f"languages materialized before their declared checkpoint: {premature}"
        )
    missing = sorted(set(expected) - set(modules))
    if missing:
        errors.append(
            f"languages declared for this checkpoint but absent from disk: {missing}"
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

    for name in sorted(set(modules) & set(expected)):
        declared = expected[name]["external"]
        for dependency in sorted(modules[name]["external"] - declared):
            errors.append(
                "UNDECLARED EXTERNAL DEPENDENCY\n"
                f"  module: {name}\n"
                f"  dependency: {dependency}\n"
                f"  expected explicit external dependencies: {sorted(declared)}\n"
                "  action: verify necessity; if unnecessary, remove through MPS "
                "model-aware tooling; if genuinely required, amend the controlled "
                "blueprint before acceptance"
            )
        for dependency in sorted(declared - modules[name]["external"]):
            errors.append(
                f"{name}: blueprint declares external dependency {dependency} but the "
                f"module descriptor does not carry it"
            )

    cycle = find_cycle(combined)
    if cycle:
        errors.append(f"module dependency cycle: {' -> '.join(cycle)}")

    counts, node_counts = concept_counts()
    missing_aspects = sorted(set(expected) & set(modules) - set(counts))
    if missing_aspects:
        errors.append(f"languages without a structure aspect: {missing_aspects}")

    total_concepts = sum(counts.values())
    total_nodes = sum(node_counts.values())
    if max_concepts is not None and total_concepts > max_concepts:
        errors.append(
            f"structure aspects declare {total_concepts} concepts, but this checkpoint "
            f"permits at most {max_concepts}"
        )

    summary = {
        "modules": modules,
        "concepts": counts,
        "total_concepts": total_concepts,
        "total_nodes": total_nodes,
        "acyclic": not cycle,
        "checkpoint": checkpoint,
        "expected_concepts": max_concepts,
        "deferred_languages": deferred,
    }
    return errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkpoint",
        default=None,
        help=(
            "derive the expected language set and concept ceiling from the blueprint "
            "for this checkpoint, e.g. MPS-1; preferred over --max-concepts"
        ),
    )
    parser.add_argument(
        "--max-concepts",
        type=int,
        default=None,
        help=(
            "diagnostic/test override: fail if structure aspects declare more concepts "
            "than this; --checkpoint derives the same number from the blueprint"
        ),
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help=(
            "print the checkpoint to inventory to ceiling derivation and exit, without "
            "asserting that the languages are present on disk; with --checkpoint it "
            "explains one checkpoint, otherwise every checkpoint the blueprint declares"
        ),
    )
    args = parser.parse_args()
    if args.explain:
        if args.max_concepts is not None:
            print(
                "ERROR: --explain derives the ceiling; --max-concepts would replace it",
                file=sys.stderr,
            )
            return 2
        return explain(args.checkpoint)
    if args.checkpoint is not None and args.max_concepts is not None:
        # Preferring one silently would hide which number the run actually enforced.
        print(
            "ERROR: --checkpoint and --max-concepts are mutually exclusive; the "
            "checkpoint derives the ceiling from the blueprint, the override replaces it",
            file=sys.stderr,
        )
        return 2
    errors, summary = check(args.max_concepts, args.checkpoint)
    if errors:
        print("ERROR: MPS module graph gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if summary.get("checkpoint"):
        print(f"checkpoint: {summary['checkpoint']}")
        print(f"expected concepts: {summary['expected_concepts']}")
        print(f"observed concepts: {summary['total_concepts']}")
        print(f"structure nodes: {summary['total_nodes']}")
        if summary["deferred_languages"]:
            print(
                f"declared for a later checkpoint, expected absent: "
                f"{', '.join(summary['deferred_languages'])}"
            )
    print(
        f"PASS: {len(summary['modules'])} language modules match the blueprint dependency "
        f"graph; acyclic; {summary['total_concepts']} concepts declared across "
        f"{summary['total_nodes']} structure nodes"
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
