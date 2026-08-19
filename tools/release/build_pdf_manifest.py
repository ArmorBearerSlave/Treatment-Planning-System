#!/usr/bin/env python3
"""Build a provenance manifest for controlled-document PDF artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def command(*args: str) -> str:
    result = subprocess.run(
        list(args), cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"command failed ({' '.join(args)}):\n{result.stdout[-3000:]}")
    return result.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=REPO_ROOT / "tmp" / "pdfs" / "controlled" / "build-index.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "output" / "pdf" / "manifest.json")
    parser.add_argument("--release-status", choices=("review", "governed-release"), default="review")
    args = parser.parse_args()
    policy = yaml.safe_load((REPO_ROOT / "spec" / "artifacts.yaml").read_text(encoding="utf-8"))
    index = json.loads(args.index.read_text(encoding="utf-8"))
    status = command("git", "status", "--porcelain=v1")
    dirty = bool(status)
    if args.release_status == "governed-release":
        if dirty:
            raise ValueError("governed release artifacts require a clean worktree")
        if not policy["release_controls"]["governed_release_artifact"]["release_authorized"]:
            raise ValueError("artifact policy does not authorize a governed release")

    source_paths = [
        REPO_ROOT / "main.tex",
        REPO_ROOT / "NL_TPS_Document_Suite_Overleaf.tex",
        REPO_ROOT / "nl_tps_common.sty",
        *sorted((REPO_ROOT / "overleaf").glob("*.tex")),
        *sorted(REPO_ROOT.glob("NL_TPS_*_Overleaf.tex")),
    ]
    unique_sources = sorted(set(source_paths), key=lambda path: path.as_posix())
    artifacts: list[dict[str, Any]] = []
    for record in index["documents"]:
        path = REPO_ROOT / record["artifact"]
        if not path.exists():
            raise ValueError(f"indexed artifact is missing: {record['artifact']}")
        if "_Overleaf" in path.name:
            raise ValueError(f"artifact retains prohibited _Overleaf suffix: {path.name}")
        artifacts.append(
            {
                "filename": path.name,
                "sha256": sha256(path),
                "byte_count": path.stat().st_size,
                "page_count": record["page_count"],
                "source_entry": record["entry"],
                "overfull_box_count": record["overfull_box_count"],
            }
        )
    architecture = yaml.safe_load((REPO_ROOT / "spec" / "architecture.yaml").read_text(encoding="utf-8"))
    manifest = {
        "schema_version": "0.1",
        "policy_id": policy["policy_id"],
        "source_commit": command("git", "rev-parse", "HEAD"),
        "dirty_worktree": dirty,
        "release_status": args.release_status,
        "release_authorized": False,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "architecture_baseline": f"{architecture['baseline']['document_id']}-v{architecture['baseline']['version']}",
        "latex_toolchain": command(shutil.which("pdflatex") or "pdflatex", "--version").splitlines()[0],
        "source_files": [
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "sha256": sha256(path),
                "byte_count": path.stat().st_size,
            }
            for path in unique_sources
        ],
        "artifacts": artifacts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        f"PASS: wrote {args.output} for {len(artifacts)} {args.release_status} artifacts; "
        f"dirty_worktree={dirty}; release_authorized=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
