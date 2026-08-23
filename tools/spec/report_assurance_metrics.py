#!/usr/bin/env python3
"""Derive the Stage A assurance metrics from their entity populations, and refuse assertions.

MPS-MAT-009. Every headline number this programme reported was, at some point, a number that
had been true once and was afterwards carried forward: 15 of 16 acceptance items survived
four checkpoints while an obligation its own freeze called mandatory was absent, and the
enumeration gate cited a population that does not exist in a clone. A metric preserved
because it was previously reported is an assertion wearing a measurement's clothes.

So each figure here is computed from the population it describes, on every run:

    acceptance items      from acceptance-item state in the materialization checklist
    evidence obligations  from the evidence reconciler's derived obligation states
    V&V / construction     from the trace graph's own entity records

and any figure ASSERTED elsewhere in the controlled record is compared against the derived
one. Disagreement is non-passing. That check is the point: an aggregate that cannot be
reconciled with its own population has stopped describing it.

Only DISCHARGED counts toward the obligation numerator. ATTESTED and OBSERVED are real states
and neither closes anything -- an authority may acknowledge an obligation without
establishing it, and an artifact may be correctly bound and still show it unmet.
"""
from __future__ import annotations

import argparse
import io
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "spec"))

CHECKLIST = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"
RELOCATION = REPO_ROOT / "spec" / "relocation_verification.yaml"


def load(path: Path):
    with io.open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle.read())


def acceptance_items() -> tuple[int, int, dict]:
    plan = load(CHECKLIST)
    items = plan["acceptance_items"]
    counts = Counter(item["status"] for item in items)
    return counts.get("complete", 0), len(items), dict(counts)


def evidence_obligations() -> tuple[int, int, dict]:
    import check_evidence_reconciliation as reconciler

    derived = reconciler.states()
    counts = Counter(state for state, _ in derived.values())
    return counts.get(reconciler.DISCHARGED, 0), len(derived), dict(counts)


def construction_population() -> tuple[int, int, int]:
    """Source-explicit hazard sets, total entities, and V&V claims, from the trace graph."""
    import build_trace_graph

    document = build_trace_graph.materialize()
    records = document["records"]
    explicit = sum(1 for record in records
                   if record["hazard_specificity"] == "source_explicit")
    # Counted from the records that carry a claim id, not read from the document's own
    # vv_claim_count field. The point of this tool is that an aggregate must be recomputed
    # from its population; taking the producer's own total would make this a comparison of a
    # number with itself, which is the defect being repaired one level up.
    claims = sum(1 for record in records if record.get("vv_claim_id"))
    declared_total = document.get("vv_claim_count")
    if declared_total is not None and declared_total != claims:
        raise SystemExit(
            f"MEASUREMENT INVALID: the trace graph declares vv_claim_count={declared_total} "
            f"but {claims} records carry a vv_claim_id. Refusing to report either number.")
    return explicit, len(records), claims


def asserted_aggregates() -> dict[str, int]:
    """Numbers asserted in the controlled record that must agree with their populations."""
    if not RELOCATION.is_file():
        return {}
    body = load(RELOCATION) or {}
    results = (body.get("results") or {})
    return {
        "records": results.get("records"),
        "vv_claims": results.get("vv_claims"),
        "source_explicit_hazard_sets": results.get("source_explicit_hazard_sets"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="fail when an asserted aggregate disagrees with its population")
    args = parser.parse_args()

    complete, total_items, item_states = acceptance_items()
    discharged, total_obligations, obligation_states = evidence_obligations()
    explicit, entities, claims = construction_population()

    print(f"Acceptance items:      {complete} / {total_items}")
    print(f"Evidence obligations:  {discharged} / {total_obligations}")
    print(f"V&V checks:            {explicit} / {entities:,}")
    print()
    print(f"  acceptance-item states: {dict(sorted(item_states.items()))}")
    print(f"  obligation states:      {dict(sorted(obligation_states.items()))}")
    print(f"  V&V claims in graph:    {claims:,}")
    print()
    print("  Only DISCHARGED counts toward the obligation numerator. ATTESTED and OBSERVED "
          "are\n  real states and neither closes anything.")

    problems: list[str] = []
    asserted = asserted_aggregates()
    for name, value, derived in (
            ("records", asserted.get("records"), entities),
            ("vv_claims", asserted.get("vv_claims"), claims),
            ("source_explicit_hazard_sets",
             asserted.get("source_explicit_hazard_sets"), explicit),
    ):
        if value is None:
            continue
        if value != derived:
            problems.append(
                f"spec/relocation_verification.yaml asserts {name} = {value}, but the entity "
                f"population derives {derived}. An aggregate that disagrees with its own "
                f"population has stopped describing it.")

    if problems:
        print("\nFAIL: asserted aggregates disagree with their populations", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    if args.check and asserted:
        print(f"\nPASS: {len(asserted)} asserted aggregates agree with their derived "
              f"populations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
