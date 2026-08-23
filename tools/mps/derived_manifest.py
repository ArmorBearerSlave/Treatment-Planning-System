#!/usr/bin/env python3
"""Enumerate the derived-output path set of an MPS project, as an observation.

MPS-MAT-009, F2 restoration. Removing an authored node does not establish that the
artifacts it generated disappeared: authored persistence and generated output are separate
state, and the four tracked-state criteria -- HEAD, model tree hash, git diff, git
diff --cached -- are all blind to generated output because it is gitignored.

So restoration is checked by regenerating cold from the restored model and comparing the
resulting path set against a cold reconstruction from the baseline model. What this tool
produces is the enumeration itself, not a verdict about it. A recorded "the sets are equal"
is a claim; the two listings are the observation, and they let a later reader re-perform the
comparison without re-running MPS.

The comparison is deliberately an enumeration and not an absence search. Asking whether a
predicted experimental name is gone answers only whether the name that was predicted is
gone. Any additional path, under any name, is a restoration failure, and only enumerating
both sides can see one.

Relative paths, sorted, forward slashes, so two workspaces at different absolute locations
compare equal when their generated output is the same.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

# The four directory kinds the restoration order names, plus source_gen.caches, which is
# reported separately: it is generated state like the rest, but it is a cache, so a
# difference there is worth seeing without letting it silently decide the verdict.
NAMED_KINDS = ("test_gen", "classes_gen", "test_gen.caches", "source_gen")
CACHE_KINDS = ("source_gen.caches",)
ALL_KINDS = NAMED_KINDS + CACHE_KINDS


class MeasurementInvalid(Exception):
    """The manifest could not be measured. Not an observation about the derived output.

    MI-EXIT-01. This branch already SAID measurement invalid and nevertheless exited 1,
    because `raise SystemExit("text")` prints the text and exits 1: Python reserves the
    integer form for the status. So the two states a reader most needs to tell apart --
    "I measured, and found a discrepancy" and "I could not measure" -- arrived at the process
    boundary as the same number.

    The class is measurement-state-to-process-verdict corruption. It is NOT the same as
    F5-FU-02, which is post-measurement corruption: there a correct equivalence result had
    already been computed and was destroyed while being printed. Here no complete measurement
    ever existed, so nothing was corrupted after the fact -- an incomplete measurement was
    mapped onto the verdict code that means a completed one.

    This instrument has no reachable substantive-finding state, and none is invented for it:
    it either enumerates the population or reports that it could not.
    """


def enumerate_derived(project_dir: Path, kinds: tuple[str, ...],
                      label: str = "") -> dict:
    """Every file under every directory of the given kinds, relative to the project."""
    if not project_dir.is_dir():
        raise MeasurementInvalid(f"{project_dir} is not a directory")

    per_kind: dict[str, list[str]] = {kind: [] for kind in kinds}
    roots: list[Path] = []
    for path in sorted(project_dir.rglob("*")):
        if path.is_dir() and path.name in kinds:
            if any(parent in roots for parent in path.parents):
                continue
            roots.append(path)

    for root in roots:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                relative = str(path.relative_to(project_dir)).replace("\\", "/")
                per_kind[root.name].append(relative)

    for kind in per_kind:
        per_kind[kind].sort()

    combined = sorted(p for paths in per_kind.values() for p in paths)
    return {
        # The absolute location is deliberately NOT recorded. Two workspaces at different
        # absolute paths must produce identical manifests when their generated output is the
        # same, and an absolute path in the record would both defeat that and put
        # host-specific material into retained evidence.
        "workspace_label": label,
        "kinds": list(kinds),
        "per_kind_counts": {kind: len(paths) for kind, paths in per_kind.items()},
        "per_kind_paths": per_kind,
        "total_files": len(combined),
        "paths": combined,
        # Over the sorted listing exactly as recorded, so the digest identifies the
        # observation a reader is holding rather than a re-derivation of it.
        "manifest_sha256": hashlib.sha256(
            ("\n".join(combined) + "\n").encode("utf-8")).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--out", type=Path, help="write the manifest as JSON")
    parser.add_argument("--include-caches", action="store_true",
                        help="also enumerate source_gen.caches")
    parser.add_argument("--subtree", help="restrict to paths beginning with this prefix")
    parser.add_argument("--label", default="",
                        help="workspace label recorded instead of the absolute path")
    args = parser.parse_args()

    kinds = ALL_KINDS if args.include_caches else NAMED_KINDS
    try:
        manifest = enumerate_derived(args.project_dir.resolve(), kinds, args.label)
    except MeasurementInvalid as error:
        print(f"MEASUREMENT INVALID: {error}. No manifest is available, so no statement "
              f"about the derived output is made.", file=sys.stderr)
        return 2

    if args.subtree:
        keep = [p for p in manifest["paths"] if p.startswith(args.subtree)]
        manifest = {
            **manifest,
            "subtree": args.subtree,
            "per_kind_paths": {k: [p for p in v if p.startswith(args.subtree)]
                               for k, v in manifest["per_kind_paths"].items()},
            "paths": keep,
            "total_files": len(keep),
            "manifest_sha256": hashlib.sha256(
                ("\n".join(keep) + "\n").encode("utf-8")).hexdigest(),
        }
        manifest["per_kind_counts"] = {k: len(v)
                                       for k, v in manifest["per_kind_paths"].items()}

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(f"derived manifest: {manifest['total_files']} files, "
          f"sha256 {manifest['manifest_sha256'][:16]}")
    for kind, count in sorted(manifest["per_kind_counts"].items()):
        print(f"  {kind:20s} {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
