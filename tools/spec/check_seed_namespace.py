#!/usr/bin/env python3
"""Validate namespaced ConOps seed identifiers and typed HLR relations."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPO_ROOT / "spec" / "requirements.yaml"
HLR_BUNDLE = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"
HLR_TEX = REPO_ROOT / "overleaf" / "NL_TPS_High_Level_Requirements.tex"


def main() -> int:
    requirements = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    bundle = json.loads(HLR_BUNDLE.read_text(encoding="utf-8"))
    canonical_ids = {record["id"] for record in bundle["records"]}
    relations = requirements["seed_relations"]
    errors: list[str] = []
    sources = [relation["source"] for relation in relations]
    if len(relations) != 29:
        errors.append(f"expected 29 seed relations, found {len(relations)}")
    if len(sources) != len(set(sources)):
        errors.append("duplicate ConOps seed source")
    for relation in relations:
        if not relation["source"].startswith("CONOPS-"):
            errors.append(f"unqualified seed ID: {relation['source']}")
        if relation["relation"] != "SUPERSEDED_BY":
            errors.append(f"{relation['source']} has untyped or unsupported relation")
        unknown = sorted(set(relation["targets"]) - canonical_ids)
        if unknown:
            errors.append(f"{relation['source']} has unknown targets: {unknown}")

    tex_sources: list[str] = []
    for line in HLR_TEX.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(CONOPS-[A-Z]+-\d{3})\s*&", line)
        if match:
            tex_sources.append(match.group(1))
            if r"SUPERSEDED\_BY" not in line:
                errors.append(f"{match.group(1)} lacks typed relation in rendered crosswalk")
    if tex_sources != sources:
        errors.append("LaTeX crosswalk order/content differs from spec/requirements.yaml")

    if errors:
        print("ERROR: ConOps seed namespace validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PASS: 29 namespaced ConOps seed IDs with typed SUPERSEDED_BY relations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
