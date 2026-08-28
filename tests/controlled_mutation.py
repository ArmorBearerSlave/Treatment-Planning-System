"""Mutation of controlled files with a recovery design that survives process termination.

NF-35 / IR-05. The committed helper wrote a modified controlled file to disk, yielded, and
restored in a Python `finally`. A `finally` block is a promise the interpreter keeps only while
the interpreter is alive: SIGKILL, a power loss, an OOM kill or a hard crash between the write
and the restore leaves a tracked controlled file modified, and the next actor inherits a dirty
tree whose contents look authored. There was no pre-image on disk, no journal, and nothing that
would notice at the start of the next run that a previous one had died mid-mutation.

The repair is a write-ahead journal. Before a controlled file is touched, its original bytes are
written to a journal entry and flushed to the platform; the mutation happens after that, and the
journal entry is removed only once the file has been restored and verified byte-identical. So
the pre-image outlives the process that created it, and `recover()` -- which runs on import of
any module that mutates -- restores anything a dead run left behind and says so.

Deliberately NOT a garbage-collected temporary directory: the whole point is that the pre-image
survives the death of the process that wrote it, so it is placed at a fixed, ignored path and
cleaned by successful restoration rather than by an exit handler.

The order matters and is the property under test. Journal first, then mutate. Writing the journal
after the mutation would reproduce the defect with more machinery, because the fatal window is
exactly the interval during which the file is modified and no pre-image exists.

Scope, stated rather than implied: this survives process death. It does not survive deletion of
the journal directory between runs, and it does not make a mutation atomic with respect to a
concurrent reader. Neither is claimed.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Ignored, derived, and outside the controlled tree. A journal entry is recovery state, never
# evidence: nothing reads it to establish a proposition about the repository.
JOURNAL_DIR = REPO_ROOT / "build" / "work" / "mutation-journal"


def _entry_path(target: Path) -> Path:
    digest = hashlib.sha256(str(target.resolve()).encode("utf-8")).hexdigest()[:16]
    return JOURNAL_DIR / f"{digest}.journal"


def _write_journal(target: Path, original: bytes) -> Path:
    """Write the pre-image and flush it to the platform before the caller mutates anything."""
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    entry = _entry_path(target)
    payload = json.dumps({
        "path": str(target.resolve()),
        "sha256": hashlib.sha256(original).hexdigest(),
        "size": len(original),
    }).encode("utf-8")

    # Written to a temporary name and renamed, so a partially written journal is never
    # mistaken for a complete one. A torn journal would be worse than none: it would look
    # like a recoverable pre-image and restore garbage.
    handle, tmp = tempfile.mkstemp(dir=str(JOURNAL_DIR))
    with os.fdopen(handle, "wb") as fh:
        fh.write(len(payload).to_bytes(4, "big"))
        fh.write(payload)
        fh.write(original)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, entry)
    return entry


def _read_journal(entry: Path):
    raw = entry.read_bytes()
    if len(raw) < 4:
        return None
    length = int.from_bytes(raw[:4], "big")
    if len(raw) < 4 + length:
        return None
    meta = json.loads(raw[4:4 + length].decode("utf-8"))
    original = raw[4 + length:]
    if len(original) != meta["size"]:
        return None
    if hashlib.sha256(original).hexdigest() != meta["sha256"]:
        return None
    return meta, original


def recover() -> list[str]:
    """Restore every controlled file a terminated run left modified. Idempotent.

    Returns what it repaired, so a caller can fail loudly rather than silently absorbing the
    evidence that a previous run died. A silent recovery would hide exactly the condition the
    finding is about.
    """
    if not JOURNAL_DIR.exists():
        return []
    recovered = []
    for entry in sorted(JOURNAL_DIR.glob("*.journal")):
        parsed = _read_journal(entry)
        if parsed is None:
            # An unreadable entry is reported, never deleted: deleting it would discard the
            # only record that something went wrong.
            recovered.append(f"{entry.name}: unreadable journal entry, left in place")
            continue
        meta, original = parsed
        target = Path(meta["path"])
        if target.exists() and target.read_bytes() == original:
            entry.unlink()
            continue
        target.write_bytes(original)
        entry.unlink()
        recovered.append(str(target))
    return recovered


def begin(target: Path, new_bytes: bytes) -> bytes:
    """Journal the pre-image, then mutate. The primitives, exposed so a control can be killed
    between them and prove that the ordering is what makes recovery possible."""
    original = target.read_bytes()
    _write_journal(target, original)
    target.write_bytes(new_bytes)
    return original


def end(target: Path, original: bytes) -> None:
    """Restore, verify byte-identity, and only then discard the pre-image."""
    target.write_bytes(original)
    if target.read_bytes() != original:
        raise AssertionError(f"{target.name} not restored byte-identically")
    entry = _entry_path(target)
    if entry.exists():
        entry.unlink()


@contextlib.contextmanager
def mutated_text(target: Path, old: str, new: str, count: int = 1):
    """Replace `old` with `new` on disk, journalled, and restore byte-identically."""
    original = target.read_bytes()
    text = original.decode("utf-8")
    if old not in text:
        raise AssertionError(f"mutation anchor not present in {target.name}")
    begin(target, text.replace(old, new, count).encode("utf-8"))
    try:
        yield
    finally:
        end(target, original)


@contextlib.contextmanager
def mutated_by(target: Path, transform):
    """Journalled mutation for edits a single anchor pair cannot express.

    `transform` receives the decoded text and returns the replacement text. Same guarantee as
    mutated_text: pre-image journalled and flushed before the write, discarded only after
    byte-identical restoration is verified.
    """
    original = target.read_bytes()
    begin(target, transform(original.decode("utf-8")).encode("utf-8"))
    try:
        yield
    finally:
        end(target, original)


def outstanding() -> list[str]:
    """Journal entries present right now. Empty in a healthy tree."""
    if not JOURNAL_DIR.exists():
        return []
    return sorted(p.name for p in JOURNAL_DIR.glob("*.journal"))


# Recovery on import. A run that begins with a controlled file left modified by a dead
# predecessor would otherwise measure a tree nobody authored -- which is the same class of
# defect as a warm output tree keeping a broken project green.
_RECOVERED_AT_IMPORT = recover()
