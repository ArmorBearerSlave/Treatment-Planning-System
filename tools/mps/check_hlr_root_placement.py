"""Classify every imported HLR root in the MPS project, and refuse a misplaced one.

REA-C-007 says imported requirement roots persist in the designated import model and
never in a language structure aspect. That rule matters more than it reads. The MPS-4
concept ceiling is derived by check_module_graph from
`languages/*/models/*.structure.mps`, so 119 requirement roots written into a structure
aspect would be counted as 119 concepts and the ceiling would read 215 instead of 96 --
a number that still looks deliberate. Nothing else in the toolchain would object.

The classifier deliberately does not read identifier text. The proof sandbox already
holds requirements called GOV-001 and GOV-001-1, so any rule keyed on identifier shape
would count them. A node is an imported HLR root if and only if:

  * it is a root node, and
  * its concept is nltps.realization.structure.ImportedHLR, and
  * it resides in the designated import model, and
  * it carries the two-part provenance REA-C-006 requires -- one entry fingerprinting
    the source row, distinguished by carrying a line number, and one fingerprinting the
    source artifact.

An ImportedHLR root that fails the placement clauses is reported as invalid placement,
never quietly counted and never quietly ignored. Being uncounted is the dangerous
outcome: it is indistinguishable from the root not existing.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mps_layout  # noqa: E402
from export_hlr_corpus import IMPORTED_HLR, Model  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = REPO_ROOT / "mps" / "NLTPSGovernance"
DEFAULT_BUNDLE = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"
IMPORT_MODEL = "r:42669edd-f887-4e0e-a7a4-d7a2958f0e96(nltps.corpus.hlr)"

IMPORTED_HLR_ROOT = "imported_hlr_root"
INVALID_PLACEMENT = "invalid_import_placement"
NOT_AN_HLR_ROOT = "not_an_hlr_root"


def is_structure_aspect(path: Path, project_root: Path) -> bool:
    """A language structure aspect, which is where check_module_graph counts concepts."""
    try:
        relative = path.relative_to(project_root)
    except ValueError:
        return False
    parts = relative.parts
    if not (len(parts) >= 4 and parts[0] == "languages" and parts[2] == "models"):
        return False
    # A structure aspect is `<lang>.structure.mps` as a file, or `<lang>.structure` as a
    # converted folder. Matching only the file suffix would let a converted structure
    # aspect stop being recognised as one.
    return parts[-1].endswith(".structure.mps") or parts[-1].endswith(".structure")


def has_two_part_provenance(model: Model, node: ElementTree.Element) -> bool:
    entries = model.children(node, "provenance")
    if len(entries) != 2:
        return False
    with_line = [e for e in entries if model.prop(e, "sourceLine") is not None]
    return len(with_line) == 1


def classify_root(model: Model, node: ElementTree.Element, path: Path,
                  project_root: Path, import_model: str) -> tuple[str, str]:
    """(classification, reason) for one root node."""
    if model.concept(node) != IMPORTED_HLR:
        return NOT_AN_HLR_ROOT, "concept is not ImportedHLR"
    if is_structure_aspect(path, project_root):
        return INVALID_PLACEMENT, ("an ImportedHLR root under a language structure aspect "
                                   "would be counted as a concept")
    if model.model_ref != import_model:
        return INVALID_PLACEMENT, (f"an ImportedHLR root outside the designated import "
                                   f"model, in {model.model_ref}")
    if not has_two_part_provenance(model, node):
        return INVALID_PLACEMENT, "an ImportedHLR root without the two-part provenance"
    return IMPORTED_HLR_ROOT, ""


def model_files(project_root: Path) -> list[Path]:
    """Every authored model, in whichever layout it is persisted.

    A converted model is a folder of `.mpsr` root files, so a `*.mps` glob would find
    none of its roots and the count would silently fall to zero rather than error.
    """
    return mps_layout.discover(project_root)


def scan(project_root: Path, import_model: str = IMPORT_MODEL) -> dict:
    counted: list[str] = []
    invalid: list[str] = []
    for path in model_files(project_root):
        try:
            model = Model(path)
        except ElementTree.ParseError:
            continue
        for node in model.roots:
            classification, reason = classify_root(model, node, path, project_root,
                                                   import_model)
            if classification == IMPORTED_HLR_ROOT:
                counted.append(f"{path.name}/{node.get('id')}")
            elif classification == INVALID_PLACEMENT:
                invalid.append(f"{path.relative_to(project_root)}/{node.get('id')}: {reason}")
    return {"counted": counted, "invalid": invalid}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    args = parser.parse_args()

    if not args.project.exists():
        print(f"ERROR: MPS project is missing: {args.project}", file=sys.stderr)
        return 1

    with io.open(args.bundle, encoding="utf-8") as handle:
        expected = json.loads(handle.read())["record_count"]

    result = scan(args.project)
    errors = list(result["invalid"])
    if len(result["counted"]) != expected:
        errors.append(f"{len(result['counted'])} imported HLR roots counted, expected "
                      f"{expected}")

    if errors:
        print("ERROR: imported HLR root placement gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"PASS: {len(result['counted'])} imported HLR roots, all in {IMPORT_MODEL}, none "
          f"in a language structure aspect, each carrying two-part provenance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
