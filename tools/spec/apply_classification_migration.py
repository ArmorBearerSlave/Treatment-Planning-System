#!/usr/bin/env python3
"""Apply or check the F/SA/O classification display migration.

Legacy HNFR, NFSR, NFC, and F/NF/O identifiers are deliberately preserved.
Only the authoritative class label and backlog terminology change.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
FILES = [
    REPO_ROOT / "overleaf" / "NL_TPS_High_Level_Functional_Non_Functional_Operational_Requirements.tex",
    REPO_ROOT / "overleaf" / "NL_TPS_Functional_Non_Functional_Operational_Sub_Requirements.tex",
    REPO_ROOT / "overleaf" / "NL_TPS_Functional_Non_Functional_Operational_Component_Realization.tex",
]
ARCH_TEX = REPO_ROOT / "overleaf" / "NL_TPS_Engineering_Architecture_and_MVP_Implementation_Plan.tex"
ARCH_YAML = REPO_ROOT / "spec" / "architecture.yaml"
QUALITY_YAML = REPO_ROOT / "spec" / "quality_attributes.yaml"


def migrate_category_document(text: str) -> str:
    return (
        text.replace("F/NF/O", "F/SA/O")
        .replace("Non-Functional", "Safety-Assurance")
        .replace("Non-functional", "Safety / assurance")
        .replace("non-functional", "safety and assurance")
    )


def migrate_architecture_text(text: str) -> str:
    anchor = (
        "The F/SA/O requirement view is proposed as the primary planning and backlog classification."
    )
    for prior_label in ("F/NF/O", "F/SA/O"):
        prior = (
            anchor
            + f" The historical {prior_label} label and HNFR, NFSR, and NFC identifiers remain stable trace aliases; "
            + "the 25 former non-functional records are classified as cross-cutting safety and assurance constraints."
        )
        text = text.replace(prior, anchor)
    migrated = text.replace("F/NF/O", "F/SA/O")
    replacement = (
        anchor
        + " Legacy HNFR, NFSR, and NFC identifiers remain stable trace aliases; "
        + "the 25 former non-functional records are classified as cross-cutting safety and assurance constraints."
    )
    if anchor in migrated and replacement not in migrated:
        migrated = migrated.replace(anchor, replacement, 1)
    return migrated


def validate_quality_spec() -> None:
    document = yaml.safe_load(QUALITY_YAML.read_text(encoding="utf-8"))
    classification = document["classification"]
    count = sum(len(values) for values in classification["canonical_hlr_sets"].values())
    if count != classification["canonical_count"] or count != 25:
        raise ValueError(f"quality classification count is {count}, expected 25")
    if classification["authoritative_label"] != "cross_cutting_safety_and_assurance_constraint":
        raise ValueError("quality classification label is not authoritative")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    validate_quality_spec()
    stale: list[str] = []
    for path in FILES:
        original = path.read_text(encoding="utf-8")
        rendered = migrate_category_document(original)
        if args.check:
            if original != rendered:
                stale.append(str(path.relative_to(REPO_ROOT)))
        else:
            path.write_text(rendered, encoding="utf-8", newline="\n")

    original_arch = ARCH_TEX.read_text(encoding="utf-8")
    rendered_arch = migrate_architecture_text(original_arch)
    if args.check:
        if original_arch != rendered_arch:
            stale.append(str(ARCH_TEX.relative_to(REPO_ROOT)))
    else:
        ARCH_TEX.write_text(rendered_arch, encoding="utf-8", newline="\n")

    original_yaml = ARCH_YAML.read_text(encoding="utf-8")
    rendered_yaml = original_yaml.replace("F/NF/O", "F/SA/O")
    if args.check:
        if original_yaml != rendered_yaml:
            stale.append(str(ARCH_YAML.relative_to(REPO_ROOT)))
    else:
        ARCH_YAML.write_text(rendered_yaml, encoding="utf-8", newline="\n")

    if stale:
        print(f"ERROR: classification migration is stale: {stale}", file=sys.stderr)
        return 1
    print("PASS: 25 records classified as cross-cutting safety and assurance constraints")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
