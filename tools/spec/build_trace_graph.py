#!/usr/bin/env python3
"""Build or check the materialized GCPL / NL-TPS hazard trace graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
OVERLEAF = REPO_ROOT / "overleaf"
POLICY_PATH = REPO_ROOT / "spec" / "allocations.yaml"
HAZARD_PATH = REPO_ROOT / "spec" / "hazards.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "mps" / "import" / "traceability.json"

ENTITY_SOURCES = {
    "HLR": ("NL_TPS_High_Level_Requirements.tex", re.compile(r"^[A-Z]{3}-\d{3}$")),
    "SUB": ("NL_TPS_Detailed_Requirements.tex", re.compile(r"^[A-Z]{3}-\d{3}-\d{2}$")),
    "HLIR": ("NL_TPS_High_Level_Interface_Requirements.tex", re.compile(r"^IF-[A-Z]{3}-\d{3}-\d{2}$")),
    "SIR": ("NL_TPS_Interface_Component_Realization.tex", re.compile(r"^SIR-[A-Z]{3}-\d{3}-\d{2}-\d{2}$")),
    "CORE-COMP": ("NL_TPS_Component_Realization.tex", re.compile(r"^C-[A-Z0-9-]+-\d{2}$")),
    "IF-COMP": ("NL_TPS_Interface_Component_Realization.tex", re.compile(r"^IC-[A-Z0-9-]+-\d{2}$")),
    "CAT-COMP": ("NL_TPS_Functional_Non_Functional_Operational_Component_Realization.tex", re.compile(r"^(?:FC|NFC|OC)-[A-Z0-9-]+-\d{2}$")),
    "MQA": ("NL_TPS_Monthly_QA_Integration_Profile.tex", re.compile(r"^MQA-(?:\d{3}(?:-\d{2})?|A\d{2})$")),
}

# Every component catalog uses one five-column layout:
#   id & layer & name & realization responsibility & lead team
# The responsibility is the normative content a component specification elaborates,
# so it is captured explicitly instead of whichever column happened to be longest.
COMPONENT_TYPES = ("CORE-COMP", "IF-COMP", "CAT-COMP")
COMPONENT_CATALOG_COLUMNS = 5
COMPONENT_RESPONSIBILITY_MIN_CHARS = 60

# MQA identifiers carry three distinct entity classes that the V&V matrix separates as
# VVC-MQA-R, VVC-MQA-S, and VVC-MQA-C. They are typed apart rather than pooled.
MQA_TYPES = ("MQA-REQ", "MQA-SUB", "MQA-COMP")
MQA_SUBASSEMBLY_COLUMNS = 4


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def split_latex_row(line: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<!\\)&", line)]


def normalize_id(value: str) -> str:
    match = re.fullmatch(r"\\mbox\{([^{}]+)\}", value.strip())
    return match.group(1) if match else value.strip()


def to_plain(value: str) -> str:
    result = value
    replacements = (
        (r"\slash\allowbreak{}", "/"),
        (r"\allowbreak{}", ""),
        (r"\&", "&"),
        (r"\ldots{}", "..."),
        ("--", "-"),
    )
    for old, new in replacements:
        result = result.replace(old, new)
    result = re.sub(r"\\(?:textbf|textit|texttt|mbox)\{([^{}]*)\}", r"\1", result)
    return " ".join(result.split())


def strip_row_terminator(value: str) -> str:
    return re.sub(r"\\\\\s*$", "", value).strip()


def mqa_type_for(entity_id: str) -> str:
    if re.fullmatch(r"MQA-\d{3}", entity_id):
        return "MQA-REQ"
    if re.fullmatch(r"MQA-\d{3}-\d{2}", entity_id):
        return "MQA-SUB"
    return "MQA-COMP"


def parse_entities() -> dict[str, dict[str, Any]]:
    entities: dict[str, dict[str, Any]] = {}
    for entity_type, (filename, id_pattern) in ENTITY_SOURCES.items():
        source = OVERLEAF / filename
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            parts = split_latex_row(line)
            if len(parts) < 2:
                continue
            entity_id = normalize_id(parts[0])
            if id_pattern.fullmatch(entity_id) is None:
                continue
            if entity_type == "HLR" and " shall " not in f" {parts[1].lower()} ":
                continue

            if entity_type in COMPONENT_TYPES:
                # Only the catalog row carries a responsibility; summary and allocation
                # rows for the same identifier are deliberately ignored.
                if len(parts) != COMPONENT_CATALOG_COLUMNS:
                    continue
                statement = parts[3]
                record = {
                    "id": entity_id,
                    "entity_type": entity_type,
                    "layer": to_plain(parts[1]),
                    "name": to_plain(parts[2]),
                    "lead_team": to_plain(strip_row_terminator(parts[4])),
                    "statement_latex": statement,
                    "statement_plain": to_plain(statement),
                    "source_file": f"overleaf/{filename}",
                    "source_line": line_number,
                    "columns": parts,
                }
                existing = entities.get(entity_id)
                if existing is not None:
                    if existing["statement_plain"] != record["statement_plain"]:
                        raise ValueError(
                            f"{entity_id} has conflicting catalog rows at "
                            f"{existing['source_file']}:{existing['source_line']} and "
                            f"{record['source_file']}:{line_number}"
                        )
                    continue
                entities[entity_id] = record
                continue

            resolved_type = mqa_type_for(entity_id) if entity_type == "MQA" else entity_type

            if resolved_type == "MQA-COMP":
                # Subassembly table: id & name & responsibility & allocated components
                if len(parts) != MQA_SUBASSEMBLY_COLUMNS:
                    continue
                statement = parts[2]
                entities[entity_id] = {
                    "id": entity_id,
                    "entity_type": resolved_type,
                    "name": to_plain(parts[1]),
                    "layer": "MQA package subassembly",
                    "lead_team": "",
                    "allocated_components": [
                        item.strip()
                        for item in to_plain(strip_row_terminator(parts[3])).split(";")
                        if item.strip()
                    ],
                    "statement_latex": statement,
                    "statement_plain": to_plain(statement),
                    "source_file": f"overleaf/{filename}",
                    "source_line": line_number,
                    "columns": parts,
                }
                continue

            statement = parts[1]
            existing = entities.get(entity_id)
            if existing and len(existing["statement_latex"]) >= len(statement):
                continue
            entities[entity_id] = {
                "id": entity_id,
                "entity_type": resolved_type,
                "statement_latex": statement,
                "statement_plain": to_plain(statement),
                "source_file": f"overleaf/{filename}",
                "source_line": line_number,
                "columns": parts,
            }
    validate_component_fields(entities)
    return entities


def validate_component_fields(entities: dict[str, dict[str, Any]]) -> None:
    """Reject component records that carry a label where a specification belongs."""
    errors: list[str] = []
    # Uniqueness is scoped within a view. Repetition across the core, interface, and
    # category views is a reconciliation question owned by spec/component_crosswalk.yaml,
    # not an import failure.
    responsibilities: dict[tuple[str, str], str] = {}
    names: dict[tuple[str, str], str] = {}
    for entity in entities.values():
        entity_type = entity["entity_type"]
        if entity_type not in COMPONENT_TYPES:
            continue
        entity_id = entity["id"]
        responsibility = entity["statement_plain"]
        name = entity["name"]
        if len(responsibility) < COMPONENT_RESPONSIBILITY_MIN_CHARS:
            errors.append(
                f"{entity_id} responsibility is {len(responsibility)} characters; "
                f"at least {COMPONENT_RESPONSIBILITY_MIN_CHARS} are required"
            )
        if not name:
            errors.append(f"{entity_id} has no component name")
        if not entity["lead_team"].startswith("T-"):
            errors.append(f"{entity_id} has no lead team")
        responsibility_key = (entity_type, responsibility)
        if responsibility_key in responsibilities:
            errors.append(
                f"{entity_id} duplicates the responsibility of "
                f"{responsibilities[responsibility_key]} within {entity_type}"
            )
        else:
            responsibilities[responsibility_key] = entity_id
        name_key = (entity_type, name)
        if name_key in names:
            errors.append(f"{entity_id} duplicates the name of {names[name_key]} within {entity_type}")
        else:
            names[name_key] = entity_id
    if errors:
        raise ValueError("component catalog validation failed:\n- " + "\n- ".join(errors))


def domain_for(entity_id: str, entity_type: str) -> str | None:
    parts = entity_id.split("-")
    if entity_type in {"HLR", "SUB"}:
        return parts[0]
    if entity_type in {"HLIR", "SIR"}:
        return parts[1]
    return None


def parent_for(entity_id: str, entity_type: str) -> str | None:
    if entity_type == "SUB":
        return entity_id.rsplit("-", 1)[0]
    if entity_type == "HLIR":
        return "-".join(entity_id.split("-")[1:-1])
    if entity_type == "SIR":
        return "IF-" + "-".join(entity_id.split("-")[1:-1])
    if entity_type == "MQA-SUB":
        return entity_id.rsplit("-", 1)[0]
    return None


VV_CLAIM_PREFIXES = {
    "HLR": "VVC-HLR",
    "SUB": "VVC-SUB",
    "HLIR": "VVC-HLIR",
    "SIR": "VVC-SIR",
    "CORE-COMP": "VVC-COMP",
    "IF-COMP": "VVC-ICOMP",
    "CAT-COMP": "VVC-CCOMP",
    "MQA-REQ": "VVC-MQA-R",
    "MQA-SUB": "VVC-MQA-S",
    "MQA-COMP": "VVC-MQA-C",
}


def vv_claim_id(entity_id: str, entity_type: str) -> str:
    return f"{VV_CLAIM_PREFIXES[entity_type]}:{entity_id}"


def hazard_specificity(mapping_basis: list[str]) -> str:
    """Classify how much engineering judgment a hazard set actually carries.

    Construction replaces a derived set with a reviewed, source-explicit one; the
    construction gate uses this field rather than re-deriving the distinction.
    """
    if "entity_override" in mapping_basis or "source_explicit" in mapping_basis:
        return "source_explicit"
    return "derived"


def materialize() -> dict[str, Any]:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    hazard_document = yaml.safe_load(HAZARD_PATH.read_text(encoding="utf-8"))
    hazard_ids = {item["id"] for item in hazard_document["hazards"]}
    entities = parse_entities()

    expected = dict(policy["coverage_policy"]["required_entity_sets"])
    actual = Counter(entity["entity_type"] for entity in entities.values())

    # Reconcile per key, not by total. A taxonomy that collapses three entity classes
    # into one still sums correctly, which is exactly the defect this rejects.
    count_errors: list[str] = []
    for key in sorted(set(expected) | set(actual)):
        if expected.get(key) != actual.get(key):
            count_errors.append(f"{key}: expected {expected.get(key)}, found {actual.get(key)}")
    if count_errors:
        raise ValueError("entity counts differ by type:\n- " + "\n- ".join(count_errors))

    mappings: dict[str, list[str]] = {}
    overrides = policy["entity_overrides"]
    domain_defaults = policy["domain_hazard_defaults"]
    family_hazards = policy["interface_family_hazards"]
    component_rules = [
        (re.compile(item["pattern"]), item["hazards"])
        for item in policy["component_hazard_rules"]
    ]

    ordered = sorted(
        entities.values(),
        key=lambda item: (
            {"HLR": 0, "SUB": 1, "HLIR": 2, "SIR": 3, "MQA-REQ": 4, "MQA-SUB": 5}.get(
                item["entity_type"], 6
            ),
            item["id"],
        ),
    )
    records: list[dict[str, Any]] = []
    for entity in ordered:
        entity_id = entity["id"]
        entity_type = entity["entity_type"]
        parent_id = parent_for(entity_id, entity_type)
        mapping_basis: list[str] = []
        hazards: list[str] = []

        if entity_id in overrides:
            hazards.extend(overrides[entity_id])
            mapping_basis.append("entity_override")
        elif entity_type == "HLR":
            explicit = re.findall(r"H-\d{2}", " ".join(entity["columns"][2:3]))
            if explicit:
                hazards.extend(explicit)
                mapping_basis.append("source_explicit")
            else:
                hazards.extend(domain_defaults[domain_for(entity_id, entity_type)])
                mapping_basis.append("domain_default")
        elif entity_type in {"SUB", "SIR"}:
            hazards.extend(mappings.get(parent_id or "", []))
            mapping_basis.append("parent_inheritance")
        elif entity_type == "HLIR":
            hazards.extend(mappings.get(parent_id or "", []))
            families = sorted(set(re.findall(r"IF-[A-Z]+-01", " ".join(entity["columns"][2:3]))))
            for family in families:
                hazards.extend(family_hazards.get(family, []))
            mapping_basis.extend(["parent_inheritance", "interface_family"])
        elif entity_type in COMPONENT_TYPES:
            for pattern, assigned in component_rules:
                if pattern.search(entity_id):
                    hazards.extend(assigned)
                    mapping_basis.append(f"component_rule:{pattern.pattern}")
                    break
        elif entity_type in MQA_TYPES:
            parent_hazards = mappings.get(parent_id or "", [])
            if parent_hazards:
                hazards.extend(parent_hazards)
                mapping_basis.append("parent_inheritance")
            else:
                hazards.extend(policy["mqa_default_hazards"])
                mapping_basis.append("mqa_default")
        else:
            raise ValueError(f"{entity_id} has unhandled entity type {entity_type}")

        unique_hazards = sorted(set(hazards), key=lambda value: int(value.split("-")[1]))
        unknown = sorted(set(unique_hazards) - hazard_ids)
        if unknown:
            raise ValueError(f"{entity_id} maps to unknown hazards: {unknown}")
        if len(unique_hazards) < policy["coverage_policy"]["minimum_hazards_per_entity"]:
            raise ValueError(f"{entity_id} has no hazard allocation")
        mappings[entity_id] = unique_hazards
        record = {
            "id": entity_id,
            "entity_type": entity_type,
            "domain": domain_for(entity_id, entity_type),
            "parent_id": parent_id,
            "hazards": unique_hazards,
            "mapping_basis": mapping_basis,
            "hazard_specificity": hazard_specificity(mapping_basis),
            "vv_claim_id": vv_claim_id(entity_id, entity_type),
            "statement_plain": entity["statement_plain"],
            "statement_sha256": sha256_text(entity["statement_latex"]),
            "source_file": entity["source_file"],
            "source_line": entity["source_line"],
        }
        if entity_type in COMPONENT_TYPES or entity_type == "MQA-COMP":
            record["name"] = entity["name"]
            record["layer"] = entity["layer"]
            record["lead_team"] = entity["lead_team"]
        if "allocated_components" in entity:
            record["allocated_components"] = entity["allocated_components"]
        records.append(record)

    claim_ids = [record["vv_claim_id"] for record in records]
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("duplicate V&V claim ID")
    return {
        "schema_version": "0.2",
        "authority_stage": "A_mirror",
        "authoritative": False,
        "policy_source": "spec/allocations.yaml",
        "hazard_source": "spec/hazards.yaml",
        "entity_count": len(records),
        "vv_claim_count": len(records),
        "entity_type_counts": dict(actual),
        "records": records,
    }


def serialize(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = materialize()
    rendered = serialize(document)
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != rendered:
            print("ERROR: materialized trace graph drift detected", file=sys.stderr)
            return 1
        print(
            f"PASS: {document['entity_count']} entities and {document['vv_claim_count']} V&V claims carry hazards"
        )
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(rendered)
    print(f"WROTE: {args.output} with {document['entity_count']} hazard-linked entities")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
