#!/usr/bin/env python3
"""Detect a synchronized or whitespace-bearing GCPL / NL-TPS workspace path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def location_findings(path: Path) -> list[str]:
    rendered = str(path.resolve())
    findings: list[str] = []
    if "onedrive" in rendered.casefold():
        findings.append("path is inside OneDrive")
    if any(character.isspace() for character in rendered):
        findings.append("path contains whitespace")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="return nonzero when the current repository path is unsuitable",
    )
    args = parser.parse_args()
    findings = location_findings(REPO_ROOT)
    if not findings:
        print(f"PASS: workspace path is local and space-free: {REPO_ROOT}")
        return 0
    level = "ERROR" if args.enforce else "WARNING"
    print(f"{level}: workspace location risk: {', '.join(findings)}", file=sys.stderr)
    print(
        "Use scripts/create_mps_worktree.ps1 after the worktree is clean; "
        "the checker does not move or delete data.",
        file=sys.stderr,
    )
    return 1 if args.enforce else 0


if __name__ == "__main__":
    raise SystemExit(main())
