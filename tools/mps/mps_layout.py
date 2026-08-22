"""Where an MPS model's XML actually lives, in either persistence layout.

MPS writes a model one of two ways, and the difference is not cosmetic to anything that
reads the files:

    single-file    models/<name>.mps          one document, header and every root
    file-per-root  models/<name>/.model       the header
                   models/<name>/<Root>.mpsr  one document per root

The root extension is `.mpsr`, not `.mps`. Every tool here that discovered models by
globbing `*.mps` would therefore find nothing inside a converted model -- and the two that
count things would not error, they would simply count less: the enum gate would examine a
smaller population and still report PASS, and the placement gate would count zero imported
roots. A conversion performed correctly would look exactly like data loss, or worse, like
nothing.

This module is the single place that knows the difference, so a later layout change has
one place to be wrong rather than four.
"""
from __future__ import annotations

from pathlib import Path

MODEL_HEADER = ".model"
SINGLE_FILE_SUFFIX = ".mps"
ROOT_SUFFIX = ".mpsr"

# `.mps` is also the name of the IDE's own settings directory, whose name collides with
# the model extension and which is not readable as a model.
SETTINGS_DIR = ".mps"

# Build output. MPS rewrites these; they are not authored persistence.
GENERATED_DIRS = {"source_gen", "classes_gen", "generator_gen", "tests_gen"}


def _excluded(path: Path) -> bool:
    parts = set(path.parts)
    return SETTINGS_DIR in parts or bool(GENERATED_DIRS & parts)


def discover(root: Path, include_generated: bool = False) -> list[Path]:
    """Every authored model under `root`, as the path a reader should open.

    A single-file model is returned as its `.mps` file; a file-per-root model is returned
    as its *folder*, because the folder is the model and the files inside it are its roots.
    """
    folders: set[Path] = set()
    found: list[Path] = []

    for marker in sorted(root.rglob(MODEL_HEADER)):
        if not marker.is_file():
            continue
        if not include_generated and _excluded(marker):
            continue
        folders.add(marker.parent)
        found.append(marker.parent)

    for path in sorted(root.rglob("*" + SINGLE_FILE_SUFFIX)):
        if not path.is_file():
            continue
        if not include_generated and _excluded(path):
            continue
        if any(parent in folders for parent in path.parents):
            # A stray .mps inside a converted model is not a second model.
            continue
        found.append(path)

    return sorted(set(found))


def documents(model_path: Path) -> list[Path]:
    """The XML documents making up one model, header first.

    For a single-file model that is the file itself. For a file-per-root model it is
    `.model` followed by every `.mpsr`, sorted, so a reader sees a deterministic order
    regardless of how the filesystem enumerates them.
    """
    if model_path.is_dir():
        header = model_path / MODEL_HEADER
        roots = sorted(p for p in model_path.glob("*" + ROOT_SUFFIX) if p.is_file())
        return ([header] if header.is_file() else []) + roots
    return [model_path]


def is_file_per_root(model_path: Path) -> bool:
    return model_path.is_dir() and (model_path / MODEL_HEADER).is_file()


def root_files(model_path: Path) -> list[Path]:
    """The per-root documents, empty for a single-file model."""
    if not is_file_per_root(model_path):
        return []
    return sorted(p for p in model_path.glob("*" + ROOT_SUFFIX) if p.is_file())
