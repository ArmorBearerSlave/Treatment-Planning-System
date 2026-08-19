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
            statement = parts[1]
            existing = entities.get(entity_id)
            if existing and len(existing["statement_latex"]) >= len(statement):
                continue
            entities[entity_id] = {
                "id": entity_id,
                "entity_type": entity_type,
                "statement_latex": statement,
                "statement_plain": to_plain(statement),
                "source_file": f"overleaf/{filename}",
                "source_line": line_number,
                "columns": parts,
            }
    return entities


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
    if entity_type == "MQA":
        if re.fullmatch(r"MQA-\d{3}-\d{2}", entity_id):
            return entity_id.rsplit("-", 1)[0]
    return None


def vv_claim_id(entity_id: str, entity_type: str) -> str:
    prefixes = {
        "HLR": "VVC-HLR",
        "SUB": "VVC-SUB",
        "HLIR": "VVC-HLIR",
        "SIR": "VVC-SIR",
        "CORE-COMP": "VVC-COMP",
        "IF-COMP": "VVC-ICOMP",
        "CAT-COMP": "VVC-CCOMP",
    }
    if entity_type in prefixes:
        return f"{prefixes[entity_type]}:{entity_id}"
    if re.fullmatch(r"MQA-\d{3}", entity_id):
        return f"VVC-MQA-R:{entity_id}"
    if re.fullmatch(r"MQA-\d{3}-\d{2}", entity_id):
        return f"VVC-MQA-S:{entity_id}"
    return f"VVC-MQA-C:{entity_id}"


def materialize() -> dict[str, Any]:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    hazard_document = yaml.safe_load(HAZARD_PATH.read_text(encoding="utf-8"))
    hazard_ids = {item["id"] for item in hazard_document["hazards"]}
    entities = parse_entities()

    expected = dict(policy["coverage_policy"]["required_entity_sets"])
    actual = Counter()
    for entity in entities.values():
        entity_type = entity["entity_type"]
        if entity_type == "MQA":
            entity_id = entity["id"]
            if re.fullmatch(r"MQA-\d{3}", entity_id):
                actual["MQA-REQ"] += 1
            elif re.fullmatch(r"MQA-\d{3}-\d{2}", entity_id):
                actual["MQA-SUB"] += 1
            else:
                actual["MQA-COMP"] += 1
        else:
            actual[entity_type] += 1
    if dict(actual) != expected:
        raise ValueError(f"entity counts differ: expected {expected}, found {dict(actual)}")

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
        key=lambda item: ({"HLR": 0, "SUB": 1, "HLIR": 2, "SIR": 3}.get(item["entity_type"], 4), item["id"]),
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
        elif entity_type in {"CORE-COMP", "IF-COMP", "CAT-COMP"}:
            for pattern, assigned in component_rules:
                if pattern.search(entity_id):
                    hazards.extend(assigned)
                    mapping_basis.append(f"component_rule:{pattern.pattern}")
                    break
        else:
            hazards.extend(policy["mqa_default_hazards"])
            mapping_basis.append("mqa_default")

        unique_hazards = sorted(set(hazards), key=lambda value: int(value.split("-")[1]))
        unknown = sorted(set(unique_hazards) - hazard_ids)
        if unknown:
            raise ValueError(f"{entity_id} maps to unknown hazards: {unknown}")
        if len(unique_hazards) < policy["coverage_policy"]["minimum_hazards_per_entity"]:
            raise ValueError(f"{entity_id} has no hazard allocation")
        mappings[entity_id] = unique_hazards
        records.append(
            {
                "id": entity_id,
                "entity_type": entity_type,
                "domain": domain_for(entity_id, entity_type),
                "parent_id": parent_id,
                "hazards": unique_hazards,
                "mapping_basis": mapping_basis,
                "vv_claim_id": vv_claim_id(entity_id, entity_type),
                "statement_plain": entity["statement_plain"],
                "statement_sha256": sha256_text(entity["statement_latex"]),
                "source_file": entity["source_file"],
                "source_line": entity["source_line"],
            }
        )

    claim_ids = [record["vv_claim_id"] for record in records]
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("duplicate V&V claim ID")
    return {
        "schema_version": "0.1",
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
