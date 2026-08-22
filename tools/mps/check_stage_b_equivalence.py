"""Compare the neutral export of the MPS corpus with the controlled import bundle.

Stage B asks one question: does the imported model say what the controlled document says?
The comparison is per record and per field over the 119 ids. A count, a spot check, or a
single aggregate PASS is explicitly not evidence here -- an aggregate result cannot show
which requirement was not compared, which is the failure worth catching.

The output is a 119-row table, one row per requirement, each independently attributable:
the source identifier, the artifact it came from, that record's hash, the MPS root that
represents it, the exported record, and the verdict for that row alone.

Field classes come from mps4-concept-features.yaml, equivalence_contract:

  exact       id, statement_latex, domain, category, category_id, source_hazard_text,
              record_provenance.sha256, record_provenance.source_line,
              source_artifact_provenance.sha256
  set         verification_methods, hazards
  order-free  the two provenance entries, matched by role rather than by position, which
              the exporter has already done

Nothing is normalized. statement_latex is compared exactly, because the exact text is the
one the model claims to mirror.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_hlr_corpus import IMPORTED_HLR, Model  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"
DEFAULT_EXPORT = REPO_ROOT / "mps" / "import" / "hlr-corpus-export.json"
DEFAULT_MODEL = (REPO_ROOT / "mps" / "NLTPSGovernance" / "corpus" / "nltps.corpus"
                 / "models" / "nltps.corpus.hlr.mps")
DEFAULT_TABLE = REPO_ROOT / "mps" / "import" / "stage-b-equivalence.csv"

COLUMNS = ["source_id", "source_artifact_path", "source_record_sha256", "mps_root_identity",
           "neutral_export_identity", "equivalence_verdict"]

EXACT = [
    ("id", lambda rec, b: rec["id"]),
    ("statement_latex", lambda rec, b: rec["normative_text_latex"]),
    ("domain", lambda rec, b: rec["domain"]),
    ("category", lambda rec, b: rec["category"]),
    ("category_id", lambda rec, b: rec["category_id"]),
    ("source_hazard_text", lambda rec, b: rec["source_hazard_latex"]),
    ("bundle_id", lambda rec, b: b["bundle_id"]),
]

SET_EQUAL = [
    ("verification_methods", lambda rec, b: rec["verification_methods"]),
    ("hazards", lambda rec, b: rec["source_hazard_ids"]),
]


def root_identity(model_path: Path) -> dict[str, str]:
    """id -> the MPS root that carries it, so each row is attributable to a node."""
    model = Model(model_path)
    identity = {}
    for node in model.roots:
        if model.concept(node) != IMPORTED_HLR:
            continue
        ids = model.children(node, "identifier")
        if len(ids) != 1:
            continue
        identity[model.prop(ids[0], "value")] = f"{model_path.name}/{node.get('id')}"
    return identity


def compare_record(rec: dict, exported: dict, bundle: dict) -> list[tuple[str, str]]:
    """Every failure for one record, as (category, detail). Empty means equivalent."""
    failures: list[tuple[str, str]] = []

    for field, source_of in EXACT:
        want, got = source_of(rec, bundle), exported.get(field)
        if want == got:
            continue
        if field == "id":
            category = "identifier_mismatch"
        elif field == "statement_latex":
            category = "text_mismatch"
        elif field == "source_hazard_text":
            category = "hazard_mismatch"
        else:
            category = "feature_mismatch"
        failures.append((category, f"{field}: {got!r} != {want!r}"))

    for field, source_of in SET_EQUAL:
        want, got = source_of(rec, bundle), exported.get(field) or []
        if sorted(want) != sorted(got):
            category = "hazard_mismatch" if field == "hazards" else "feature_mismatch"
            failures.append((category, f"{field}: {sorted(got)} != {sorted(want)}"))
        if len(got) != len(set(got)):
            failures.append(("feature_mismatch", f"{field} repeats an entry"))

    if field_differs(exported, "record_provenance", "sha256", rec["record_sha256"]):
        failures.append(("provenance_mismatch", "record_provenance.sha256"))
    if field_differs(exported, "record_provenance", "source_line", rec["source_line"]):
        failures.append(("provenance_mismatch", "record_provenance.source_line"))
    if field_differs(exported, "record_provenance", "source_path", bundle["source"]["path"]):
        failures.append(("provenance_mismatch", "record_provenance.source_path"))
    if field_differs(exported, "source_artifact_provenance", "sha256", bundle["source"]["sha256"]):
        failures.append(("provenance_mismatch", "source_artifact_provenance.sha256"))
    if field_differs(exported, "source_artifact_provenance", "source_path",
                     bundle["source"]["path"]):
        failures.append(("provenance_mismatch", "source_artifact_provenance.source_path"))

    if exported.get("lifecycle_state") != "proposed":
        failures.append(("lifecycle_mismatch",
                         f"lifecycle_state {exported.get('lifecycle_state')!r}"))
    if exported.get("authoritative") is not False:
        failures.append(("feature_mismatch",
                         f"authoritative {exported.get('authoritative')!r}, the mirror is "
                         "not authoritative"))

    for hazard in exported.get("hazards") or []:
        if hazard not in rec["source_hazard_plain"]:
            failures.append(("hazard_mismatch",
                             f"{hazard} is not named in this requirement's own source row"))
    return failures


def read_json(path: Path):
    with io.open(path, encoding="utf-8") as handle:
        return json.loads(handle.read())


def field_differs(exported: dict, group: str, field: str, want) -> bool:
    return (exported.get(group) or {}).get(field) != want


def run(bundle_path: Path, export_path: Path, model_path: Path,
        table_path: Path) -> tuple[list[dict], list[str]]:
    bundle = read_json(bundle_path)
    exported = read_json(export_path)
    identity = root_identity(model_path)

    source = {rec["id"]: rec for rec in bundle["records"]}
    by_id: dict[str, dict] = {}
    problems: list[str] = []
    for record in exported:
        if record["id"] in by_id:
            problems.append(f"duplicate_root: {record['id']} exported more than once")
        by_id[record["id"]] = record

    rows = []
    for source_id in sorted(source):
        rec = source[source_id]
        exported_record = by_id.get(source_id)
        if exported_record is None:
            problems.append(f"missing_root: {source_id} has no exported record")
            verdict = "missing_root"
            failures: list[tuple[str, str]] = []
        else:
            failures = compare_record(rec, exported_record, bundle)
            verdict = "equivalent" if not failures else ";".join(
                sorted({category for category, _ in failures}))
            for category, detail in failures:
                problems.append(f"{category}: {source_id}: {detail}")
        rows.append({
            "source_id": source_id,
            "source_artifact_path": bundle["source"]["path"],
            "source_record_sha256": rec["record_sha256"],
            "mps_root_identity": identity.get(source_id, ""),
            "neutral_export_identity": (f"{export_path.name}#{source_id}"
                                        if exported_record else ""),
            "equivalence_verdict": verdict,
        })
        if exported_record is not None and not identity.get(source_id):
            problems.append(f"missing_root: {source_id} is exported but no MPS root carries it")

    for extra in sorted(set(by_id) - set(source)):
        problems.append(f"extra_root: {extra} is exported but is not in the source")
        rows.append({
            "source_id": extra,
            "source_artifact_path": bundle["source"]["path"],
            "source_record_sha256": "",
            "mps_root_identity": identity.get(extra, ""),
            "neutral_export_identity": f"{export_path.name}#{extra}",
            "equivalence_verdict": "extra_root",
        })

    table_path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(table_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    args = parser.parse_args()

    for path in (args.bundle, args.export, args.model):
        if not path.exists():
            print(f"ERROR: missing input: {path}", file=sys.stderr)
            return 1

    rows, problems = run(args.bundle, args.export, args.model, args.table)
    expected = read_json(args.bundle)["record_count"]

    if len(rows) != expected:
        problems.append(f"the table has {len(rows)} rows, expected {expected}")

    if problems:
        print("ERROR: Stage B equivalence failed", file=sys.stderr)
        for problem in problems[:60]:
            print(f"- {problem}", file=sys.stderr)
        if len(problems) > 60:
            print(f"- ... and {len(problems) - 60} more", file=sys.stderr)
        return 1

    equivalent = sum(1 for row in rows if row["equivalence_verdict"] == "equivalent")
    fields = len(EXACT) + len(SET_EQUAL) + 8
    print(f"PASS: {equivalent}/{len(rows)} requirements compared field by field against "
          f"{args.bundle.name} and found equivalent; {fields} compared fields per record; "
          f"table written to {args.table.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
