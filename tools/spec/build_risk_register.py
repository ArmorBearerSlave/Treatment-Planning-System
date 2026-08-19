#!/usr/bin/env python3
"""Build the hazard-derived risk model and render the controlled risk rows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = REPO_ROOT / "mps" / "import" / "traceability.json"
HAZARD_PATH = REPO_ROOT / "spec" / "hazards.yaml"
SCORE_PATH = REPO_ROOT / "spec" / "risk_scores.yaml"
RISK_SPEC_PATH = REPO_ROOT / "spec" / "risks.yaml"
RISK_TEX_PATH = REPO_ROOT / "overleaf" / "NL_TPS_Risk_and_Mitigation_Register.tex"


def split_row(line: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<!\\)&", line)]


def normalize_id(value: str) -> str:
    match = re.fullmatch(r"\\mbox\{([^{}]+)\}", value.strip())
    return match.group(1) if match else value.strip()


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    return "".join(replacements.get(character, character) for character in value)


def excerpt(value: str, limit: int = 220) -> str:
    if len(value) <= limit:
        return latex_escape(value)
    prefix = value[:limit].rsplit(" ", 1)[0].rstrip(".,;:")
    return latex_escape(prefix) + r"\ldots{}"


def canonical_hlr(entity_id: str, entity_type: str) -> str | None:
    parts = entity_id.split("-")
    if entity_type == "HLR":
        return entity_id
    if entity_type == "SUB":
        return "-".join(parts[:2])
    if entity_type == "HLIR":
        return "-".join(parts[1:3])
    if entity_type == "SIR":
        return "-".join(parts[1:3])
    return None


def component_hlr_links() -> dict[str, list[str]]:
    links: dict[str, set[str]] = defaultdict(set)

    core_path = REPO_ROOT / "overleaf" / "NL_TPS_Component_Realization.tex"
    for line in core_path.read_text(encoding="utf-8").splitlines():
        parts = split_row(line)
        if len(parts) != 4:
            continue
        child_id = normalize_id(parts[0])
        if re.fullmatch(r"[A-Z]{3}-\d{3}-\d{2}", child_id) is None:
            continue
        hlr_id = child_id.rsplit("-", 1)[0]
        for component in re.findall(r"C-[A-Z0-9-]+-\d{2}", parts[2]):
            links[component].add(hlr_id)

    interface_path = REPO_ROOT / "overleaf" / "NL_TPS_Interface_Component_Realization.tex"
    for line in interface_path.read_text(encoding="utf-8").splitlines():
        parts = split_row(line)
        if len(parts) != 4:
            continue
        sir_id = normalize_id(parts[0])
        if re.fullmatch(r"SIR-[A-Z]{3}-\d{3}-\d{2}-\d{2}", sir_id) is None:
            continue
        hlr_id = "-".join(sir_id.split("-")[1:3])
        for component in re.findall(r"IC-[A-Z0-9-]+-\d{2}", parts[2]):
            links[component].add(hlr_id)

    category_path = REPO_ROOT / "overleaf" / "NL_TPS_Functional_Non_Functional_Operational_Component_Realization.tex"
    for line in category_path.read_text(encoding="utf-8").splitlines():
        parts = split_row(line)
        if len(parts) not in {4, 5}:
            continue
        source_child = normalize_id(parts[1])
        if re.fullmatch(r"[A-Z]{3}-\d{3}-\d{2}", source_child) is None:
            continue
        hlr_id = source_child.rsplit("-", 1)[0]
        allocation_field = parts[2] if len(parts) == 4 else parts[3]
        for component in re.findall(r"(?:FC|NFC|OC)-[A-Z0-9-]+-\d{2}", allocation_field):
            links[component].add(hlr_id)

    all_hlrs = {
        f"{domain}-{index:03d}"
        for domain, count in {
            "GOV": 7, "SAF": 10, "NLI": 8, "EVD": 8, "CLN": 9, "PLN": 12,
            "REV": 9, "DAT": 10, "AIM": 8, "HFE": 6, "SEC": 8, "OPS": 7,
            "VAL": 9, "ACC": 8,
        }.items()
        for index in range(1, count + 1)
    }
    for universal in ("IC-BND-01", "IC-CFG-01", "IC-IAM-01", "IC-AUD-01", "IC-TRC-01"):
        links[universal].update(all_hlrs)
    return {component: sorted(values) for component, values in links.items()}


def seed_scores(hlr_ids: list[str]) -> dict[str, Any]:
    document = {
        "schema_version": "0.1",
        "status": "pending_multidisciplinary_facilitated_analysis",
        "scoring_scale": {
            "severity": "site-approved ordinal scale required",
            "occurrence": "site-approved ordinal scale required",
            "detectability": "site-approved ordinal scale required",
            "rpn": "computed only after the three approved ordinal inputs are recorded",
        },
        "gate_policy": "Gate 1 and later require all 119 HLR scores to be approved",
        "scores": {
            hlr_id: {
                "status": "pending_facilitated_review",
                "severity": None,
                "occurrence": None,
                "detectability": None,
                "rpn": None,
                "control_effectiveness": None,
                "residual_risk": None,
                "acceptability": None,
                "approved_by": [],
                "approval_date": None,
            }
            for hlr_id in hlr_ids
        },
    }
    SCORE_PATH.write_text(yaml.safe_dump(document, sort_keys=False, width=120), encoding="utf-8", newline="\n")
    return document


def load_inputs() -> tuple[list[dict[str, Any]], dict[str, dict[str, str]], dict[str, Any]]:
    trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
    # MQA entities are subordinate realization records that do not add to the 119-HLR
    # baseline, so they carry no separate risk record. They are typed as MQA-REQ,
    # MQA-SUB, and MQA-COMP rather than pooled under one MQA type.
    risk_records = [
        record
        for record in trace["records"]
        if not record["entity_type"].startswith("MQA")
    ]
    hazards = yaml.safe_load(HAZARD_PATH.read_text(encoding="utf-8"))
    hazard_map = {hazard["id"]: hazard for hazard in hazards["hazards"]}
    hlr_ids = sorted(record["id"] for record in risk_records if record["entity_type"] == "HLR")
    scores = (
        yaml.safe_load(SCORE_PATH.read_text(encoding="utf-8"))
        if SCORE_PATH.exists()
        else seed_scores(hlr_ids)
    )
    if sorted(scores["scores"]) != hlr_ids:
        raise ValueError("risk score register does not contain exactly the 119 HLR IDs")
    return risk_records, hazard_map, scores


def build_structured_risks() -> dict[str, Any]:
    trace_records, hazards, scores = load_inputs()
    component_links = component_hlr_links()
    structured: list[dict[str, Any]] = []
    for trace in trace_records:
        entity_id = trace["id"]
        entity_type = trace["entity_type"]
        direct_hlr = canonical_hlr(entity_id, entity_type)
        linked_hlrs = [direct_hlr] if direct_hlr else component_links.get(entity_id, [])
        if not linked_hlrs:
            raise ValueError(f"{entity_id} has no HLR scoring source")
        primary = trace["hazards"][0]
        hazard = hazards[primary]
        scoring_source = (
            {"kind": "self", "hlr_ids": linked_hlrs}
            if entity_type == "HLR"
            else {
                "kind": "inherit_parent_hlr" if direct_hlr else "maximum_approved_linked_hlr",
                "hlr_ids": linked_hlrs,
            }
        )
        status_values = {scores["scores"][hlr_id]["status"] for hlr_id in linked_hlrs}
        structured.append(
            {
                "id": entity_id,
                "entity_type": entity_type,
                "hazard_ids": trace["hazards"],
                "primary_hazard": primary,
                "full_normative_text": trace["statement_plain"],
                "normative_text_sha256": trace["statement_sha256"],
                "failure_condition": hazard["failure_condition"],
                "potential_effect": hazard["potential_effect"],
                "mitigation": hazard["control_strategy"],
                "scoring_source": scoring_source,
                "scoring_status": (
                    "approved"
                    if status_values == {"approved"}
                    else "pending_facilitated_score"
                    if entity_type == "HLR"
                    else "pending_parent_score"
                ),
                "override": None,
            }
        )
    return {
        "schema_version": "0.2",
        "status": "hazard_derived_stage_a_risk_model",
        "source_trace_graph": "mps/import/traceability.json",
        "score_source": "spec/risk_scores.yaml",
        "score_policy": {
            "authoritative_level": "HLR",
            "hlr_score_count": 119,
            "child_rule": "inherit approved parent HLR score unless an approved override exists",
            "component_rule": "use maximum approved linked HLR score unless an approved override exists",
            "gate_1_requires_all_scores_approved": True,
            "scores_fabricated_by_generator": False,
        },
        "record_count": len(structured),
        "records": structured,
    }


def render_tex(source_text: str, risk_document: dict[str, Any]) -> str:
    risk_map = {record["id"]: record for record in risk_document["records"]}
    lines: list[str] = []
    replaced = 0
    for line in source_text.splitlines():
        parts = split_row(line)
        entity_id = normalize_id(parts[0]) if parts else ""
        record = risk_map.get(entity_id)
        if record is not None and len(parts) == 7:
            hazard_text = ", ".join(record["hazard_ids"])
            prior_trace = re.sub(r"^Hazards H-\d{2}(?:, H-\d{2})*;\s*", "", parts[1])
            prior_trace = re.sub(r"source/hazard\s+", "source trace ", prior_trace, flags=re.IGNORECASE)
            parts[1] = f"Hazards {hazard_text}; {prior_trace}"
            parts[2] = (
                latex_escape(record["failure_condition"])
                + " Requirement context: "
                + excerpt(record["full_normative_text"])
            )
            parts[3] = latex_escape(record["potential_effect"])
            parts[4] = (
                latex_escape(record["mitigation"])
                + " Realize all linked requirements, interfaces, components, checks, monitoring, and release controls."
            )
            evidence = re.sub(r";\s*FMEA.*$", "", parts[5]).strip()
            score_ids = ", ".join(record["scoring_source"]["hlr_ids"])
            parts[5] = (
                f"{evidence}; FMEA source {score_ids}; "
                f"{latex_escape(record['scoring_status'].replace('_', ' '))}; override none"
            )
            line = " & ".join(parts)
            replaced += 1
        lines.append(line)
    if replaced != 2088:
        raise ValueError(f"expected to render 2,088 risk rows, rendered {replaced}")
    rendered = "\n".join(lines) + "\n"
    rendered = rendered.replace(
        r"\NLMeta{Version}{0.1 - Preliminary engineering baseline}",
        r"\NLMeta{Version}{0.2 - Hazard-derived preliminary baseline}",
    ).replace(
        r"\NLMeta{Date}{18 August 2026}",
        r"\NLMeta{Date}{19 August 2026}",
    )
    if r"\NLMeta{Hazard trace}" not in rendered:
        rendered = rendered.replace(
            r"\NLMeta{Coverage}{2,088 entities: 1,904 requirements and 184 component responsibilities}",
            r"\NLMeta{Coverage}{2,088 entities: 1,904 requirements and 184 component responsibilities}"
            "\n"
            r"\NLMeta{Hazard trace}{Entity hazards and full normative text are controlled in \texttt{spec/risks.yaml}}",
        )
    rendered = rendered.replace(
        "Severity, occurrence, detectability, risk-priority number, benefit-risk determination, residual risk, and control-effectiveness conclusions remain TBD until established by the approved team using site, workflow, modality, disease-site, vendor, model, commissioning, and production evidence.",
        "The 119 HLR score records remain pending approved multidisciplinary facilitated analysis. Child scores inherit only from an approved HLR score, with a controlled override and exception record; component scores use the maximum approved linked HLR score. Gate 1 and later remain blocked until all 119 parent scores and acceptance decisions are approved.",
    )
    rendered = rendered.replace(
        "FMEA fields & Severity, occurrence, detectability, RPN, residual risk, control effectiveness, and acceptability are explicitly TBD pending approved multidisciplinary analysis.",
        "FMEA fields & Severity, occurrence, detectability, RPN, residual risk, control effectiveness, and acceptability are controlled once at the 119-HLR level in \\texttt{spec/risk\\_scores.yaml}. Children inherit the approved parent score unless an approved override exists; components use the maximum approved linked-HLR score. Gate 1 and later require complete approval.",
    )
    return rendered


def serialize_yaml(document: dict[str, Any]) -> str:
    return yaml.safe_dump(document, sort_keys=False, width=140, allow_unicode=False)


def validate_gate(scores: dict[str, Any], gate: int) -> None:
    if gate < 1:
        return
    errors: list[str] = []
    for hlr_id, score in scores["scores"].items():
        values = [score[field] for field in ("severity", "occurrence", "detectability", "rpn")]
        if score["status"] != "approved" or any(value is None for value in values):
            errors.append(hlr_id)
    if errors:
        raise ValueError(f"Gate {gate} blocked: {len(errors)} HLR risk scores are not approved")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--gate", type=int, default=0)
    args = parser.parse_args()
    risk_document = build_structured_risks()
    scores = yaml.safe_load(SCORE_PATH.read_text(encoding="utf-8"))
    validate_gate(scores, args.gate)
    source_text = RISK_TEX_PATH.read_text(encoding="utf-8")
    rendered_tex = render_tex(source_text, risk_document)
    rendered_yaml = serialize_yaml(risk_document)
    if args.check:
        if rendered_tex != source_text:
            print("ERROR: risk register LaTeX is stale", file=sys.stderr)
            return 1
        if not RISK_SPEC_PATH.exists() or RISK_SPEC_PATH.read_text(encoding="utf-8") != rendered_yaml:
            print("ERROR: structured risk register is stale", file=sys.stderr)
            return 1
        print("PASS: 2,088 hazard-derived risk records; full text retained; HLR inheritance enforced")
        return 0
    RISK_TEX_PATH.write_text(rendered_tex, encoding="utf-8", newline="\n")
    RISK_SPEC_PATH.write_text(rendered_yaml, encoding="utf-8", newline="\n")
    print(f"WROTE: {RISK_SPEC_PATH} and updated {RISK_TEX_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
