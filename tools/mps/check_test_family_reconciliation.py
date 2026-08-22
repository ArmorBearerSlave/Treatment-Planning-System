"""Reconcile the declared test-family population with the operational one.

Two populations exist. initial_test_families in mps/bootstrap/language-skeleton.json was
declared at MPS-0 and states what the project intended to test. The operational ledger in
mps/materialization/stage-a-checklist.yaml was enumerated at closure from the mechanisms MPS
actually provides. They are different objects with different bases, and the danger is not
that they differ -- it is that a family could pass from one to the other by silence, so that
something declared at MPS-0 simply stops being mentioned and nobody notices it left.

So every blueprint family must carry exactly one explicit disposition, and every operational
family absent from the blueprint must declare itself newly introduced with a basis. Nothing
crosses by omission in either direction.

undecided is a first-class disposition on purpose. Forcing a disposition would invite
inferring one, and three of these need an engineering decision rather than an implementer's
guess -- notably ARCH-INVARIANT-001-no-language-equivalence, where dropping an architectural
invariant from a test taxonomy may be perfectly correct but dropping it from controlled
scope is not. An undecided entry passes structurally and is reported by name every run, so
the absence stays visible instead of being resolved by relabelling.

This gate compares two artifacts against each other, which is ordinarily the shape that
verifies neither. It is legitimate here only because the object under control IS the
correspondence between them: the question is not whether either population is right, but
whether anything has silently left one without being accounted for in the other.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"
PLAN = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"

DISPOSITIONS = {"carried", "renamed", "retired", "undecided"}
NEEDS_LEDGER = {"carried", "renamed"}


def _find(node, key):
    if isinstance(node, dict):
        if key in node:
            return node[key]
        for value in node.values():
            found = _find(value, key)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find(value, key)
            if found is not None:
                return found
    return None


def load():
    import yaml

    with io.open(BLUEPRINT, encoding="utf-8") as handle:
        blueprint = json.load(handle).get("initial_test_families") or []
    with io.open(PLAN, encoding="utf-8") as handle:
        plan = yaml.safe_load(handle.read())
    ledger = _find(plan, "test_family_status")
    reconciliation = _find(plan, "test_family_reconciliation")
    return blueprint, ledger, reconciliation


def main() -> int:
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter
                            ).parse_args()
    blueprint, ledger, reconciliation = load()
    problems = []

    if ledger is None:
        problems.append("no test_family_status ledger in the checklist")
    if reconciliation is None:
        problems.append("no test_family_reconciliation block in the checklist")
    if problems:
        print("FAIL: test-family reconciliation\n", file=sys.stderr)
        for problem in problems:
            print("  - " + problem, file=sys.stderr)
        return 1

    ledger_names = {entry["family"] for entry in ledger.get("families", [])}
    dispositions = reconciliation.get("dispositions") or []
    introduced = {entry["ledger"] for entry in reconciliation.get("newly_introduced") or []}

    seen = {}
    for entry in dispositions:
        name = entry.get("blueprint")
        if name in seen:
            problems.append("blueprint family " + str(name)
                            + " has more than one disposition")
        seen[name] = entry

    for name in blueprint:
        entry = seen.get(name)
        if entry is None:
            problems.append("blueprint family " + name + " has no disposition. It was "
                            "declared at MPS-0 and is unaccounted for at closure, which is "
                            "exactly the silence this gate exists to prevent.")
            continue
        disposition = entry.get("disposition")
        if disposition not in DISPOSITIONS:
            problems.append(name + " has unsupported disposition " + repr(disposition))
            continue
        if disposition in NEEDS_LEDGER:
            target = entry.get("ledger")
            if target not in ledger_names:
                problems.append(name + " is " + disposition + " to " + repr(target)
                                + ", which is not a family in the operational ledger")
        if disposition == "retired" and not str(entry.get("rationale", "")).strip():
            problems.append(name + " is retired with no rationale. Retiring a declared "
                            "family is a decision and must carry one.")
        if disposition == "undecided" and not str(entry.get("awaiting", "")).strip():
            problems.append(name + " is undecided with nothing recorded about what it "
                            "awaits, which makes it indistinguishable from an oversight")

    for extra in sorted(seen):
        if extra not in blueprint:
            problems.append("disposition names " + repr(extra)
                            + ", which is not in initial_test_families")

    accounted = {entry.get("ledger") for entry in dispositions
                 if entry.get("disposition") in NEEDS_LEDGER}
    for name in sorted(ledger_names):
        if name in accounted or name in introduced:
            continue
        problems.append("operational family " + name + " is neither a disposition target "
                        "nor declared newly introduced, so it appeared without a stated "
                        "basis")

    for entry in reconciliation.get("newly_introduced") or []:
        if entry.get("ledger") not in ledger_names:
            problems.append("newly introduced " + repr(entry.get("ledger"))
                            + " is not in the operational ledger")
        if not str(entry.get("basis", "")).strip():
            problems.append(str(entry.get("ledger")) + " is declared newly introduced with "
                            "no basis")

    if problems:
        print("FAIL: test-family reconciliation\n", file=sys.stderr)
        for problem in problems:
            print("  - " + problem + "\n", file=sys.stderr)
        return 1

    undecided = [name for name, entry in sorted(seen.items())
                 if entry.get("disposition") == "undecided"]
    print("PASS: all " + str(len(blueprint)) + " blueprint families carry exactly one "
          "disposition, and all " + str(len(ledger_names)) + " operational families are "
          "either a disposition target or declared newly introduced")
    if undecided:
        print("      OPEN: " + str(len(undecided)) + " awaiting an engineering decision, "
              "not resolved by this gate: " + ", ".join(undecided))
    return 0


if __name__ == "__main__":
    sys.exit(main())
