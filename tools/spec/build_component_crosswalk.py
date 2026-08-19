#!/usr/bin/env python3
"""Build or check the component view crosswalk.

The core, interface, and category component views overlap heavily. Constructing all
of them without reconciliation means specifying the same responsibility two or three
times under different identifiers.

This tool derives the overlap and proposes a relation from observable evidence. It
does not decide the reconciliation. D-ENG-004 is an accountable engineering decision;
every entry stays `pending_review` until a named reviewer records one, and the
construction gate refuses to approve a component whose entry is still pending.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = REPO_ROOT / "mps" / "import" / "traceability.json"
DEFAULT_OUTPUT = REPO_ROOT / "spec" / "component_crosswalk.yaml"

VIEW_PREFIXES = {
    "CORE-COMP": re.compile(r"^C-"),
    "IF-COMP": re.compile(r"^IC-"),
    "CAT-COMP": re.compile(r"^(?:FC|NFC|OC)-"),
}

# Evidence tiers, strongest first. The proposal follows the evidence; the decision
# does not follow the proposal.
PROPOSAL_RULES = (
    ("responsibility_identical", "SAME_AS"),
    ("name_identical", "REFINES"),
    ("stem_only", "UNRESOLVED"),
)


def stem_for(entity_id: str, entity_type: str) -> str:
    return VIEW_PREFIXES[entity_type].sub("", entity_id)


def load_components() -> list[dict[str, Any]]:
    document = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
    return [
        record
        for record in document["records"]
        if record["entity_type"] in VIEW_PREFIXES
    ]


def build() -> dict[str, Any]:
    components = load_components()
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in components:
        stem = stem_for(record["id"], record["entity_type"])
        groups.setdefault(stem, []).append(record)

    entries: list[dict[str, Any]] = []
    for stem in sorted(groups):
        members = sorted(groups[stem], key=lambda item: item["id"])
        if len(members) < 2:
            continue

        names = {member["name"] for member in members}
        responsibilities = {member["statement_plain"] for member in members}
        if len(responsibilities) == 1:
            evidence = "responsibility_identical"
        elif len(names) == 1:
            evidence = "name_identical"
        else:
            evidence = "stem_only"
        proposed = dict(PROPOSAL_RULES)[evidence]

        entries.append(
            {
                "stem": stem,
                "views": sorted({member["entity_type"] for member in members}),
                "members": [
                    {
                        "id": member["id"],
                        "view": member["entity_type"],
                        "name": member["name"],
                        "lead_team": member["lead_team"],
                        "responsibility_sha256": member["statement_sha256"],
                    }
                    for member in members
                ],
                "evidence": evidence,
                "proposed_relation": proposed,
                "status": "pending_review",
                "decided_relation": None,
                "reviewer": None,
                "rationale": None,
            }
        )

    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["evidence"]] = counts.get(entry["evidence"], 0) + 1

    return {
        "schema_version": "0.1",
        "register_id": "CWX-001",
        "title": "Component view crosswalk",
        "status": "derived_evidence_pending_accountable_decision",
        "decision": "D-ENG-004",
        "source": "mps/import/traceability.json",
        "authority": (
            "This file records observable overlap and a proposal derived from it. "
            "It confers no authority to supersede a view and decides nothing."
        ),
        "vocabulary_status": (
            "SAME_AS, REFINES, and DISTINCT are proposed additions to the ADR-001 "
            "TraceLink relation vocabulary and require that decision to be amended "
            "before any entry is treated as a controlled relation."
        ),
        "relation_meanings": {
            "SAME_AS": "One responsibility recorded in more than one view; specify once.",
            "REFINES": "A view-scoped narrowing of a shared responsibility; specify the parent once.",
            "DISTINCT": "Genuinely separate responsibilities that happen to share a stem.",
            "UNRESOLVED": "Evidence is insufficient to propose; a reviewer must classify.",
        },
        "overlap_group_count": len(entries),
        "evidence_counts": dict(sorted(counts.items())),
        "entries": entries,
    }


def serialize(document: dict[str, Any]) -> bytes:
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=False, width=100).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    document = build()
    rendered = serialize(document)

    if args.check:
        if not args.output.exists():
            print(f"ERROR: component crosswalk missing: {args.output}", file=sys.stderr)
            return 1
        existing = yaml.safe_load(args.output.read_text(encoding="utf-8"))
        fresh = yaml.safe_load(rendered.decode("utf-8"))

        # Reviewer decisions are recorded in the file and must survive regeneration,
        # so drift is checked on the derived evidence rather than on the whole file.
        def evidence_view(source: dict[str, Any]) -> Any:
            return [
                {
                    "stem": entry["stem"],
                    "members": entry["members"],
                    "evidence": entry["evidence"],
                    "proposed_relation": entry["proposed_relation"],
                }
                for entry in source["entries"]
            ]

        if evidence_view(existing) != evidence_view(fresh):
            print(
                "ERROR: component crosswalk evidence drift; regenerate and re-review",
                file=sys.stderr,
            )
            return 1

        decided = sum(1 for entry in existing["entries"] if entry["status"] == "decided")
        pending = len(existing["entries"]) - decided
        print(
            f"PASS: {len(existing['entries'])} component overlap groups; "
            f"{decided} decided, {pending} pending accountable review"
        )
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(rendered)
    print(
        f"WROTE: {args.output} with {document['overlap_group_count']} overlap groups "
        f"({document['evidence_counts']})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
