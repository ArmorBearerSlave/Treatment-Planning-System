#!/usr/bin/env python3
"""Check that CLAUDE.md still describes the controls that exist.

CLAUDE.md is read first by every session and overrides default behaviour, which makes
it the one artifact whose staleness is actively harmful rather than merely unhelpful.
A session obeying a superseded copy does not simply lack guidance: it reconstructs the
controls a later amendment removed, and every other gate stays green while it does.

That happened. After the post-MPS-1 amendment replaced a hard-coded concept ceiling
with a blueprint-derived one and added a fifth checkpoint, CLAUDE.md still described
four checkpoints and instructed the reader to pass the removed flag. Nothing detected
it, because no gate read the file. It was caught by a person re-reading it at a
session boundary.

This gate closes that hole. It asserts only what is mechanically derivable -- the
checkpoints named, the closure claims, the commands prescribed, the design sources
cited, the deferral vocabulary used, and the absence of flags that were removed. It
cannot check whether the prose is good advice, and does not try.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROLS_PATH = REPO_ROOT / "CLAUDE.md"
PLAN_PATH = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"
PLAN_GATE_PATH = REPO_ROOT / "tools" / "mps" / "check_materialization_plan.py"

CHECKPOINT_LINE_RE = re.compile(r"^\s{2,}(MPS-\d)\s{2,}(\S.*?)\s*$")
COMMAND_RE = re.compile(r"^python (tools/[a-z]+/[a-z_]+\.py)(.*)$", re.MULTILINE)
BACKTICK_PATH_RE = re.compile(r"`((?:spec|mps|tools|scripts)/[A-Za-z0-9_./-]+)`")
EXPECTED_CHECKPOINTS_RE = re.compile(r"EXPECTED_CHECKPOINTS\s*=\s*\[([^\]]*)\]")

# Flags removed by the post-MPS-1 amendment. Presenting one as the canonical way to
# bound a checkpoint would send the next session back to a hard-coded ceiling.
RETIRED_INVOCATIONS = {
    "--max-concepts <checkpoint bound>": (
        "the ceiling is derived from the blueprint; use --checkpoint MPS-N. "
        "--max-concepts survives only as a diagnostic override"
    ),
}


def controls_checkpoints(text: str) -> dict[str, str]:
    """Return the checkpoint table CLAUDE.md presents, id -> trailing annotation."""
    found: dict[str, str] = {}
    for line in text.splitlines():
        match = CHECKPOINT_LINE_RE.match(line)
        if match:
            found[match.group(1)] = match.group(2)
    return found


def plan_checkpoints() -> list[str]:
    plan = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))
    return [entry["id"] for entry in plan["checkpoints"]]


def gate_checkpoints() -> list[str]:
    match = EXPECTED_CHECKPOINTS_RE.search(PLAN_GATE_PATH.read_text(encoding="utf-8"))
    if match is None:
        raise ValueError("EXPECTED_CHECKPOINTS not found in check_materialization_plan.py")
    return re.findall(r'"([^"]+)"', match.group(1))


def closed_checkpoints() -> set[str]:
    """A checkpoint is closed when every acceptance item it owns is complete."""
    plan = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))
    owned: dict[str, list[str]] = {}
    for item in plan["acceptance_items"]:
        owned.setdefault(item["checkpoint"], []).append(item["status"])
    return {
        checkpoint
        for checkpoint, statuses in owned.items()
        if statuses and all(status == "complete" for status in statuses)
    }


def deferral_classes() -> set[str]:
    """Deferral class names actually used in the controlled checklist."""
    found: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "deferral_class" and isinstance(value, str):
                    found.add(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8")))
    return found


def check() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    text = CONTROLS_PATH.read_text(encoding="utf-8")

    # 1. The checkpoint sequence must match both the plan and the gate that enforces it.
    described = controls_checkpoints(text)
    plan = plan_checkpoints()
    gate = gate_checkpoints()
    if plan != gate:
        errors.append(
            f"the checklist declares {plan} but check_materialization_plan.py expects {gate}"
        )
    if sorted(described) != sorted(plan):
        errors.append(
            f"CLAUDE.md describes checkpoints {sorted(described)}, but the controlled "
            f"checkpoints are {plan}"
        )

    # 2. A checkpoint annotated "closed" must actually have every item complete, and a
    #    genuinely closed one must not be presented as open work.
    closed = closed_checkpoints()
    for checkpoint, annotation in described.items():
        claims_closed = "closed" in annotation.lower()
        if claims_closed and checkpoint not in closed:
            errors.append(
                f"CLAUDE.md marks {checkpoint} closed, but not all of its acceptance "
                f"items are complete"
            )
        if not claims_closed and checkpoint in closed:
            errors.append(
                f"{checkpoint} has every acceptance item complete but CLAUDE.md does "
                f"not mark it closed"
            )

    # 3. Every command it tells the next session to run must exist.
    commands = 0
    for script, _ in COMMAND_RE.findall(text):
        commands += 1
        if not (REPO_ROOT / script).exists():
            errors.append(f"CLAUDE.md prescribes a command whose script is missing: {script}")

    # 4. Every controlled artifact it cites must exist.
    paths = 0
    for relative in sorted(set(BACKTICK_PATH_RE.findall(text))):
        paths += 1
        if not (REPO_ROOT / relative).exists():
            errors.append(f"CLAUDE.md cites a path that does not exist: {relative}")

    # 5. Deferral vocabulary must match what the checklist actually records, or the
    #    lapse asymmetry it explains is describing classes that are not in use.
    used = deferral_classes()
    for name in sorted(used):
        if name not in text:
            errors.append(
                f"the checklist records deferral class {name!r} but CLAUDE.md does not "
                f"explain it"
            )
    for name in re.findall(r"`(non_instantiability|semantic_model_absence)`", text):
        if name not in used:
            errors.append(
                f"CLAUDE.md explains deferral class {name!r}, which the checklist no "
                f"longer uses"
            )

    # 6. Retired invocations must not be presented as current.
    for retired, reason in RETIRED_INVOCATIONS.items():
        if retired in text:
            errors.append(f"CLAUDE.md still prescribes {retired!r}: {reason}")

    return errors, {
        "checkpoints": len(described),
        "commands": commands,
        "paths": paths,
        "deferral_classes": len(used),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors, counts = check()
    if errors:
        print("ERROR: session controls gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: CLAUDE.md matches the controlled state; {counts['checkpoints']} checkpoints "
        f"with closure claims verified, {counts['commands']} prescribed commands resolve, "
        f"{counts['paths']} cited paths exist, {counts['deferral_classes']} deferral classes "
        f"explained"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
