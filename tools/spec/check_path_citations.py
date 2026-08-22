"""Every repository path cited in a controlled artifact must exist, or be declared absent.

The defect class is demonstrated, not hypothetical. build/nltps-headless-build.xml carried a
comment stating that tests/test_headless_build.py held the make module list equal to the
project's modules.xml. No such file existed, and four checkpoints closed with a reader
having no way to tell an enforced control from a described one.

A survey of the whole repository afterwards found the miss was isolated: of the distinct
paths cited across controlled artifacts, only two negative-control fixtures and one
declared-future gate were absent. That is a reassuring result and exactly the reason to
make the check permanent -- it is cheap now precisely because there is nothing to clean up.

The allowlist is the load-bearing half. Absent-because-deferred and absent-by-design are
legitimate, absent-because-nobody-noticed is not, and only a written status distinguishes
them. An entry must say which it is, so a gate cited as future work cannot sit cited and
missing indefinitely without someone having declared it.

What this does NOT check, stated so the gate is not read as stronger than it is: it
verifies that a cited file exists, never that a file which exists asserts what the citing
comment claims it asserts. A comment saying "tests/x.py holds A equal to B" passes here as
long as tests/x.py exists, whatever it actually tests. That second half is far more
expensive and is not attempted.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = REPO_ROOT / "spec" / "path_citation_allowlist.yaml"

# Controlled artifacts only. The MPS project itself is written by MPS and is not a place
# where a human writes a claim about coverage.
SCAN = (
    ("tools", ("*.py",)),
    ("tests", ("*.py",)),
    ("spec", ("*.yaml", "*.yml")),
    ("build", ("*.xml",)),
    (".github", ("*.yml", "*.yaml")),
    ("mps/materialization", ("*.yaml",)),
    ("mps/bootstrap", ("*.yaml", "*.json")),
)
EXTRA_FILES = ("CLAUDE.md",)

TOP_LEVEL = "tools|tests|spec|build|scripts|mps|docs"
EXTENSIONS = "py|yaml|yml|json|xml|md|csv|txt|msd|mpl|mps|mpsr|devkit"
CITATION = re.compile(r"(?<![\w./-])((?:" + TOP_LEVEL + r")/[A-Za-z0-9_@.+-]+"
                      r"(?:/[A-Za-z0-9_@.+-]+)*\.(?:" + EXTENSIONS + r"))(?![\w-])")
# Glob-ish citations describe a family, not a file, and are not resolvable.
GLOBBY = re.compile(r"[*?{}\[\]]|/\.\.")


def allowlist() -> dict[str, dict]:
    if not ALLOWLIST.is_file():
        return {}
    import yaml

    with io.open(ALLOWLIST, encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle.read()) or {}
    return {entry["path"]: entry for entry in loaded.get("absent_by_declaration", [])}


def scanned_files() -> list[Path]:
    found = []
    for folder, patterns in SCAN:
        base = REPO_ROOT / folder
        if not base.is_dir():
            continue
        for pattern in patterns:
            found.extend(p for p in base.rglob(pattern) if "__pycache__" not in p.parts)
    found.extend(REPO_ROOT / name for name in EXTRA_FILES
                 if (REPO_ROOT / name).is_file())
    return sorted(set(found))


def citations() -> dict[str, set[str]]:
    """Cited path -> the artifacts citing it."""
    cited: dict[str, set[str]] = {}
    for path in scanned_files():
        if path == ALLOWLIST or path.name == Path(__file__).name:
            continue
        with io.open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        for match in CITATION.finditer(text):
            value = match.group(1)
            if GLOBBY.search(value):
                continue
            cited.setdefault(value, set()).add(
                str(path.relative_to(REPO_ROOT)).replace("\\", "/"))
    return cited


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="print every citation found")
    args = parser.parse_args()

    declared = allowlist()
    cited = citations()
    missing, stale = [], []

    for value, citers in sorted(cited.items()):
        exists = (REPO_ROOT / value).exists()
        if args.list:
            print(f"{'ok ' if exists else 'MISSING'} {value}")
        if exists:
            continue
        entry = declared.get(value)
        if entry is None:
            missing.append((value, sorted(citers)))

    for value, entry in sorted(declared.items()):
        if (REPO_ROOT / value).exists():
            stale.append((value, entry.get("status", "?")))

    if missing or stale:
        print("FAIL: path citations\n", file=sys.stderr)
        for value, citers in missing:
            print(f"  - {value} does not exist; cited by {', '.join(citers)}.\n"
                  f"    Either create it, correct the citation, or declare it in "
                  f"{ALLOWLIST.relative_to(REPO_ROOT)} with a status.\n", file=sys.stderr)
        for value, status in stale:
            print(f"  - {value} is declared absent ({status}) but now exists. Remove the "
                  f"allowlist entry so the declaration cannot outlive its reason.\n",
                  file=sys.stderr)
        return 1

    print(f"PASS: {len(cited)} distinct paths cited across controlled artifacts; "
          f"all resolve, except {len(declared)} declared absent with a recorded status. "
          f"Existence only -- this does not verify that a cited file asserts what the "
          f"citing text claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
