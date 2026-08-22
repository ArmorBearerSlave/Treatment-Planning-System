"""Export the imported HLR corpus from the MPS model into a neutral representation.

The point of this file is Stage B evidence. `mps/import/hlr-baseline.json` says what the
controlled document contains; this says what the MPS model contains; and
`check_stage_b_equivalence.py` compares the two field by field. That only means anything
if the two sides are independent, so nothing here reads the bundle. Every value is taken
out of the persisted model, and a field the model does not carry is absent rather than
filled in from the source -- a field quietly sourced from the bundle would compare the
input against itself and could never fail.

The export is deliberately free of MPS specifics. Node ids, model references, the file
the model happens to live in and the order MPS chose to store children in are all
representation, not content, and none of them appears in the output. What remains is
addressable by the source's own identifiers.

Output is UTF-8 with LF newlines, JSON with sorted keys and a trailing newline, records
ascending by id. The MPS-1 finding that a PowerShell generator emitted CRLF is why the
newline is written explicitly rather than left to the host.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = (REPO_ROOT / "mps" / "NLTPSGovernance" / "corpus" / "nltps.corpus"
                 / "models" / "nltps.corpus.hlr.mps")
DEFAULT_OUT = REPO_ROOT / "mps" / "import" / "hlr-corpus-export.json"

IMPORTED_HLR = "nltps.realization.structure.ImportedHLR"
HAZARD = "nltps.governance.structure.Hazard"
LIFECYCLE_STATE = "nltps.foundation.structure.LifecycleState"

# An enumeration value persists as <memberId>/<memberName>. The member id is MPS identity
# and is dropped; that the id resolves to a member of the property's own enumeration is
# check_enum_persistence's question, not this one's.
ENUM_VALUE = re.compile(r"^[^/]+/(.+)$")


class ModelError(Exception):
    pass


class Model:
    """A persisted MPS model, addressed by concept and feature name rather than by index."""

    def __init__(self, path: Path) -> None:
        self.path = path
        root = ElementTree.parse(path).getroot()
        self.concept_by_index: dict[str, str] = {}
        self.feature_by_index: dict[str, str] = {}
        for concept in root.iter("concept"):
            index, name = concept.get("index"), concept.get("name")
            if index and name:
                self.concept_by_index[index] = name
            for kind in ("property", "child", "reference"):
                for feature in concept.findall(kind):
                    findex, fname = feature.get("index"), feature.get("name")
                    if findex and fname:
                        self.feature_by_index[findex] = fname
        self.roots = list(root.findall("node"))
        self.by_id: dict[str, ElementTree.Element] = {}
        for node in self.roots:
            self._index(node)

    def _index(self, node: ElementTree.Element) -> None:
        node_id = node.get("id")
        if node_id:
            self.by_id[node_id] = node
        for child in node.findall("node"):
            self._index(child)

    def concept(self, node: ElementTree.Element) -> str:
        index = node.get("concept", "")
        return self.concept_by_index.get(index, index)

    def prop(self, node: ElementTree.Element, name: str, default=None):
        for element in node.findall("property"):
            if self.feature_by_index.get(element.get("role", "")) == name:
                return element.get("value")
        return default

    def enum(self, node: ElementTree.Element, name: str) -> str | None:
        raw = self.prop(node, name)
        if raw is None:
            return None
        match = ENUM_VALUE.match(raw)
        if not match:
            raise ModelError(f"{name} on node {node.get('id')} is not an enumeration value: {raw!r}")
        return match.group(1)

    def children(self, node: ElementTree.Element, role: str) -> list[ElementTree.Element]:
        return [c for c in node.findall("node")
                if self.feature_by_index.get(c.get("role", "")) == role]

    def ref(self, node: ElementTree.Element, role: str) -> ElementTree.Element | None:
        for element in node.findall("ref"):
            if self.feature_by_index.get(element.get("role", "")) != role:
                continue
            target = element.get("node")
            if target is None:
                # A cross-model target cannot be resolved from this file alone. The corpus
                # keeps its hazards and its lifecycle vocabulary in the same model, so this
                # is a real defect rather than a case to tolerate.
                raise ModelError(
                    f"{role} on node {node.get('id')} points outside this model")
            resolved = self.by_id.get(target)
            if resolved is None:
                raise ModelError(f"{role} on node {node.get('id')} does not resolve: {target}")
            return resolved
        return None


def one(nodes: list, what: str, node_id: str):
    if len(nodes) != 1:
        raise ModelError(f"expected exactly one {what} on node {node_id}, found {len(nodes)}")
    return nodes[0]


def provenance(model: Model, node: ElementTree.Element) -> tuple[dict, dict]:
    """The two provenance entries, told apart by content rather than by position.

    The record entry is the one carrying a line number. Matching them by order would make
    the export depend on the order MPS happened to store the children in, which the
    equivalence contract excludes from comparison.
    """
    entries = model.children(node, "provenance")
    if len(entries) != 2:
        raise ModelError(f"node {node.get('id')} carries {len(entries)} provenance children")
    with_line = [e for e in entries if model.prop(e, "sourceLine") is not None]
    without = [e for e in entries if model.prop(e, "sourceLine") is None]
    if len(with_line) != 1 or len(without) != 1:
        raise ModelError(f"node {node.get('id')} provenance roles cannot be told apart")
    record = {
        "source_path": model.prop(with_line[0], "sourcePath"),
        "source_line": int(model.prop(with_line[0], "sourceLine")),
        "sha256": model.prop(with_line[0], "sha256"),
    }
    artifact = {
        "source_path": model.prop(without[0], "sourcePath"),
        "sha256": model.prop(without[0], "sha256"),
    }
    return record, artifact


def export_root(model: Model, node: ElementTree.Element) -> dict:
    node_id = node.get("id", "")
    identifier = one(model.children(node, "identifier"), "identifier", node_id)
    alias = one(model.children(node, "aliases"), "alias", node_id)
    lifecycle = model.ref(node, "lifecycleState")
    if lifecycle is None:
        raise ModelError(f"node {node_id} has no lifecycleState")
    if model.concept(lifecycle) != LIFECYCLE_STATE:
        raise ModelError(f"node {node_id} lifecycleState is a {model.concept(lifecycle)}")

    hazards = []
    for hazard_ref in model.children(node, "hazards"):
        target = model.ref(hazard_ref, "hazard")
        if target is None:
            raise ModelError(f"node {node_id} carries a HazardRef with no hazard")
        if model.concept(target) != HAZARD:
            raise ModelError(f"node {node_id} hazard link reaches a {model.concept(target)}")
        hazards.append(model.prop(target, "hazardId"))

    record, artifact = provenance(model, node)
    return {
        "id": model.prop(identifier, "value"),
        "domain": model.enum(node, "domain"),
        "category": model.enum(node, "category"),
        "category_id": model.prop(alias, "value"),
        "statement_latex": model.prop(node, "statement"),
        "verification_methods": [model.enum(e, "method")
                                 for e in model.children(node, "verificationMethods")],
        "hazards": sorted(hazards),
        "source_hazard_text": model.prop(node, "sourceHazardText"),
        "record_provenance": record,
        "source_artifact_provenance": artifact,
        "lifecycle_state": model.enum(lifecycle, "state"),
        # MPS omits a property that equals its default, and the declared default is false.
        "authoritative": model.prop(node, "authoritative", "false") == "true",
        "bundle_id": model.prop(node, "bundleId"),
    }


def export(model_path: Path) -> list[dict]:
    model = Model(model_path)
    records = [export_root(model, node) for node in model.roots
               if model.concept(node) == IMPORTED_HLR]

    seen: dict[str, int] = {}
    for record in records:
        if record["id"] in seen:
            # A collision is a conflict, not a merge and not a rename.
            raise ModelError(f"stable identifier {record['id']!r} is used by more than one root")
        seen[record["id"]] = 1
    records.sort(key=lambda r: r["id"])
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true",
                        help="fail if the file on disk differs from what would be written")
    args = parser.parse_args()

    if not args.model.exists():
        print(f"ERROR: model is missing: {args.model}", file=sys.stderr)
        return 1

    try:
        records = export(args.model)
    except ModelError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    text = json.dumps(records, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    if args.check:
        if not args.out.exists():
            print(f"ERROR: export is missing: {args.out}", file=sys.stderr)
            return 1
        with io.open(args.out, encoding="utf-8", newline="") as handle:
            current = handle.read()
        if current != text:
            print("ERROR: the export on disk does not match the model", file=sys.stderr)
            return 1
        print(f"PASS: {len(records)} exported records match the model at {args.model.name}")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print(f"wrote {args.out.relative_to(REPO_ROOT)}: {len(records)} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
