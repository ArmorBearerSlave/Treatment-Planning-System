"""Compare declared model persistence with the persistence MPS actually used on disk.

`project.default_model_persistence` has been declared `file-per-root` since MPS-0, in both
`spec/architecture.yaml` and `mps/bootstrap/language-skeleton.json`.
`check_language_skeleton` compares those two declarations with each other and never looks
at a model. Four checkpoints therefore closed green on a persistence constraint that no
model in the project has ever satisfied.

That is the failure this file exists to make impossible to repeat. A gate that compares a
declaration with another declaration verifies neither of them; it verifies only that
somebody wrote the same word twice. What follows observes the layout MPS wrote.

Two on-disk shapes are distinguishable without interpreting model content:

    single-file    models/<name>.mps            one file holding every root
    file-per-root  models/<name>/.model         a folder, one .mps file per root

Scope is deliberate. The project default is reported for every model, so the divergence is
visible rather than assumed, but it is *enforced* only where a controlled contract requires
it: `file_per_root_contract` in mps4-concept-features.yaml binds the designated import
model. Demanding conversion of every language aspect model would assert more than any
contract does.
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

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = REPO_ROOT / "mps" / "NLTPSGovernance"
ARCHITECTURE = REPO_ROOT / "spec" / "architecture.yaml"
SKELETON = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"

# The model the MPS-4 file-per-root contract names. Enforced; everything else is reported.
CONTRACTED_MODELS = ("r:42669edd-f887-4e0e-a7a4-d7a2958f0e96(nltps.corpus.hlr)",)

SINGLE_FILE = "single-file"
FILE_PER_ROOT = "file-per-root"

# Generated output, not authored persistence. MPS rewrites these on every build.
GENERATED = {"source_gen", "classes_gen", "generator_gen", "tests_gen"}


def declared_persistence() -> str:
    """What the controlled specification says the project default is."""
    import yaml

    with io.open(ARCHITECTURE, encoding="utf-8") as handle:
        architecture = yaml.safe_load(handle.read())
    for key in ("mps_project", "project", "mps"):
        block = architecture.get(key)
        if isinstance(block, dict) and "default_model_persistence" in block:
            return block["default_model_persistence"]
    for block in architecture.values():
        if isinstance(block, dict) and "default_model_persistence" in block:
            return block["default_model_persistence"]
    raise SystemExit("ERROR: spec/architecture.yaml declares no default_model_persistence")


def model_ref(path: Path) -> str | None:
    try:
        return ElementTree.parse(path).getroot().get("ref")
    except ElementTree.ParseError:
        return None


def observe(project_root: Path) -> list[dict]:
    """Every authored model on disk, with the persistence shape MPS actually wrote."""
    observed: list[dict] = []
    seen_dirs: set[Path] = set()

    for marker in sorted(project_root.rglob(".model")):
        if GENERATED & set(marker.parts) or ".mps" in marker.parts:
            continue
        folder = marker.parent
        seen_dirs.add(folder)
        roots = mps_layout.root_files(folder)
        observed.append({
            "reference": model_ref(marker) or folder.name,
            "path": str(folder.relative_to(project_root)),
            "persistence": FILE_PER_ROOT,
            "root_files": len(roots),
        })

    for path in sorted(project_root.rglob("*.mps")):
        if not path.is_file() or GENERATED & set(path.parts) or ".mps" in path.parts:
            continue
        if any(parent in seen_dirs for parent in path.parents):
            continue
        reference = model_ref(path)
        if reference is None:
            continue
        observed.append({
            "reference": reference,
            "path": str(path.relative_to(project_root)),
            "persistence": SINGLE_FILE,
            "root_files": 1,
        })

    observed.sort(key=lambda entry: entry["path"])
    return observed


def check(project_root: Path, declared: str,
          contracted: tuple[str, ...] = CONTRACTED_MODELS) -> tuple[list[dict], list[str]]:
    observed = observe(project_root)
    by_reference = {entry["reference"]: entry for entry in observed}
    errors: list[str] = []

    for reference in contracted:
        entry = by_reference.get(reference)
        if entry is None:
            errors.append(f"the contracted model {reference} was not found on disk")
            continue
        if entry["persistence"] != declared:
            errors.append(
                f"{reference} is persisted {entry['persistence']} at {entry['path']}, but "
                f"the controlled specification declares {declared}. MPS converts a model "
                f"with the IDE action Convert to File-Per-Root Format; no mps_mcp_* "
                f"operation sets a model's persistence mode, and rewriting the layout on "
                f"disk is prohibited by ADR-001"
            )
    return observed, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--report", action="store_true",
                        help="print every observed model and its persistence, then exit 0")
    args = parser.parse_args()

    if not args.project.exists():
        print(f"ERROR: MPS project is missing: {args.project}", file=sys.stderr)
        return 1

    declared = declared_persistence()
    observed, errors = check(args.project, declared)

    counts: dict[str, int] = {}
    for entry in observed:
        counts[entry["persistence"]] = counts.get(entry["persistence"], 0) + 1

    if args.report:
        print(json.dumps({"declared": declared, "counts": counts, "models": observed},
                         indent=1, sort_keys=True))
        return 0

    if errors:
        print("ERROR: model persistence gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(f"- observed across the project: {counts}", file=sys.stderr)
        return 1

    print(f"PASS: declared {declared}; every contracted model is persisted that way; "
          f"observed across the project: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
