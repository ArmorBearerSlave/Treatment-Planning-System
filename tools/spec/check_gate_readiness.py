#!/usr/bin/env python3
"""Check controlled risk-score and quantitative-target readiness by gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=int, choices=range(0, 6), default=0)
    args = parser.parse_args()
    scores = yaml.safe_load((REPO_ROOT / "spec" / "risk_scores.yaml").read_text(encoding="utf-8"))
    quality = yaml.safe_load((REPO_ROOT / "spec" / "quality_attributes.yaml").read_text(encoding="utf-8"))
    errors: list[str] = []
    if len(scores["scores"]) != 119:
        errors.append(f"risk score count is {len(scores['scores'])}, expected 119")
    classified = sum(len(items) for items in quality["classification"]["canonical_hlr_sets"].values())
    if classified != 25:
        errors.append(f"safety/assurance classification count is {classified}, expected 25")
    targets = quality["quantitative_quality_target_register"]["targets"]
    target_ids = [target["id"] for target in targets]
    if len(target_ids) != len(set(target_ids)):
        errors.append("duplicate quantitative target ID")

    if args.gate >= 1:
        unapproved_scores = [
            hlr_id
            for hlr_id, score in scores["scores"].items()
            if score["status"] != "approved"
            or any(score[field] is None for field in ("severity", "occurrence", "detectability", "rpn"))
        ]
        pending_targets = [
            target["id"]
            for target in targets
            if target["status"] != "approved" or target["value"] is None or target["unit"] is None
        ]
        if unapproved_scores:
            errors.append(f"{len(unapproved_scores)} HLR risk scores are not approved")
        if pending_targets:
            errors.append(f"{len(pending_targets)} quantitative targets are not approved")

    if errors:
        print(f"ERROR: Gate {args.gate} readiness failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: Gate {args.gate} structural readiness; 119 HLR score records, "
        f"25 reclassified constraints, {len(targets)} quantitative target records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
