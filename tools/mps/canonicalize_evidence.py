#!/usr/bin/env python3
"""Put a retained execution artifact into canonical form, by a declared deterministic rule.

MPS-MAT-009 F1. Two controls were each correct and jointly unsatisfiable: the currency gate
requires the verbatim runner artifacts to be retained under mps/materialization/evidence/
with matching hashes, and the hygiene gate rejects those same artifacts because a JUnit
report carries the whole system-property dump, including the host's user-profile paths.
Satisfying either entailed failing the other, and the reviewer correctly refused to choose:
scrubbing changes the hashes so the artifact is no longer the runner's output, and exempting
the evidence tree narrows a disclosure control.

The way out is neither. The artifact is transformed by a rule that is DECLARED, so the
transformation is auditable; DETERMINISTIC, so anyone holding the runner's output can
re-derive the retained form and confirm it; and IDEMPOTENT, so canonical form is a fixed
point that can be checked rather than asserted. The record then carries both digests --
what the runner emitted and what is retained -- so the retained artifact is provably a
declared derivation rather than an edited one.

What the rule removes is exactly the host-identifying path material the disclosure control
names, and nothing else. It does not touch test counts, identities, assertion text,
outcomes, timings or the build verdict, because those are the evidence.

What the rule deliberately KEEPS is the hostname. It is host-specific, but it is not a
pattern the disclosure control names, and it is load-bearing evidence: the review's
limitation L2 -- that every execution ran on the same machine that produced the original
evidence -- is only checkable because the hostname survives in the reports. Normalising it
would destroy the reader's ability to detect single-host dependence, which is a real
limitation of the package. Removing disclosure and removing evidence are different
operations and this rule performs only the first.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

RULE_ID = "evidence_canonicalization/v1"

# Ordered, and the order is part of the rule. Each pattern is anchored on the same shape the
# hygiene gate's disclosure patterns detect, widened only where the gate's own character
# class would stop early: a Windows 8.3 short name such as ERIC~1.BRA contains a tilde, so
# the gate matches a prefix of it while the canonicaliser must consume the whole segment.
# The placeholders carry no XML metacharacters, and that is a correctness requirement rather
# than a style choice. The first draft of this rule substituted <USERPROFILE>, which is a
# perfectly readable placeholder and which silently destroyed every artifact it touched: the
# JUnit reports carry these paths inside attribute values, so injecting a raw angle bracket
# produced a well-formed-looking file that no XML parser would read. The canonicaliser
# reported success. Nothing else would have noticed until a consumer tried to parse the
# retained evidence, which is exactly the class of defect this programme keeps finding --
# a tool's own report of success standing in for the property it claims.
SUBSTITUTIONS = (
    ("windows_user_profile",
     re.compile(r"(?i)[A-Z]:[\\/]Users[\\/][A-Za-z0-9._~-]+"),
     "%USERPROFILE%"),
    ("unix_home",
     re.compile(r"/home/[A-Za-z0-9._-]+"),
     "%HOME%"),
)


class NotCanonical(Exception):
    """The artifact is not in canonical form. A refusal, not a repair."""


def canonicalize_text(text: str) -> str:
    """Apply the declared rule. Idempotent by construction: the replacements introduce no
    text that any pattern matches, so a second application is a no-op."""
    for _, pattern, replacement in SUBSTITUTIONS:
        text = pattern.sub(replacement, text)
    # LF, because the retained-artifact rule requires the recorded hash to survive a clone
    # and git rewrites CR bytes on commit.
    return text.replace("\r\n", "\n").replace("\r", "\n")


def canonicalize_bytes(raw: bytes) -> bytes:
    return canonicalize_text(raw.decode("utf-8", errors="replace")).encode("utf-8")


def is_canonical(raw: bytes) -> bool:
    return canonicalize_bytes(raw) == raw


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def structurally_intact(raw: bytes, suffix: str) -> tuple[bool, str]:
    """Whether the canonical form is still readable as what it claims to be.

    A canonicaliser that removes disclosure and leaves an unparseable artifact has not
    produced evidence, it has produced a file. This is checked rather than trusted because
    the first version of this rule did exactly that and reported success.
    """
    if suffix.casefold() in {".xml"}:
        from xml.etree import ElementTree
        try:
            ElementTree.fromstring(raw.decode("utf-8", errors="replace"))
        except ElementTree.ParseError as error:
            return False, f"not well-formed XML after canonicalization: {error}"
    if suffix.casefold() in {".json"}:
        import json as _json
        try:
            _json.loads(raw.decode("utf-8", errors="replace"))
        except ValueError as error:
            return False, f"not valid JSON after canonicalization: {error}"
    return True, ""


def canonicalize_file(source: Path, destination: Path) -> dict:
    raw = source.read_bytes()
    canonical = canonicalize_bytes(raw)
    intact, why = structurally_intact(canonical, source.suffix)
    if not intact:
        raise NotCanonical(f"{source}: {why}")
    if canonicalize_bytes(canonical) != canonical:
        # Cannot happen with the current rule, and is checked anyway: a non-idempotent rule
        # would make "canonical form" unverifiable, since the check itself would depend on
        # how many times the rule had been applied.
        raise NotCanonical(f"{RULE_ID} is not idempotent on {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(canonical)
    removed = {
        name: len(set(pattern.findall(raw.decode("utf-8", errors="replace"))))
        for name, pattern, _ in SUBSTITUTIONS
    }
    return {
        "rule": RULE_ID,
        "as_produced_sha256": sha256(raw),
        "canonical_sha256": sha256(canonical),
        "as_produced_bytes": len(raw),
        "canonical_bytes": len(canonical),
        "distinct_matches_replaced": {k: v for k, v in removed.items() if v},
        "already_canonical": raw == canonical,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path, nargs="?")
    parser.add_argument("--check", action="store_true",
                        help="report whether the file is already in canonical form")
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"MEASUREMENT INVALID: {args.source} is not a file", file=sys.stderr)
        return 2

    if args.check:
        raw = args.source.read_bytes()
        if is_canonical(raw):
            print(f"PASS: {args.source} is in canonical form under {RULE_ID} "
                  f"(sha256 {sha256(raw)[:16]})")
            return 0
        print(f"FAIL: {args.source} is not in canonical form under {RULE_ID}",
              file=sys.stderr)
        return 1

    if args.destination is None:
        print("ERROR: a destination is required unless --check is given", file=sys.stderr)
        return 2

    result = canonicalize_file(args.source, args.destination)
    print(f"{RULE_ID}: {args.source.name} -> {args.destination}")
    print(f"  as produced sha256 {result['as_produced_sha256']}")
    print(f"  canonical   sha256 {result['canonical_sha256']}")
    print(f"  replaced           {result['distinct_matches_replaced'] or 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
