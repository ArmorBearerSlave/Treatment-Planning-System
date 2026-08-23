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


class MeasurementInvalid(Exception):
    """A required population could not be derived. Not a statement about the metrics.

    MI-EXIT-01. The vv_claim_count branch below already SAID measurement invalid and
    nevertheless exited 1, because `raise SystemExit("text")` prints the text and exits 1 --
    Python reserves the integer form for the status. This tool validates the headline
    assurance aggregates, so that collapse was the costly one: "the asserted assurance state
    disagrees with its population" and "I could not read the population" reached the process
    boundary as the same number, and only the first is a finding about the record.
    """


def load(path: Path):
    if not path.is_file():
        raise MeasurementInvalid(f"{path} is missing")
    try:
        with io.open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle.read())
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise MeasurementInvalid(f"{path} could not be read: {error}")


def acceptance_items(checklist: Path | None = None) -> tuple[int, int, dict]:
    plan = load(checklist or CHECKLIST)
    if not isinstance(plan, dict) or "acceptance_items" not in plan:
        raise MeasurementInvalid(
            f"{checklist or CHECKLIST} carries no acceptance_items, so the acceptance-item "
            f"population cannot be derived")
    items = plan["acceptance_items"]
    counts = Counter(item["status"] for item in items)
    return counts.get("complete", 0), len(items), dict(counts)


def evidence_obligations() -> tuple[int, int, dict]:
    import check_evidence_reconciliation as reconciler

    derived = reconciler.states()
    counts = Counter(state for state, _ in derived.values())
    return counts.get(reconciler.DISCHARGED, 0), len(derived), dict(counts)


def construction_population(document: dict | None = None) -> tuple[int, int, int]:
    """Source-explicit hazard sets, total entities, and V&V claims, from the trace graph.

    `document` is an internal injection seam for controls, not a command-line surface. The
    production CLI never accepts a substitute population: a tool that can be pointed at
    arbitrary inputs while printing output indistinguishable from the controlled assurance
    report is a provenance hazard, and that hazard is worse than the testing convenience.
    """
    if document is None:
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
        raise MeasurementInvalid(
            f"the trace graph declares vv_claim_count={declared_total} but {claims} records "
            f"carry a vv_claim_id. Refusing to report either number.")
    return explicit, len(records), claims


def asserted_aggregates(relocation: Path | None = None) -> dict[str, int]:
    """Numbers asserted in the controlled record that must agree with their populations."""
    path = relocation or RELOCATION
    if relocation is None and not path.is_file():
        return {}
    body = load(path) or {}
    results = (body.get("results") or {})
    return {
        "records": results.get("records"),
        "vv_claims": results.get("vv_claims"),
        "source_explicit_hazard_sets": results.get("source_explicit_hazard_sets"),
    }


def run_assurance_measurement(checklist_path: Path, relocation_path: Path,
                              check: bool = False, document: dict | None = None) -> int:
    """The whole measurement, once. Sources are parameters; the CLI supplies canonical ones.

    Separating this from main() is what lets a control drive the measurement-invalid and
    substantive-finding branches with scratch fixtures at the process boundary, WITHOUT the
    production command growing switches that accept arbitrary sources. The earlier round did
    the opposite and created two provenance defects: a production invocation could print
    "Acceptance items: 16 / 16" and "PASS" over substitute inputs, indistinguishable from the
    controlled assurance report, and the reconciled assertions were attributed to the
    controlled file when they had come from somewhere else.
    """
    try:
        complete, total_items, item_states = acceptance_items(checklist_path)
        discharged, total_obligations, obligation_states = evidence_obligations()
        explicit, entities, claims = construction_population(document)
        asserted = asserted_aggregates(relocation_path)
    except MeasurementInvalid as error:
        print(f"MEASUREMENT INVALID: {error}. No assurance metrics are reported and no "
              f"statement is made about whether the asserted assurance state is correct; "
              f"the instrument lacked the evidence required to decide.", file=sys.stderr)
        return 2

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

    if check and asserted:
        print(f"\nPASS: {len(asserted)} asserted aggregates agree with their derived "
              f"populations")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="fail when an asserted aggregate disagrees with its population")
    args = parser.parse_args()
    # The canonical controlled sources, always. There is deliberately no way to substitute
    # them from the command line: a production invocation must never be able to print a
    # report shaped exactly like the controlled assurance report over inputs that are not the
    # controlled ones.
    return run_assurance_measurement(CHECKLIST, RELOCATION, args.check)


if __name__ == "__main__":
    sys.exit(main())
