#!/usr/bin/env python3
"""Build or check the deterministic NL-TPS 119-HLR Stage A mirror bundle.

Each record also carries the controlled F/SA/O category, read from the categorized
requirements document rather than inferred from requirement wording. That document states
a Category ID and the Source ID it aliases on every row, so the mapping is a lookup and
never a judgement. A classifier that read the requirement text would be deciding
governance classification at import time, which is precisely what a non-authoritative
mirror must not do.

Every classification failure is fatal. A partially classified corpus would let MPS-4
materialize requirement roots whose mandatory category came from somewhere nobody can
point at, and the mandatory-ness of that field means the gap would surface as a modelling
error long after the decision that caused it.
"""

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
DEFAULT_CLASSIFICATION = (
    REPO_ROOT / "overleaf"
    / "NL_TPS_High_Level_Functional_Non_Functional_Operational_Requirements.tex"
)
DEFAULT_OUTPUT = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"
DEFAULT_SCHEMA = REPO_ROOT / "mps" / "import" / "hlr-baseline.schema.json"
ARCHITECTURE_SPEC = REPO_ROOT / "spec" / "architecture.yaml"
TERMINOLOGY_SPEC = REPO_ROOT / "spec" / "terminology.yaml"
QUALITY_SPEC = REPO_ROOT / "spec" / "quality_attributes.yaml"

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
# The categorized document's identifier prefixes and the RequirementCategoryEnum member
# each denotes. HNFR is the safety-and-assurance class: the F/SA/O migration changed the
# display label and deliberately preserved the identifier, so the prefix still reads NF.
CATEGORY_BY_PREFIX = {
    "HFR": "functional",
    "HNFR": "cross_cutting_safety_and_assurance_constraint",
    "HOR": "operational",
}
EXPECTED_CATEGORY_COUNTS = {
    "functional": 69,
    "cross_cutting_safety_and_assurance_constraint": 25,
    "operational": 25,
}
ROW_RE = re.compile(
    r"^([A-Z]{3}-\d{3})\s*(?<!\\)&\s*(.*?)\s*(?<!\\)&\s*(.*?)\s*(?<!\\)&\s*(.*?)\s*\\\\\s*$"
)
META_RE = re.compile(r"\\NLMeta\{([^{}]+)\}\{([^{}]+)\}")
# Category ID and the Source ID it aliases, both in \mbox{}, on one categorized row.
CATEGORY_ROW_RE = re.compile(
    r"\\mbox\{(HFR|HNFR|HOR)-([A-Z]{3})-(\d{3})\}\s*&\s*\\mbox\{([A-Z]{3}-\d{3})\}"
)


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


def parse_classification(text: str) -> dict[str, dict[str, str]]:
    """Read Category ID to Source ID from the categorized requirements document.

    Returns source id -> {category_id, category}. A repeated source id is reported rather
    than silently collapsed by the dict, because the collapse would look like success.
    """
    mapping: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    for prefix, domain, number, source_id in CATEGORY_ROW_RE.findall(text):
        if source_id in mapping:
            duplicates.append(source_id)
        mapping[source_id] = {
            "category_id": f"{prefix}-{domain}-{number}",
            "category": CATEGORY_BY_PREFIX[prefix],
        }
    if duplicates:
        raise ValueError(
            f"categorized source lists a source ID more than once: {sorted(set(duplicates))}"
        )
    return mapping


def validate_classification(
    records: list[dict[str, object]], mapping: dict[str, dict[str, str]]
) -> None:
    """Fail closed on anything that would leave a category unattributable."""
    errors: list[str] = []
    record_ids = [str(record["id"]) for record in records]

    unclassified = [rid for rid in record_ids if rid not in mapping]
    if unclassified:
        errors.append(f"HLRs with no category alias: {unclassified}")
    orphan = sorted(set(mapping) - set(record_ids))
    if orphan:
        errors.append(f"category aliases naming an HLR that does not exist: {orphan}")

    repeated = sorted(
        item
        for item, count in Counter(e["category_id"] for e in mapping.values()).items()
        if count > 1
    )
    if repeated:
        errors.append(f"duplicate category IDs: {repeated}")

    # The alias carries the domain it classifies. If the two disagree the alias points at
    # the wrong requirement, which no count or total would reveal.
    for rid in record_ids:
        entry = mapping.get(rid)
        if entry is not None and entry["category_id"].split("-")[1] != rid.split("-")[0]:
            errors.append(
                f"{entry['category_id']} is aliased to {rid}, but their domains differ"
            )

    counts = Counter(mapping[rid]["category"] for rid in record_ids if rid in mapping)
    if dict(counts) != EXPECTED_CATEGORY_COUNTS:
        errors.append(
            f"category counts differ: expected {EXPECTED_CATEGORY_COUNTS}, found {dict(counts)}"
        )
    if sum(counts.values()) != 119:
        errors.append(f"expected 119 categorized HLRs, found {sum(counts.values())}")

    # Independent corroboration. Every safety-and-assurance HLR is named by the controlled
    # quality-attribute register; if the two artifacts disagree, one of them is wrong and
    # the import must not proceed on the strength of either.
    quality_text = QUALITY_SPEC.read_text(encoding="utf-8")
    absent = [
        rid
        for rid in sorted(record_ids)
        if mapping.get(rid, {}).get("category")
        == "cross_cutting_safety_and_assurance_constraint"
        and rid not in quality_text
    ]
    if absent:
        errors.append(f"safety-and-assurance HLRs absent from {QUALITY_SPEC.name}: {absent}")

    if errors:
        raise ValueError("HLR classification validation failed:\n- " + "\n- ".join(errors))


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


def build_bundle(source: Path, classification: Path | None = None) -> dict[str, object]:
    classification = classification or DEFAULT_CLASSIFICATION
    source_bytes = source.read_bytes()
    source_text = source_bytes.decode("utf-8")
    source_metadata = parse_source_metadata(source_text)
    records = parse_records(source_text)
    validate_records(records)

    classification_bytes = classification.read_bytes()
    mapping = parse_classification(classification_bytes.decode("utf-8"))
    validate_classification(records, mapping)
    for record in records:
        entry = mapping[str(record["id"])]
        # The category is controlled content with its own provenance, so it is not folded
        # into record_sha256: that hash is the fingerprint of the HLR source row and has
        # to keep meaning exactly that for Stage B equivalence.
        record["category"] = entry["category"]
        record["category_id"] = entry["category_id"]

    def relative(path: Path) -> str:
        try:
            return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            return str(path.resolve())

    source_path = relative(source)
    classification_source = {
        "path": relative(classification),
        "sha256": sha256_bytes(classification_bytes),
    }
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
        "classification_source": classification_source,
        "expected_domain_counts": EXPECTED_DOMAIN_COUNTS,
        "expected_category_counts": EXPECTED_CATEGORY_COUNTS,
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
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the committed output exactly matches a fresh deterministic build",
    )
    args = parser.parse_args()

    bundle = build_bundle(args.source, args.classification)
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
