#!/usr/bin/env python3
"""Validate constructed component, requirement, and sub-requirement records.

Construction adds engineering content to identifiers that already exist and are
hash-bound to the controlled documents. This gate enforces the parts of that which
are mechanically checkable:

  * every record conforms to its construction schema, with no unknown fields;
  * every identifier exists in the materialized trace graph;
  * the canonical statement a record claims to elaborate still hashes to its source;
  * a reviewed or approved record carries a reviewed, source-explicit hazard set;
  * a record whose blocking decision is open cannot reach approved state;
  * a component in an unresolved crosswalk group cannot reach approved state.

Passing proves internal consistency. It proves nothing about clinical correctness,
risk acceptability, or whether a V&V claim has been executed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mps.schema_subset import validate_json_schema  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]
CONSTRUCTION_DIR = REPO_ROOT / "spec" / "construction"
SCHEMA_DIR = REPO_ROOT / "spec" / "schemas"
TRACE_PATH = REPO_ROOT / "mps" / "import" / "traceability.json"
DECISIONS_PATH = REPO_ROOT / "spec" / "engineering_decisions.yaml"
CROSSWALK_PATH = REPO_ROOT / "spec" / "component_crosswalk.yaml"
POLICY_PATH = REPO_ROOT / "spec" / "construction_policy.yaml"

SECTIONS = {
    "components": ("component.schema.json", "component"),
    "requirements": ("requirement.schema.json", "requirement"),
    "subrequirements": ("subrequirement.schema.json", "subrequirement"),
}

APPROVAL_STATES = {"reviewed", "approved"}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def statement_hash_field(entity_class: str) -> str:
    if entity_class == "component":
        return "responsibility_sha256"
    return "canonical_statement_sha256"


def check() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts: dict[str, int] = {"component": 0, "requirement": 0, "subrequirement": 0}

    if not CONSTRUCTION_DIR.exists():
        return ([f"missing construction directory: {CONSTRUCTION_DIR}"], counts)

    trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
    trace_by_id = {record["id"]: record for record in trace["records"]}

    decisions = load_yaml(DECISIONS_PATH)
    open_decisions = {
        entry["id"]
        for entry in decisions["decisions"]
        if entry["status"] != "resolved"
    }

    crosswalk = load_yaml(CROSSWALK_PATH)
    unresolved_components = {
        member["id"]
        for entry in crosswalk["entries"]
        if entry["status"] != "decided"
        for member in entry["members"]
    }

    policy = load_yaml(POLICY_PATH) if POLICY_PATH.exists() else {}
    treatment_policy = policy.get("treatment_by_entity_type", {})

    schemas = {
        name: json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
        for name, (filename, _) in SECTIONS.items()
    }

    for path in sorted(CONSTRUCTION_DIR.glob("*.yaml")):
        document = load_yaml(path)
        for section, (_, entity_class) in SECTIONS.items():
            for record in document.get(section, []) or []:
                record_id = record.get("id", "<no id>")
                label = f"{path.name}:{record_id}"

                try:
                    validate_json_schema(record, schemas[section])
                except ValueError as exc:
                    for line in str(exc).splitlines()[1:]:
                        errors.append(f"{label}{line.lstrip('-')}")
                    continue

                counts[entity_class] += 1
                state = record["construction_state"]

                traced = trace_by_id.get(record_id)
                if traced is None:
                    errors.append(f"{label}: identifier is not in the materialized trace graph")
                    continue

                expected_hash = traced["statement_sha256"]
                actual_hash = record.get(statement_hash_field(entity_class))
                if actual_hash != expected_hash:
                    errors.append(
                        f"{label}: statement hash {actual_hash} does not match the source "
                        f"hash {expected_hash}; the record elaborates text that has changed"
                    )

                if record.get("vv_claim_id") and record["vv_claim_id"] != traced["vv_claim_id"]:
                    errors.append(
                        f"{label}: V&V claim {record['vv_claim_id']} does not match "
                        f"{traced['vv_claim_id']}"
                    )

                expected_treatment = treatment_policy.get(traced["entity_type"])
                actual_treatment = record.get("treatment")
                exception = record.get("treatment_exception")
                if expected_treatment and actual_treatment and actual_treatment != expected_treatment:
                    if exception is None:
                        errors.append(
                            f"{label}: treatment '{actual_treatment}' departs from the policy "
                            f"treatment '{expected_treatment}' for {traced['entity_type']} "
                            f"without a recorded exception"
                        )
                    elif exception.get("policy_treatment") != expected_treatment:
                        errors.append(
                            f"{label}: treatment exception cites policy treatment "
                            f"'{exception.get('policy_treatment')}' but the policy for "
                            f"{traced['entity_type']} is '{expected_treatment}'"
                        )
                elif exception is not None:
                    errors.append(
                        f"{label}: records a treatment exception but does not depart "
                        f"from the policy treatment '{expected_treatment}'"
                    )

                if state == "approved":
                    blocking = set(record.get("blocking_decisions", [])) & open_decisions
                    if blocking:
                        errors.append(
                            f"{label}: cannot be approved while {sorted(blocking)} remain open"
                        )
                    if entity_class == "component" and record_id in unresolved_components:
                        errors.append(
                            f"{label}: cannot be approved while its component crosswalk "
                            f"group is pending review (D-ENG-004)"
                        )

                if state in APPROVAL_STATES and record.get("hazard_basis") != "source_explicit":
                    errors.append(
                        f"{label}: state '{state}' requires a reviewed, source-explicit hazard set"
                    )

    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors, counts = check()
    if errors:
        print("ERROR: construction record gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    total = sum(counts.values())
    print(
        f"PASS: {total} construction records validate "
        f"({counts['component']} component, {counts['requirement']} requirement, "
        f"{counts['subrequirement']} sub-requirement); identifiers, statement hashes, "
        f"V&V claims, decision blocks, and crosswalk state reconcile"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
