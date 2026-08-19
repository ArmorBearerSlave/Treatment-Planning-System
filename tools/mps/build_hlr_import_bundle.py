#!/usr/bin/env python3
"""Build or check the deterministic NL-TPS 119-HLR Stage A mirror bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import yaml

from schema_subset import validate_json_schema


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "overleaf" / "NL_TPS_High_Level_Requirements.tex"
DEFAULT_OUTPUT = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"
DEFAULT_SCHEMA = REPO_ROOT / "mps" / "import" / "hlr-baseline.schema.json"
ARCHITECTURE_SPEC = REPO_ROOT / "spec" / "architecture.yaml"
TERMINOLOGY_SPEC = REPO_ROOT / "spec" / "terminology.yaml"

EXPECTED_DOMAIN_COUNTS = {
    "GOV": 7,
    "SAF": 10,
    "NLI": 8,
    "EVD": 8,
    "CLN": 9,
    "PLN": 12,
    "REV": 9,
    "DAT": 10,
    "AIM": 8,
    "HFE": 6,
    "SEC": 8,
    "OPS": 7,
    "VAL": 9,
    "ACC": 8,
}
ALLOWED_METHODS = {"I", "A", "T", "D", "HFE"}
ROW_RE = re.compile(
    r"^([A-Z]{3}-\d{3})\s*(?<!\\)&\s*(.*?)\s*(?<!\\)&\s*(.*?)\s*(?<!\\)&\s*(.*?)\s*\\\\\s*$"
)
META_RE = re.compile(r"\\NLMeta\{([^{}]+)\}\{([^{}]+)\}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def to_plain(value: str) -> str:
    """Normalize the small LaTeX subset present in the controlled HLR rows."""
    replacements = (
        (r"\slash\allowbreak{}", "/"),
        (r"\allowbreak{}", ""),
        (r"\&", "&"),
        ("--", "-"),
    )
    result = value
    for old, new in replacements:
        result = result.replace(old, new)
    return " ".join(result.split())


def parse_source_metadata(source_text: str) -> dict[str, str]:
    metadata = {key.strip(): value.strip() for key, value in META_RE.findall(source_text)}
    required = ("Document identifier", "Requirements version", "Date")
    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError(f"source is missing required NLMeta fields: {missing}")
    version_match = re.fullmatch(r"(\d+\.\d+)(?:\s+-\s+.*)?", metadata["Requirements version"])
    if not version_match:
        raise ValueError("Requirements version NLMeta is not parseable")
    try:
        source_date = datetime.strptime(metadata["Date"], "%d %B %Y").date().isoformat()
    except ValueError as exc:
        raise ValueError("Date NLMeta must use 'D Month YYYY'") from exc
    return {
        "document_id": metadata["Document identifier"],
        "requirements_version": version_match.group(1),
        "source_date": source_date,
    }


def load_controlled_context() -> dict[str, str]:
    architecture = yaml.safe_load(ARCHITECTURE_SPEC.read_text(encoding="utf-8"))
    terminology = yaml.safe_load(TERMINOLOGY_SPEC.read_text(encoding="utf-8"))
    baseline = architecture["baseline"]
    identity = terminology["identity"]
    return {
        "architecture_baseline": f"{baseline['document_id']}-v{baseline['version']}",
        "technology_name": identity["technology"]["name"],
        "technology_acronym": identity["technology"]["acronym"],
        "implementation_alias": identity["implementation"]["acronym"],
    }


def parse_records(source_text: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(source_text.splitlines(), start=1):
        match = ROW_RE.match(line)
        if not match:
            continue
        requirement_id, normative_latex, source_hazard_latex, methods_latex = match.groups()
        domain = requirement_id[:3]
        methods_plain = to_plain(methods_latex)
        methods = methods_plain.split("/")
        record_hash_input = (
            requirement_id + "\n" + normative_latex + "\n" + source_hazard_latex
            + "\n" + methods_latex
        ).encode("utf-8")
        records.append(
            {
                "id": requirement_id,
                "domain": domain,
                "normative_text_latex": normative_latex,
                "normative_text_plain": to_plain(normative_latex),
                "source_hazard_latex": source_hazard_latex,
                "source_hazard_plain": to_plain(source_hazard_latex),
                "verification_methods": methods,
                "source_line": line_number,
                "record_sha256": sha256_bytes(record_hash_input),
            }
        )
    return records


def validate_records(records: list[dict[str, object]]) -> None:
    errors: list[str] = []
    ids = [str(record["id"]) for record in records]
    counts = Counter(str(record["domain"]) for record in records)

    if len(records) != 119:
        errors.append(f"expected 119 records, found {len(records)}")
    if len(set(ids)) != len(ids):
        duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
        errors.append(f"duplicate IDs: {duplicates}")
    if dict(counts) != EXPECTED_DOMAIN_COUNTS:
        errors.append(
            f"domain counts differ: expected {EXPECTED_DOMAIN_COUNTS}, found {dict(counts)}"
        )

    for domain, expected_count in EXPECTED_DOMAIN_COUNTS.items():
        expected_ids = [f"{domain}-{index:03d}" for index in range(1, expected_count + 1)]
        actual_ids = [requirement_id for requirement_id in ids if requirement_id.startswith(domain + "-")]
        if actual_ids != expected_ids:
            errors.append(f"{domain} IDs are not sequential: {actual_ids}")

    for record in records:
        requirement_id = str(record["id"])
        normative_latex = str(record["normative_text_latex"])
        normative_plain = str(record["normative_text_plain"])
        methods = set(record["verification_methods"])
        if " shall " not in f" {normative_plain.lower()} ":
            errors.append(f"{requirement_id} has no normative shall")
        if not normative_latex:
            errors.append(f"{requirement_id} has empty exact source text")
        if "\\" in normative_plain:
            errors.append(f"{requirement_id} retains an unsupported LaTeX command")
        if not methods or not methods <= ALLOWED_METHODS:
            errors.append(f"{requirement_id} has invalid verification methods: {sorted(methods)}")

    if errors:
        raise ValueError("HLR import validation failed:\n- " + "\n- ".join(errors))


def build_bundle(source: Path) -> dict[str, object]:
    source_bytes = source.read_bytes()
    source_text = source_bytes.decode("utf-8")
    source_metadata = parse_source_metadata(source_text)
    records = parse_records(source_text)
    validate_records(records)
    try:
        source_path = source.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        source_path = str(source.resolve())
    return {
        "schema_version": "0.1",
        "bundle_id": f"NLTPS-HLR-MIRROR-{source_metadata['requirements_version']}",
        "authority_stage": "A_mirror",
        "authoritative": False,
        "controlled_context": load_controlled_context(),
        "source": {
            "path": source_path,
            **source_metadata,
            "sha256": sha256_bytes(source_bytes),
        },
        "expected_domain_counts": EXPECTED_DOMAIN_COUNTS,
        "record_count": len(records),
        "records": records,
    }


def serialize(bundle: dict[str, object]) -> bytes:
    return (json.dumps(bundle, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def validate_bundle_schema(bundle: dict[str, object], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validate_json_schema(bundle, schema)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the committed output exactly matches a fresh deterministic build",
    )
    args = parser.parse_args()

    bundle = build_bundle(args.source)
    validate_bundle_schema(bundle, args.schema)
    rendered = serialize(bundle)

    if args.check:
        if not args.output.exists():
            print(f"ERROR: output does not exist: {args.output}", file=sys.stderr)
            return 1
        existing = args.output.read_bytes()
        existing_bundle = json.loads(existing.decode("utf-8"))
        validate_bundle_schema(existing_bundle, args.schema)
        if existing != rendered:
            print(
                "ERROR: HLR mirror bundle drift detected; regenerate and review the diff",
                file=sys.stderr,
            )
            return 1
        print(
            f"PASS: {bundle['record_count']} HLRs; deterministic output matches; "
            f"source SHA-256 {bundle['source']['sha256']}"
        )
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(rendered)
    print(
        f"WROTE: {args.output} with {bundle['record_count']} HLRs; "
        f"source SHA-256 {bundle['source']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
