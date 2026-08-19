#!/usr/bin/env python3
"""Add required clinical-adapter allocations and verify allocation depth."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "overleaf" / "NL_TPS_Component_Realization.tex"
ROW_ID = re.compile(r"^(?:\\mbox\{)?([A-Z]{3}-\d{3}-\d{2})(?:\})?$")
SUMMARY_ID = re.compile(r"^(C-[A-Z0-9-]+-\d{2})$")


def split_row(line: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<!\\)&", line)]


def add_component(field: str, component: str) -> str:
    existing = set(re.findall(r"C-[A-Z0-9-]+-\d{2}", field))
    if component in existing:
        return field
    return field.rstrip() + "; " + component


def required_components(requirement_id: str, statement: str) -> list[str]:
    text = statement.lower()
    domain = requirement_id.split("-")[0]
    required: list[str] = []
    if domain == "CLN":
        if requirement_id.startswith("CLN-002-") or re.search(r"registration|registered|transform|deformable|rigid|accumulat", text):
            required.append("C-REG-01")
        if re.search(r"contour|structure|anatom|segment|target|organ.at.risk|oar", text):
            required.append("C-SEG-01")
    if domain == "PLN":
        required.append("C-PLAN-01")
        if re.search(r"dose|calculat|optimi|beam|objective|constraint|candidate|robust|deliver|machine|technique|fluence|spot", text):
            required.append("C-DOSE-01")
        if re.search(r"proton|range|rbe|let|interplay", text):
            required.append("C-PBT-01")
        if re.search(r"intent|prescription|objective|constraint|priority|unit|laterality", text):
            required.append("C-INTENT-01")
    if domain in {"DAT", "VAL", "GOV"} and re.search(
        r"interface|contract|schema|dicom|conformance|compatib|architecture|boundary", text
    ):
        required.append("C-ARCH-01")
    return required


def transform(source_text: str) -> tuple[str, Counter[str]]:
    lines = source_text.splitlines()
    transformed: list[str] = []
    counts: Counter[str] = Counter()
    requirement_rows: list[tuple[str, str, str]] = []

    for line in lines:
        parts = split_row(line)
        if len(parts) == 4:
            match = ROW_ID.fullmatch(parts[0])
            if match:
                requirement_id = match.group(1)
                statement = parts[1]
                allocation = parts[2]
                for component in required_components(requirement_id, statement):
                    allocation = add_component(allocation, component)
                parts[2] = allocation
                line = " & ".join(parts)
                requirement_rows.append((requirement_id, statement, allocation))
        transformed.append(line)

    for _, _, allocation in requirement_rows:
        for component in set(re.findall(r"C-[A-Z0-9-]+-\d{2}", allocation)):
            counts[component] += 1

    output: list[str] = []
    for line in transformed:
        parts = split_row(line)
        if len(parts) == 3:
            component_id = parts[0]
            if SUMMARY_ID.fullmatch(component_id) and re.fullmatch(r"\d+\s*\\\\", parts[2]):
                suffix = " \\\\"
                parts[2] = f"{counts[component_id]}{suffix}"
                line = " & ".join(parts)
        output.append(line)
    return "\n".join(output) + "\n", counts


def validate_counts(counts: Counter[str]) -> None:
    minimums = {
        "C-DOSE-01": 12,
        "C-SEG-01": 9,
        "C-REG-01": 6,
        "C-PBT-01": 4,
        "C-INTENT-01": 15,
        "C-ARCH-01": 1,
    }
    failures = {
        component: (counts[component], minimum)
        for component, minimum in minimums.items()
        if counts[component] < minimum
    }
    if failures:
        raise ValueError(f"clinical-adapter allocation minimums not met: {failures}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    original = SOURCE.read_text(encoding="utf-8")
    rendered, counts = transform(original)
    validate_counts(counts)
    if args.check:
        if rendered != original:
            print("ERROR: clinical-adapter allocation document is stale", file=sys.stderr)
            return 1
        print(
            "PASS: clinical adapter allocations - "
            + ", ".join(f"{name}={counts[name]}" for name in sorted(counts) if name in {
                "C-DOSE-01", "C-SEG-01", "C-REG-01", "C-PBT-01", "C-INTENT-01", "C-ARCH-01"
            })
        )
        return 0
    SOURCE.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"UPDATED: {SOURCE}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
