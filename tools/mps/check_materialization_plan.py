#!/usr/bin/env python3
"""Validate the Stage A MPS materialization plan and its checkpoint discipline.

The plan's value is the review boundary between checkpoints. This gate keeps that
boundary enforceable rather than aspirational:

  * every acceptance item belongs to exactly one checkpoint and is referenced by it;
  * only the final checkpoint may contain HLR roots, so the first live-MPS commit
    cannot carry the corpus import;
  * the workspace requirement matches the relocation decision;
  * the pinned toolchain build is recorded;
  * prohibitions on patient data, credentials, and signing keys stay false.

It checks the plan, not the MPS project. MPS creates its own persistence and no
text tool authors it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"
SKELETON_PATH = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"

EXPECTED_CHECKPOINTS = ["MPS-0", "MPS-1", "MPS-2", "MPS-3"]
PROHIBITED_FLAGS = (
    "patient_data_permitted",
    "clinical_credentials_permitted",
    "signing_keys_permitted",
)


def check() -> list[str]:
    errors: list[str] = []
    plan = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))

    for flag in PROHIBITED_FLAGS:
        if plan.get(flag) is not False:
            errors.append(f"{flag} must be false")

    workspace = plan.get("workspace", {})
    if workspace.get("kind") != "independent_clone":
        errors.append(
            "workspace kind must be independent_clone; a linked worktree leaves the "
            "Git common directory outside the relocated tree"
        )
    if workspace.get("synchronized_directory_permitted") is not False:
        errors.append("workspace must prohibit synchronized directories")
    if workspace.get("whitespace_in_path_permitted") is not False:
        errors.append("workspace must prohibit whitespace in the path")

    pinned = plan.get("pinned_toolchain", {})
    if not pinned.get("build"):
        errors.append("pinned_toolchain.build must record the exact MPS build")

    checkpoints = plan.get("checkpoints", [])
    ids = [entry["id"] for entry in checkpoints]
    if ids != EXPECTED_CHECKPOINTS:
        errors.append(f"checkpoints must be {EXPECTED_CHECKPOINTS} in order, found {ids}")

    for entry in checkpoints:
        if entry.get("commit_boundary") is not True:
            errors.append(f"{entry['id']} must be a commit boundary")

    carrying = [entry["id"] for entry in checkpoints if entry.get("contains_hlr_roots")]
    if carrying != [EXPECTED_CHECKPOINTS[-1]]:
        errors.append(
            f"only {EXPECTED_CHECKPOINTS[-1]} may contain HLR roots, found {carrying}; "
            "the first live-MPS commit shall not contain the 119 HLRs"
        )

    items = plan.get("acceptance_items", [])
    item_ids = {item["id"] for item in items}
    if len(item_ids) != len(items):
        errors.append("duplicate acceptance item identifier")

    referenced: dict[str, list[str]] = {}
    for entry in checkpoints:
        for item_id in entry.get("acceptance_items", []):
            referenced.setdefault(item_id, []).append(entry["id"])
            if item_id not in item_ids:
                errors.append(f"{entry['id']} references unknown acceptance item {item_id}")

    for item in items:
        item_id = item["id"]
        checkpoint = item.get("checkpoint")
        if checkpoint not in EXPECTED_CHECKPOINTS:
            errors.append(f"{item_id} declares unknown checkpoint {checkpoint!r}")
        elif checkpoint not in referenced.get(item_id, []):
            errors.append(
                f"{item_id} declares checkpoint {checkpoint} but that checkpoint does "
                f"not reference it"
            )
        if item_id not in referenced:
            errors.append(f"{item_id} is not referenced by any checkpoint")
        if item.get("status") not in {"pending", "complete", "blocked"}:
            errors.append(f"{item_id} has unsupported status {item.get('status')!r}")
        if item.get("status") == "complete" and not item.get("evidence"):
            errors.append(f"{item_id} is complete without attributable evidence")

    for path in plan.get("controlled_inputs", []):
        if not (REPO_ROOT / path).exists():
            errors.append(f"controlled input is missing: {path}")

    if not SKELETON_PATH.exists():
        errors.append("language skeleton blueprint is missing")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors = check()
    if errors:
        print("ERROR: MPS materialization plan gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    plan = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))
    complete = sum(1 for item in plan["acceptance_items"] if item["status"] == "complete")
    total = len(plan["acceptance_items"])
    print(
        f"PASS: {len(plan['checkpoints'])} checkpoints, {total} acceptance items, "
        f"{complete} complete; HLR import confined to {EXPECTED_CHECKPOINTS[-1]}; "
        f"pinned build {plan['pinned_toolchain']['build']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
