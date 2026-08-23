#!/usr/bin/env python3
"""Measure the authored model-test population from the MPS model, not from a test report.

MPS-MAT-009 F6(a): the currency record derived `authored`, `discovered` and `executed` from
one artifact, and two of them were literally the same variable. Three numbers that always
agree because they share a source are one number wearing three hats, and the gate's stated
purpose for them -- excluding "testmodules resolving to nothing", "a silently changing
discovery population" and "a failing test disappearing rather than failing" -- needs them to
be capable of disagreeing.

So `authored` is measured here, from the authored persistence, and `discovered` and
`executed` continue to come from the JUnit report. The two populations are then compared. If
a test is deleted from the report, authored and executed disagree and the gate fails. If a
test is deleted from the model, both move together and the declared expectation is what
catches it.

What counts as an authored test, in the jetbrains.mps.lang.test sense used by this project:

  NodeErrorCheckOperation   a named assertion attached to a fixture node; MPS emits one
                            JUnit test per operation, named test_<operation name> with a
                            generated suffix.
  SimpleNodeTest            a test method on the NodesTestCase; MPS emits one JUnit test
                            named test_<method name>().

The two shapes are counted separately because they fail differently: an assertion that stops
being emitted is a lost semantic control, while a lost test method is a lost harness witness,
and the MPS-MAT-008 controls turn on telling those apart.

This reads persistence. It does not author it.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mps_layout  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = (REPO_ROOT / "mps" / "NLTPSGovernance" / "tests" / "nltps.modeltests"
                 / "models" / "nltps.modeltests.headless@tests.mps")

ERROR_CHECK = "jetbrains.mps.lang.test.structure.NodeErrorCheckOperation"
NODE_TEST = "jetbrains.mps.lang.test.structure.SimpleNodeTest"
TEST_CASE = "jetbrains.mps.lang.test.structure.NodesTestCase"
NAME = "name"


class ModelReadError(Exception):
    """The population could not be measured. Not a statement about the population."""


def _walk(element: ElementTree.Element):
    for node in element.findall("node"):
        yield node
        yield from _walk(node)


def population(model_path: Path) -> dict:
    """Every authored test in one model, addressed by concept name rather than by index."""
    if not model_path.exists():
        raise ModelReadError(
            f"cannot measure the authored population: {model_path} does not exist. An "
            f"absent model must refuse rather than report zero, for the same reason a task "
            f"over zero discovered tests is not a pass.")

    concept_by_index: dict[str, str] = {}
    feature_by_index: dict[str, str] = {}
    nodes: list[ElementTree.Element] = []

    documents = mps_layout.documents(model_path)
    if not documents:
        raise ModelReadError(f"cannot measure the authored population: {model_path} "
                             f"resolved to zero documents")

    for document in documents:
        root = ElementTree.parse(document).getroot()
        # Registry entries are merged across documents: in a file-per-root model each root
        # file carries only the indices it uses, so an index absent from one document may be
        # defined in another.
        for concept in root.iter("concept"):
            index, name = concept.get("index"), concept.get("name")
            if index and name:
                concept_by_index[index] = name
            for kind in ("property", "child", "reference"):
                for feature in concept.findall(kind):
                    findex, fname = feature.get("index"), feature.get("name")
                    if findex and fname:
                        feature_by_index[findex] = fname
        nodes.extend(_walk(root))

    def concept_of(node: ElementTree.Element) -> str:
        index = node.get("concept", "")
        return concept_by_index.get(index, index)

    def name_of(node: ElementTree.Element) -> str | None:
        for element in node.findall("property"):
            if feature_by_index.get(element.get("role", "")) == NAME:
                return element.get("value")
        return None

    error_checks, node_tests, cases = [], [], []
    for node in nodes:
        concept = concept_of(node)
        if concept == ERROR_CHECK:
            error_checks.append(name_of(node) or f"<unnamed {node.get('id')}>")
        elif concept == NODE_TEST:
            node_tests.append(name_of(node) or f"<unnamed {node.get('id')}>")
        elif concept == TEST_CASE:
            cases.append(name_of(node) or f"<unnamed {node.get('id')}>")

    return {
        "model": str(model_path.relative_to(REPO_ROOT)).replace("\\", "/")
                 if model_path.is_relative_to(REPO_ROOT) else str(model_path),
        "test_cases": sorted(cases),
        "error_check_operations": sorted(error_checks),
        "node_test_methods": sorted(node_tests),
        "authored": len(error_checks) + len(node_tests),
    }


def matches_identity(authored_name: str, identity: str) -> bool:
    """Whether one JUnit identity corresponds to one authored name.

    MPS emits `test_<name>` for an error-check operation, with a generated numeric suffix,
    and `test_<name>()` for a test method. The suffix is why this is a prefix relation
    rather than equality -- and why the relation is stated here once instead of being
    re-derived, differently, by each caller that needs it.
    """
    stem = identity[len("test_"):] if identity.startswith("test_") else identity
    stem = stem[:-2] if stem.endswith("()") else stem
    return stem == authored_name or stem.startswith(authored_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--expect", type=int,
                        help="fail unless exactly this many authored tests are present")
    parser.add_argument("--json", action="store_true", help="emit the population as JSON")
    args = parser.parse_args()

    try:
        result = population(args.model)
    except (ModelReadError, ElementTree.ParseError) as error:
        # A measurement failure is reported as a measurement failure, never as a finding
        # about the population. Exit 2 is the convention the currency gate established.
        print(f"MEASUREMENT INVALID: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"authored model tests: {result['authored']} "
              f"({len(result['error_check_operations'])} error-check operations, "
              f"{len(result['node_test_methods'])} test methods) "
              f"across {len(result['test_cases'])} test cases")
        for name in result["error_check_operations"]:
            print(f"  assertion: {name}")
        for name in result["node_test_methods"]:
            print(f"  method:    {name}")

    if args.expect is not None and result["authored"] != args.expect:
        print(f"FAIL: expected {args.expect} authored tests, measured "
              f"{result['authored']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    with io.open(sys.stdout.fileno(), "w", encoding="utf-8", closefd=False) as _:
        pass
    sys.exit(main())
