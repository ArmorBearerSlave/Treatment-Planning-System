#!/usr/bin/env python3
"""Reject tracked build products, environment paths, and obvious secret material."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
# MPS-MAT-009 F1. Retained runner artifacts are named here, one path at a time, and the
# listing exempts them from ONE rule: the generated-artifact-type rejection. Every other
# predicate in this file -- disclosure, secrets, line endings, the index check -- continues
# to apply to them unchanged. That asymmetry is the whole design: the conflict was that a
# build log is simultaneously the evidence and a generated artifact, and only the second
# fact is what the hygiene rule was about.
EVIDENCE_ALLOWLIST = REPO_ROOT / "mps" / "materialization" / "evidence-allowlist.yaml"
ALLOWLIST_REQUIRED_FIELDS = ("path", "artifact_class", "reason", "supports")
REQUIRED_ROOT_FILES = {
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "NOTICE.md",
    ".github/CODEOWNERS",
}
GENERATED_SUFFIXES = {".aux", ".log", ".out", ".toc", ".synctex", ".fls", ".fdb_latexmk"}
TEXT_SUFFIXES = {
    ".md", ".txt", ".tex", ".sty", ".py", ".ps1", ".json", ".yaml", ".yml", ".toml", ".xml", ".csv",
    # MPS-MAT-009 F1. Retained execution evidence types. These were tracked and NOT scanned:
    # disclosure coverage was keyed on extension, so a retained runner log, an intervention
    # patch or a review report could carry a host path and pass. The .log case was the sharp
    # one -- the generated-artifact rule rejected those files for being logs, which looked
    # like coverage, and the moment F1 exempted three of them by name they would have become
    # entirely unscanned. An exemption from one rule must not silently remove another, so the
    # scan is widened at the same time as the exemption is introduced.
    ".log", ".patch", ".diff", ".html",
}
# MPS owns its persistence and writes CRLF on Windows. ADR-001 prohibits any text tool
# from normalizing it, and no determinism gate reads it, so it is exempt from the
# working-tree check below. The index-level check still covers it: .gitattributes
# normalizes on add, so the committed bytes and every fresh checkout are LF.
TOOL_OWNED_PERSISTENCE_PREFIXES = ("mps/NLTPSGovernance/",)
SENSITIVE_PATTERNS = {
    "Windows user-profile path": re.compile(r"(?i)[A-Z]:[\\/]Users[\\/][A-Za-z0-9._-]+"),
    "Unix home path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "private-key material": re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "GitHub token": re.compile("github" + r"_pat_[A-Za-z0-9_]{20,}"),
    "OpenAI key": re.compile("sk" + r"-[A-Za-z0-9]{20,}"),
    "AWS access key": re.compile("AKIA" + r"[A-Z0-9]{16}"),
}


def load_generated_type_allowlist() -> tuple[dict[str, dict], list[str]]:
    """Exact repository-relative paths exempt from the generated-artifact-type rule.

    Returns the allowlist and any problems with the allowlist itself. A register that
    exempts things is a control, so it is validated like one: every entry must say what the
    artifact is, why it is retained, and which obligation it supports, and every listed path
    must exist. A stale entry is how an exemption outlives its reason.
    """
    problems: list[str] = []
    if not EVIDENCE_ALLOWLIST.is_file():
        return {}, problems
    import yaml

    try:
        body = yaml.safe_load(EVIDENCE_ALLOWLIST.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        return {}, [f"the evidence allowlist is not parseable: {error}"]

    allowed: dict[str, dict] = {}
    for entry in body.get("entries") or []:
        relative = entry.get("path")
        if not relative:
            problems.append("an evidence-allowlist entry names no path")
            continue
        missing = [f for f in ALLOWLIST_REQUIRED_FIELDS if not entry.get(f)]
        if missing:
            problems.append(
                f"evidence-allowlist entry {relative} is missing {missing}; an exemption "
                f"that does not say what it exempts or why is not reviewable")
            continue
        if relative in allowed:
            problems.append(f"evidence-allowlist lists {relative} more than once")
            continue
        if not (REPO_ROOT / relative).exists():
            problems.append(
                f"evidence-allowlist names {relative}, which does not exist; an exemption "
                f"must not outlive the artifact it was written for")
            continue
        allowed[relative] = entry
    return allowed, problems


def file_problems(relative: str, path: Path,
                  generated_type_allowed: dict) -> tuple[list[str], bool]:
    """The hygiene policy's verdict on ONE file, and whether it carries working-tree CRLF.

    Extracted so the policy can be tested as a policy rather than only as a whole-repository
    verdict. F1's allowlist is a narrow exemption from exactly one rule, and the only way to
    show that it is narrow is to drive an allowlisted path through this function with
    prohibited content and observe that it is still rejected. A whole-repository PASS cannot
    demonstrate the absence of a bypass, because a bypass shows up as a PASS.
    """
    errors: list[str] = []
    normalized = relative.replace("\\", "/")
    suffix = path.suffix.casefold()
    if normalized.startswith(("tmp/", "output/")):
        errors.append(f"generated build path is tracked: {relative}")
    if suffix in GENERATED_SUFFIXES or suffix == ".pdf":
        # The ONLY rule the allowlist can suppress, and only for an exactly-named path.
        if normalized not in generated_type_allowed:
            errors.append(f"generated artifact type is tracked: {relative}")
    if "/" not in normalized and suffix == ".docx":
        errors.append(f"legacy DOCX remains at repository root: {relative}")
    if suffix not in TEXT_SUFFIXES or not path.exists():
        return errors, False

    text = path.read_text(encoding="utf-8", errors="replace")
    # Deliberately NOT gated on the allowlist. An allowlisted artifact is exempt from being
    # a generated type and from nothing else; if this scan were skipped for it, the allowlist
    # would have become a disclosure bypass, which is the failure mode the whole design is
    # arranged to prevent.
    for label, pattern in SENSITIVE_PATTERNS.items():
        match = pattern.search(text)
        if match:
            errors.append(f"{relative} contains {label}: {match.group(0)!r}")
    # The determinism gates read working-tree bytes, so local CRLF makes them report drift
    # that does not exist. Files a third-party tool owns are exempt here and covered by the
    # index check instead.
    if normalized.startswith(TOOL_OWNED_PERSISTENCE_PREFIXES):
        return errors, False
    return errors, b"\r\n" in path.read_bytes()


def git_paths(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args, "-z"], cwd=REPO_ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return [part.decode("utf-8") for part in result.stdout.split(b"\0") if part]


def index_eol_errors() -> list[str]:
    """Reject any tracked text file whose stored form is not LF.

    A fresh checkout receives whatever the index holds, filtered by .gitattributes.
    If the index carries CRLF or mixed endings, the determinism gates break for the
    next person to clone, which is the defect this whole control exists to prevent.
    """
    result = subprocess.run(
        ["git", "ls-files", "--eol", "-z"], cwd=REPO_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    offenders: list[str] = []
    for entry in result.stdout.decode("utf-8", errors="replace").split("\0"):
        if not entry.strip():
            continue
        fields = entry.split("\t", 1)
        if len(fields) != 2:
            continue
        attrs, relative = fields
        index_eol = next((part for part in attrs.split() if part.startswith("i/")), "")
        if index_eol in {"i/crlf", "i/mixed"}:
            offenders.append(f"{relative} ({index_eol})")
    if offenders:
        return [
            f"{len(offenders)} tracked text files are stored with non-LF endings "
            f"(first: {offenders[0]}); every fresh checkout would receive them and the "
            "byte-comparison gates would fail. Check .gitattributes."
        ]
    return []


def main() -> int:
    errors: list[str] = []
    crlf_paths: list[str] = []
    generated_type_allowed, allowlist_problems = load_generated_type_allowlist()
    errors.extend(allowlist_problems)
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
        found, carries_crlf = file_problems(relative, REPO_ROOT / relative,
                                            generated_type_allowed)
        errors.extend(found)
        if carries_crlf:
            crlf_paths.append(relative)

    if crlf_paths:
        errors.append(
            f"{len(crlf_paths)} controlled text files carry CRLF line endings in the "
            f"working tree (first: {crlf_paths[0]}); the byte-comparison gates read "
            "working-tree bytes and require LF."
        )

    # The invariant that actually matters: what git stores, and therefore what every
    # fresh checkout receives, is LF. This covers every tracked text file including
    # tool-owned persistence.
    errors.extend(index_eol_errors())

    if errors:
        print("ERROR: repository hygiene gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(tracked)} proposed tracked paths contain no build products, root DOCX "
        f"files, user-profile paths, or recognized secret material; "
        f"{len(generated_type_allowed)} retained evidence artifacts are individually exempt "
        f"from the generated-artifact-type rule only, and were disclosure-scanned like every "
        f"other file"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
