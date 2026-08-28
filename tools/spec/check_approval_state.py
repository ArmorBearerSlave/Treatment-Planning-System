#!/usr/bin/env python3
"""Enforce machine-unambiguous architecture and ADR approval state by stage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
# Every controlled decision record. ADR-003 (ARCH-DGX-01) joined at the computational
# hosting amendment; the per-record checks below have always been generic, and only this
# completeness assertion had to learn about it.
REGISTERED_DECISIONS = {"ADR-001", "ADR-002", "ADR-003"}


def approval_authorities(records: list[dict[str, Any]]) -> set[str]:
    return {
        str(record.get("authority", "")).strip()
        for record in records
        if isinstance(record, dict) and record.get("authority")
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("A", "B", "C", "D", "release"), default="A")
    args = parser.parse_args()
    architecture = yaml.safe_load((REPO_ROOT / "spec" / "architecture.yaml").read_text(encoding="utf-8"))
    decisions = yaml.safe_load((REPO_ROOT / "spec" / "decisions.yaml").read_text(encoding="utf-8"))
    terminology = yaml.safe_load((REPO_ROOT / "spec" / "terminology.yaml").read_text(encoding="utf-8"))
    errors: list[str] = []

    baseline = architecture["baseline"]
    architecture_approvals = architecture["recorded_approvals"]
    decision_records = {record["id"]: record for record in decisions["decisions"]}
    if set(decision_records) != REGISTERED_DECISIONS:
        errors.append(
            f"decision register must contain exactly {sorted(REGISTERED_DECISIONS)}"
        )

    approval_objects = [
        ("ENG-PKG-01", baseline["approval_state"], architecture_approvals),
        *[
            (decision_id, record["approval_state"], record["recorded_approvals"])
            for decision_id, record in sorted(decision_records.items())
        ],
    ]
    if terminology["approval_state"] != decision_records["ADR-002"]["approval_state"]:
        errors.append("terminology approval state differs from ADR-002")

    if args.stage in {"A", "B"}:
        for identifier, state, approvals in approval_objects:
            if state != "pending_named_approval":
                errors.append(f"{identifier} is {state}; Stage {args.stage} expects pending_named_approval")
            if approvals:
                errors.append(f"{identifier} has approvals but remains pending")
        expected_stage = "A_mirror" if args.stage == "A" else "B_equivalence"
        current_stage = architecture["mps_authority_transition"]["current_stage"]
        if current_stage != expected_stage:
            errors.append(f"current MPS stage is {current_stage}, expected {expected_stage}")
    else:
        for identifier, state, approvals in approval_objects:
            if state != "approved":
                errors.append(f"{identifier} approval_state is {state}, not approved")
            if not approvals:
                errors.append(f"{identifier} has no recorded approvals")
        required = set(baseline["required_approval_domains"])
        recorded = approval_authorities(architecture_approvals)
        missing = sorted(required - recorded)
        if missing:
            errors.append(f"ENG-PKG-01 lacks required approval domains: {missing}")
        adr001 = decision_records["ADR-001"]
        if adr001.get("authority_cutover_status") != "approved":
            errors.append("ADR-001 authority_cutover_status is not approved")
        adr_required = set(adr001["stage_c_approval_required_from"])
        adr_recorded = approval_authorities(adr001["recorded_approvals"])
        adr_missing = sorted(adr_required - adr_recorded)
        if adr_missing:
            errors.append(f"ADR-001 lacks Stage C approval domains: {adr_missing}")

    if errors:
        print(f"ERROR: approval-state gate failed for stage {args.stage}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    named = ", ".join(identifier for identifier, _, _ in approval_objects)
    state = "pending with zero recorded approvals" if args.stage in {"A", "B"} else "approved"
    print(f"PASS: Stage {args.stage} approval state is explicit; {named} are {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
