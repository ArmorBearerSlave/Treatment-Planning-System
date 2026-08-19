#!/usr/bin/env python3
"""Validate controlled Stage A specifications and cross-artifact invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
from schema_subset import validate_json_schema  # noqa: E402


REQUIRED_SPECS = {
    "architecture.yaml",
    "artifacts.yaml",
    "terminology.yaml",
    "decisions.yaml",
    "requirements.yaml",
    "hazards.yaml",
    "interfaces.yaml",
    "components.yaml",
    "allocations.yaml",
    "vv.yaml",
    "risk_scores.yaml",
    "risks.yaml",
    "quality_attributes.yaml",
    "readiness.yaml",
    "defects.yaml",
    "engineering_decisions.yaml",
    "component_crosswalk.yaml",
    "construction_policy.yaml",
}


def load_yaml(name: str) -> dict[str, Any]:
    value = yaml.safe_load((REPO_ROOT / "spec" / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"spec/{name} is not a mapping")
    return value


def main() -> int:
    errors: list[str] = []
    existing = {path.name for path in (REPO_ROOT / "spec").glob("*.yaml")}
    missing = sorted(REQUIRED_SPECS - existing)
    if missing:
        errors.append(f"missing controlled specs: {missing}")

    try:
        documents = {name: load_yaml(name) for name in sorted(REQUIRED_SPECS - set(missing))}
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        print(f"ERROR: unable to load controlled specs: {exc}", file=sys.stderr)
        return 1

    hazards = documents["hazards.yaml"]["hazards"]
    hazard_ids = [hazard["id"] for hazard in hazards]
    if len(hazard_ids) != 18 or len(set(hazard_ids)) != 18:
        errors.append("hazard catalog must contain 18 unique hazards")

    interfaces = documents["interfaces.yaml"]
    required_families = interfaces["required_families"]
    if interfaces["counts"] != {
        "interface_families": 19,
        "high_level_interface_requirements": 357,
        "sub_interface_requirements": 1071,
        "interface_components": 61,
    }:
        errors.append("interface catalog counts differ from the controlled baseline")
    if len(required_families) != 19 or len(set(required_families)) != 19:
        errors.append("interface catalog must contain 19 unique families")

    allocations = documents["allocations.yaml"]
    allocation_families = set(allocations["interface_family_hazards"])
    if allocation_families != set(required_families):
        errors.append("interface-family hazard allocation differs from spec/interfaces.yaml")
    for family in ("IF-DICOM-01", "IF-TPS-01", "IF-IHE-01"):
        if "H-12" not in allocations["interface_family_hazards"][family]:
            errors.append(f"{family} does not carry the H-12 transfer-boundary hazard")
    expected_entities = sum(allocations["coverage_policy"]["required_entity_sets"].values())
    if expected_entities != 2144:
        errors.append(f"allocation entity count is {expected_entities}, expected 2144")

    architecture = documents["architecture.yaml"]
    terminology = documents["terminology.yaml"]
    skeleton = json.loads((REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json").read_text(encoding="utf-8"))
    hlr_bundle = json.loads((REPO_ROOT / "mps" / "import" / "hlr-baseline.json").read_text(encoding="utf-8"))
    expected_baseline = f"{architecture['baseline']['document_id']}-v{architecture['baseline']['version']}"
    for label, actual in (
        ("MPS skeleton", skeleton["architecture_baseline"]),
        ("HLR mirror", hlr_bundle["controlled_context"]["architecture_baseline"]),
    ):
        if actual != expected_baseline:
            errors.append(f"{label} baseline is {actual}, expected {expected_baseline}")
    identity = terminology["identity"]
    if hlr_bundle["controlled_context"]["technology_name"] != identity["technology"]["name"]:
        errors.append("HLR mirror technology name differs from spec/terminology.yaml")

    trace = json.loads((REPO_ROOT / "mps" / "import" / "traceability.json").read_text(encoding="utf-8"))
    try:
        schema_pairs = (
            (trace, REPO_ROOT / "spec" / "schemas" / "traceability.schema.json"),
            (hlr_bundle, REPO_ROOT / "mps" / "import" / "hlr-baseline.schema.json"),
            (architecture, REPO_ROOT / "spec" / "schemas" / "architecture.schema.json"),
            (documents["decisions.yaml"], REPO_ROOT / "spec" / "schemas" / "decisions.schema.json"),
            (terminology, REPO_ROOT / "spec" / "schemas" / "terminology.schema.json"),
            (skeleton, REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.schema.json"),
        )
        schema_ids: list[str] = []
        for instance, schema_path in schema_pairs:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            schema_ids.append(schema["$id"])
            validate_json_schema(instance, schema)
        if len(schema_ids) != len(set(schema_ids)) or any(not value.startswith("urn:gcpl:nltps:schema:") for value in schema_ids):
            errors.append("controlled JSON Schema IDs must be unique stable GCPL / NL-TPS URNs")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(str(exc))

    vv = documents["vv.yaml"]
    if vv["counts"]["total_claims"] != trace["vv_claim_count"]:
        errors.append("V&V claim count differs from the materialized trace")
    risks = documents["risks.yaml"]
    if len(risks["records"]) != 2088:
        errors.append(f"risk model has {len(risks['records'])} records, expected 2088")
    risk_by_id = {record["id"]: record for record in risks["records"]}
    gov001 = risk_by_id.get("GOV-001", {})
    if gov001.get("hazard_ids") != ["H-13", "H-18"]:
        errors.append("GOV-001 must map to H-13 and H-18")
    if "DICOM" in gov001.get("failure_condition", ""):
        errors.append("GOV-001 still carries the erroneous DICOM failure condition")
    if any("...." in record["full_normative_text"] for record in risks["records"]):
        errors.append("risk model contains data-losing four-dot truncation")

    defects = documents["defects.yaml"]["defects"]
    expected_defects = (
        {f"A{index}" for index in range(1, 8)}
        | {f"B{index}" for index in range(1, 8)}
        | {"C1", "C2"}
        | {f"K{index}" for index in range(1, 8)}
    )
    actual_defects = {defect["id"] for defect in defects}
    if len(defects) != len(expected_defects) or actual_defects != expected_defects:
        errors.append("defect register must contain exactly A1-A7, B1-B7, C1-C2, K1-K7")
    for defect in defects:
        for field in ("severity", "disposition", "correction", "evidence", "verification", "residual"):
            if not defect.get(field):
                errors.append(f"defect {defect['id']} is missing {field}")
    # The human-readable register is hand-maintained; this keeps it from drifting away
    # from the structured source, which is the failure the corpus already warns about.
    register_tex = (REPO_ROOT / "overleaf" / "NL_TPS_Defect_Resolution_Register.tex").read_text(
        encoding="utf-8"
    )
    undocumented = sorted(
        defect["id"] for defect in defects if f"\n{defect['id']} &" not in register_tex
    )
    if undocumented:
        errors.append(
            f"defects {undocumented} are in spec/defects.yaml but not in the controlled register"
        )
    readiness = documents["readiness.yaml"]["recommendations"]
    expected_readiness = {f"RRR-{index:03d}" for index in range(1, 13)}
    if len(readiness) != 12 or {item["id"] for item in readiness} != expected_readiness:
        errors.append("readiness register must contain exactly RRR-001 through RRR-012")
    artifact_policy = documents["artifacts.yaml"]
    if artifact_policy["source_control_policy"]["tracked_generated_pdfs_permitted"]:
        errors.append("artifact policy must prohibit tracked generated PDFs")
    if artifact_policy["release_controls"]["governed_release_artifact"]["release_authorized"]:
        errors.append("governed artifact release is unexpectedly authorized")

    engineering_decisions = documents["engineering_decisions.yaml"]["decisions"]
    expected_engineering = {f"D-ENG-{index:03d}" for index in range(1, 11)}
    if {item["id"] for item in engineering_decisions} != expected_engineering:
        errors.append("engineering decision register must contain exactly D-ENG-001 through D-ENG-010")
    for item in engineering_decisions:
        if "blocks_gates" not in item or "blocks_entities" not in item:
            errors.append(f"{item['id']} does not declare what it blocks")

    crosswalk = documents["component_crosswalk.yaml"]
    if crosswalk["decision"] != "D-ENG-004":
        errors.append("component crosswalk must cite D-ENG-004 as its governing decision")
    crosswalk_ids = [member["id"] for entry in crosswalk["entries"] for member in entry["members"]]
    if len(crosswalk_ids) != len(set(crosswalk_ids)):
        errors.append("a component appears in more than one crosswalk group")

    policy = documents["construction_policy.yaml"]
    trace_types = set(trace["entity_type_counts"])
    policy_types = set(policy["treatment_by_entity_type"])
    if policy_types != trace_types:
        errors.append(
            f"construction policy covers {sorted(policy_types)} but the trace graph "
            f"contains {sorted(trace_types)}"
        )
    shape = policy["effort_shape"]
    if shape["hand_authored"] + shape["derived"] + shape["inherited"] != shape["total"]:
        errors.append("construction effort shape does not sum to its declared total")
    if shape["total"] != trace["entity_count"]:
        errors.append("construction effort shape total differs from the materialized entity count")
    policy_totals: dict[str, int] = {}
    for entity_type, treatment in policy["treatment_by_entity_type"].items():
        policy_totals[treatment] = policy_totals.get(treatment, 0) + trace["entity_type_counts"][entity_type]
    declared_totals = {
        "hand": shape["hand_authored"],
        "derived": shape["derived"],
        "inherited": shape["inherited"],
    }
    if policy_totals != declared_totals:
        errors.append(
            f"construction effort shape {declared_totals} does not match the per-type "
            f"treatment assignment {policy_totals}"
        )

    if errors:
        print("ERROR: controlled specification gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    schema_count = len(list((REPO_ROOT / "spec" / "schemas").glob("*.schema.json"))) + 2
    print(
        f"PASS: {len(REQUIRED_SPECS)} controlled specs, {schema_count} schemas, "
        f"{len(hazard_ids)} hazards, {len(required_families)} interface families, "
        f"{trace['vv_claim_count']:,} trace/V&V claims, {len(risks['records']):,} risks, "
        f"{len(defects)} defects, {len(readiness)} readiness dispositions, "
        f"{len(engineering_decisions)} engineering decisions, and "
        f"{len(crosswalk['entries'])} crosswalk groups reconcile"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
