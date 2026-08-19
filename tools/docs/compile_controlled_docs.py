#!/usr/bin/env python3
"""Compile every controlled LaTeX document and the combined suite."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE_SOURCE = REPO_ROOT / "NL_TPS_Document_Suite_Overleaf.tex"
INCLUDE_RE = re.compile(
    r"\\NLTPSIncludeDocument\{(?P<title>[^{}]+)\}"
    r"\{overleaf/(?P<source>NL_TPS_[^{}]+\.tex)\}\{[^{}]+\}"
)
FATAL_RE = re.compile(r"LaTeX Error|Undefined control sequence|Fatal error|Emergency stop")
UNDEFINED_RE = re.compile(r"There were undefined references|undefined references")
OVERFULL_RE = re.compile(r"Overfull \\hbox")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def page_count(pdfinfo: str, pdf: Path) -> int:
    result = run([pdfinfo, str(pdf)])
    if result.returncode:
        raise RuntimeError(f"pdfinfo failed for {pdf}:\n{result.stdout[-3000:]}")
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise RuntimeError(f"pdfinfo did not report pages for {pdf}")
    return int(match.group(1))


def controlled_entries() -> list[dict[str, str]]:
    text = SUITE_SOURCE.read_text(encoding="utf-8")
    entries: list[dict[str, str]] = []
    for match in INCLUDE_RE.finditer(text):
        source = Path(match.group("source"))
        entry = REPO_ROOT / f"{source.stem}_Overleaf.tex"
        if not entry.exists():
            raise ValueError(f"missing top-level entry point for {source}: {entry.name}")
        entries.append(
            {
                "title": match.group("title"),
                "entry": entry.name,
                "artifact": f"GCPL_{source.stem}.pdf",
            }
        )
    if len(entries) != 19:
        raise ValueError(f"expected 19 controlled documents, found {len(entries)}")
    return entries


def compile_entry(
    pdflatex: str,
    pdfinfo: str,
    entry: str,
    artifact: str,
    run_root: Path,
    output_dir: Path,
    passes: int,
) -> dict[str, Any]:
    build_dir = run_root / Path(entry).stem
    build_dir.mkdir(parents=True, exist_ok=True)
    command = [
        pdflatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={build_dir}",
        entry,
    ]
    for pass_number in range(1, passes + 1):
        result = run(command)
        if result.returncode:
            raise RuntimeError(
                f"{entry} failed on pass {pass_number}:\n{result.stdout[-6000:]}"
            )
    stem = Path(entry).stem
    built_pdf = build_dir / f"{stem}.pdf"
    log_path = build_dir / f"{stem}.log"
    if not built_pdf.exists() or not log_path.exists():
        raise RuntimeError(f"{entry} did not produce its PDF and log")
    log = log_path.read_text(encoding="utf-8", errors="replace")
    if FATAL_RE.search(log):
        raise RuntimeError(f"{entry} log contains a fatal LaTeX condition")
    if UNDEFINED_RE.search(log):
        raise RuntimeError(f"{entry} log contains undefined references after {passes} passes")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / artifact
    shutil.copy2(built_pdf, target)
    return {
        "entry": entry,
        "artifact": target.relative_to(REPO_ROOT).as_posix(),
        "page_count": page_count(pdfinfo, target),
        "overfull_box_count": len(OVERFULL_RE.findall(log)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "output" / "pdf")
    parser.add_argument("--build-root", type=Path, default=REPO_ROOT / "tmp" / "pdfs" / "controlled")
    parser.add_argument("--index", type=Path, default=REPO_ROOT / "tmp" / "pdfs" / "controlled" / "build-index.json")
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--suite-only", action="store_true")
    args = parser.parse_args()
    if args.passes < 2:
        raise ValueError("at least two LaTeX passes are required")
    pdflatex = shutil.which("pdflatex")
    pdfinfo = shutil.which("pdfinfo")
    if not pdflatex or not pdfinfo:
        raise RuntimeError("pdflatex and pdfinfo must be available on PATH")
    args.build_root.mkdir(parents=True, exist_ok=True)
    run_root = Path(tempfile.mkdtemp(prefix="run-", dir=args.build_root))
    entries = [] if args.suite_only else controlled_entries()
    entries.append(
        {
            "title": "Controlled Documentation Suite",
            "entry": "main.tex",
            "artifact": "GCPL_NL_TPS_Controlled_Documentation_Suite.pdf",
        }
    )
    results: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, 1):
        result = compile_entry(
            pdflatex,
            pdfinfo,
            entry["entry"],
            entry["artifact"],
            run_root,
            args.output_dir,
            args.passes,
        )
        result["title"] = entry["title"]
        results.append(result)
        print(
            f"PASS {index}/{len(entries)}: {entry['entry']} -> {entry['artifact']} "
            f"({result['page_count']} pages; {result['overfull_box_count']} overfull warnings)"
        )
    index_document = {
        "schema_version": "0.1",
        "run_directory": run_root.relative_to(REPO_ROOT).as_posix(),
        "document_count": len(results),
        "documents": results,
    }
    args.index.parent.mkdir(parents=True, exist_ok=True)
    args.index.write_text(json.dumps(index_document, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: compiled {len(results)} controlled PDF artifacts; index {args.index}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
