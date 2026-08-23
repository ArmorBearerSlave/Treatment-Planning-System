"""Bind the persisted MPS corpus to its neutral export, then compare that export with the
controlled import bundle.

Stage B asks one question: does the imported model say what the controlled document says?
Answering it takes TWO edges, and for the whole of Stage A this gate measured only the
second. It loaded the baseline and the export as files, compared them, and printed a verdict
whose subject was the model -- while the model entered only through root_identity(), which
supplies node identity and never a compared value. Inverting a requirement inside the
persisted corpus left it reporting 119/119 equivalent, which is a specific, confident, wrong
answer to exactly the question a reviewer would run it to ask. MPS-MAT-009 F5.

So the verdict is now composed:

    StageBEquivalencePass  iff  ModelExportCurrent  and  ExportSourceEquivalent

The first edge is measured by export_hlr_corpus, which owns persisted-model traversal, field
selection and serialization. There is one definition of that contract and this gate calls it
rather than restating it. Both edges are measured even when the first fails, because a
changed model breaks one edge while a changed EXPORT breaks both, and reporting one when two
are broken hides which correspondence went. No PASS is emitted unless both hold.

What the first edge establishes is scoped: correspondence over the fields the exporter
selects. A persisted field outside that contract is not observed by it, so the PASS says
"matches the neutral export over the frozen exported-field contract" and not "the model is
equivalent".
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
import hashlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# One authoritative definition of the model-to-export contract. The exporter owns
# persisted-model traversal, field selection and serialization; this gate composes
# that measurement with the source comparison and never re-implements it.
from export_hlr_corpus import (  # noqa: E402
    ExportNotMeasurable,
    IMPORTED_HLR,
    Model,
    corpus_model,
    export_matches_model,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"
DEFAULT_EXPORT = REPO_ROOT / "mps" / "import" / "hlr-corpus-export.json"
DEFAULT_MODEL = corpus_model()
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
        # The model reference, not the filename: a filename changes when persistence
        # changes, and this column is meant to identify the node, not where MPS put it.
        identity[model.prop(ids[0], "value")] = f"{model.model_ref}/{node.get('id')}"
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


def comparison_state(model_path: Path, export_path: Path, bundle_path: Path) -> dict:
    """Identity of every object the composed verdict depends on.

    F1 established the shape: a manifest digest taken before, between and after the
    evaluations, required identical all three times. Reused rather than reinvented, because a
    second definition of "did the state move" would be one more pair of instruments that
    agree until they do not.
    """
    import headless_build

    def digest(path: Path) -> str:
        if path.is_dir():
            parts = []
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    parts.append(str(child.relative_to(path)).replace("\\", "/"))
                    parts.append(hashlib.sha256(child.read_bytes()).hexdigest())
            return hashlib.sha256(chr(10).join(parts).encode("utf-8")).hexdigest()
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""

    state = {
        "neutral_export_sha256": digest(export_path),
        "source_baseline_sha256": digest(bundle_path),
        "corpus_model_sha256": digest(model_path),
    }
    try:
        state["model_tree_sha256"] = headless_build.model_tree_hash(
            REPO_ROOT / "mps" / "NLTPSGovernance")
    except Exception:
        # The corpus digest above already identifies the compared object; the project-wide
        # tree hash is additional provenance and its absence must not be reported as a
        # finding about equivalence.
        state["model_tree_sha256"] = "unavailable"
    return state


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
            print(f"MEASUREMENT INVALID: missing input: {path}. No Stage B verdict is "
                  f"available; this is not a finding about the corpus.", file=sys.stderr)
            return 2

    state_before = comparison_state(args.model, args.export, args.bundle)

    # MPS-MAT-009 F5. Two edges, both required, and BOTH evaluated. Before this repair the
    # gate loaded two files, compared them, and printed a verdict whose subject was the model
    # -- so inverting a requirement inside the persisted corpus left it reporting 119/119
    # equivalent. The binding was carried by a different instrument than the one whose name,
    # docstring and PASS line claimed it.
    #
    # Two policies are in play and they are not the same policy:
    #
    #   execution policy    no PASS is emitted once a prerequisite edge has failed
    #   diagnostic evidence both edges are measured, so under-reporting is detectable
    #
    # They are separable, and conflating them is what would hide a real defect. A changed
    # model breaks only the model/export edge; a changed EXPORT breaks both, because the
    # export then matches neither the model nor the baseline. A gate that stopped at the
    # first failure would report one broken correspondence where two are broken, and the
    # difference between those two states is diagnostic. So both are measured and every
    # failed edge is named, while the PASS remains conditional on all of them holding.
    failed_edges: list[str] = []

    try:
        current, detail, _ = export_matches_model(args.model, args.export)
    except ExportNotMeasurable as error:
        # A measurement failure is not a finding about the corpus. Reporting "the model does
        # not match" when the model could not be read would be a confident wrong answer of
        # exactly the kind this gate is being repaired for.
        print(f"MEASUREMENT INVALID: the model-to-export correspondence could not be "
              f"established, so no Stage B equivalence verdict is available. This is not a "
              f"finding about the corpus.{chr(10)}  {error}", file=sys.stderr)
        return 2
    if not current:
        failed_edges.append(f"persisted model != neutral export -- {detail}")

    state_between = comparison_state(args.model, args.export, args.bundle)

    rows, problems = run(args.bundle, args.export, args.model, args.table)
    expected = read_json(args.bundle)["record_count"]
    if len(rows) != expected:
        problems.append(f"the table has {len(rows)} rows, expected {expected}")
    if problems:
        shown = "; ".join(problems[:3])
        more = f" (and {len(problems) - 3} more)" if len(problems) > 3 else ""
        failed_edges.append(f"neutral export != source baseline -- {shown}{more}")

    state_after = comparison_state(args.model, args.export, args.bundle)
    if not (state_before == state_between == state_after):
        moved = sorted(k for k in state_before
                       if not (state_before[k] == state_between[k] == state_after[k]))
        print(f"MEASUREMENT INVALID: the compared objects changed while the composed check "
              f"was running ({moved}), so the two edges were not established over one state.",
              file=sys.stderr)
        return 2

    if failed_edges:
        print("ERROR: Stage B equivalence NOT ESTABLISHED", file=sys.stderr)
        for edge in failed_edges:
            print(f"- failed edge: {edge}", file=sys.stderr)
        if len(failed_edges) == 1 and failed_edges[0].startswith("persisted model"):
            print("  The export still matches the baseline, so the divergence is between the "
                  "model and its neutral representation: the export is stale.",
                  file=sys.stderr)
        for problem in problems[:40]:
            print(f"  detail: {problem}", file=sys.stderr)
        return 1

    equivalent = sum(1 for row in rows if row["equivalence_verdict"] == "equivalent")
    fields = len(EXACT) + len(SET_EQUAL) + 8
    # Scoped deliberately. The first edge establishes correspondence only over the field set
    # the exporter selects; a persisted field outside that contract is not observed by it. So
    # this does not say "the model is equivalent", which would claim a proposition no edge
    # here measures.
    print(f"PASS: the current persisted MPS HLR representation matches the neutral export "
          f"over the frozen exported-field contract, and {equivalent}/{len(rows)} exported "
          f"requirements satisfy the frozen Stage B source-comparison contract against "
          f"{args.bundle.name} over {fields} compared fields per record.")
    print(f"      edges established over one state: model -> export, export -> source; "
          f"model tree {state_before['model_tree_sha256'][:16]}, export "
          f"{state_before['neutral_export_sha256'][:16]}, baseline "
          f"{state_before['source_baseline_sha256'][:16]}, corpus "
          f"{state_before['corpus_model_sha256'][:16]}")
    # Displayed defensively. A --table outside the repository made relative_to raise AFTER
    # the verdict had been computed, so a correct PASS exited 1 with a traceback: the gate
    # reported a failure it had not found. Present at 1b58895 and corrected here because F5
    # is about a gate's output matching its measurement, and a verdict destroyed while being
    # printed is the same defect at the last possible moment.
    try:
        shown = args.table.relative_to(REPO_ROOT)
    except ValueError:
        shown = args.table
    print(f"      table written to {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
