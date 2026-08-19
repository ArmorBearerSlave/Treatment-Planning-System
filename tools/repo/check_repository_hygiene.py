#!/usr/bin/env python3
"""Reject tracked build products, environment paths, and obvious secret material."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_ROOT_FILES = {
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "NOTICE.md",
    ".github/CODEOWNERS",
}
GENERATED_SUFFIXES = {".aux", ".log", ".out", ".toc", ".synctex", ".fls", ".fdb_latexmk"}
TEXT_SUFFIXES = {
    ".md", ".txt", ".tex", ".sty", ".py", ".ps1", ".json", ".yaml", ".yml", ".toml", ".xml", ".csv"
}
SENSITIVE_PATTERNS = {
    "Windows user-profile path": re.compile(r"(?i)[A-Z]:[\\/]Users[\\/][A-Za-z0-9._-]+"),
    "Unix home path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "private-key material": re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "GitHub token": re.compile("github" + r"_pat_[A-Za-z0-9_]{20,}"),
    "OpenAI key": re.compile("sk" + r"-[A-Za-z0-9]{20,}"),
    "AWS access key": re.compile("AKIA" + r"[A-Z0-9]{16}"),
}


def git_paths(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args, "-z"], cwd=REPO_ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return [part.decode("utf-8") for part in result.stdout.split(b"\0") if part]


def main() -> int:
    errors: list[str] = []
    tracked = git_paths("ls-files", "--cached", "--others", "--exclude-standard")
    missing = sorted(
        relative for relative in REQUIRED_ROOT_FILES
        if not (REPO_ROOT / relative).exists()
    )
    if missing:
        errors.append(f"required repository-governance files are missing: {missing}")
    ignored_tracked = git_paths("ls-files", "-ci", "--exclude-standard")
    if ignored_tracked:
        errors.append(f"tracked files match ignore rules: {ignored_tracked}")

    for relative in tracked:
        normalized = relative.replace("\\", "/")
        path = REPO_ROOT / relative
        suffix = path.suffix.casefold()
        if normalized.startswith(("tmp/", "output/")):
            errors.append(f"generated build path is tracked: {relative}")
        if suffix in GENERATED_SUFFIXES or suffix == ".pdf":
            errors.append(f"generated artifact type is tracked: {relative}")
        if "/" not in normalized and suffix == ".docx":
            errors.append(f"legacy DOCX remains at repository root: {relative}")
        if suffix not in TEXT_SUFFIXES or not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SENSITIVE_PATTERNS.items():
            match = pattern.search(text)
            if match:
                errors.append(f"{relative} contains {label}: {match.group(0)!r}")

    if errors:
        print("ERROR: repository hygiene gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(tracked)} proposed tracked paths contain no build products, root DOCX files, "
        "user-profile paths, or recognized secret material"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
