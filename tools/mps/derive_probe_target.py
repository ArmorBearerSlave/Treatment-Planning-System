"""Derive the diagnostic probe's Ant element from the production one, or check it.

The recurring defect in this investigation has been divergence between the instrument and
the system it observes: a different worker base class, a different module population path,
a different call. Each was invisible until the one above it was removed, because from
inside a reconstruction the reconstruction looks like the real thing.

A probe element hand-copied from the production element is the same defect waiting to
happen -- the copy is correct on the day it is written and silently stops being correct the
first time the production element is edited. So it is not copied. It is derived, and
--check re-derives it and fails if the two have drifted. The permitted difference is
exactly three things: the task name, the worker class, and the probe jar.

This tool is diagnostic scaffolding for MPS-MAT-008. It does not touch the model.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_FILE = REPO_ROOT / "build" / "nltps-headless-build.xml"

PROBE_WORKER = "nltps.probe.ModuleClasspathProbe"
# The whole permitted difference between the two elements.
SUBSTITUTIONS = (
    ("<launchtests ",
     '<probelaunchtests worker="' + PROBE_WORKER + '" probeJar="${probe.jar}"\n'
     "                      "),
    ("</launchtests>", "</probelaunchtests>"),
)

PRODUCTION = re.compile(r"^  <target name=\"test\">\n(.*?)^  </target>\n",
                        re.MULTILINE | re.DOTALL)
PROBE = re.compile(r"^  <target name=\"probe\" depends=\"probe-compile\">\n(.*?)^  </target>\n",
                   re.MULTILINE | re.DOTALL)


def production_element(text: str) -> str:
    match = PRODUCTION.search(text)
    if match is None:
        raise SystemExit("ERROR: no <target name=\"test\"> in " + str(BUILD_FILE))
    body = match.group(1)
    start = body.index("<launchtests ")
    end = body.index("</launchtests>") + len("</launchtests>")
    return body[start:end]


def derive(element: str) -> str:
    derived = element
    for old, new in SUBSTITUTIONS:
        if old not in derived:
            raise SystemExit("ERROR: production element has no " + old.strip())
        derived = derived.replace(old, new)
    return derived


def probe_element(text: str) -> str | None:
    match = PROBE.search(text)
    if match is None:
        return None
    body = match.group(1)
    if "<probelaunchtests " not in body:
        return None
    start = body.index("<probelaunchtests ")
    end = body.index("</probelaunchtests>") + len("</probelaunchtests>")
    return body[start:end]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="verify the probe element is the derived one; change nothing")
    parser.add_argument("--write", action="store_true",
                        help="regenerate the probe element from the production one")
    args = parser.parse_args()

    with io.open(BUILD_FILE, encoding="utf-8") as handle:
        text = handle.read()

    expected = derive(production_element(text))
    actual = probe_element(text)

    if actual is None:
        print("SKIP: no probe target present; nothing to check", file=sys.stderr)
        return 0
    if args.write:
        if actual == expected:
            print("PASS: probe element already derived; nothing to write")
            return 0
        with io.open(BUILD_FILE, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text.replace(actual, expected))
        print("WROTE: probe element regenerated from the production element")
        return 0
    if actual != expected:
        print("FAIL: the probe element is not the production element with the three "
              "permitted substitutions applied. It has drifted, so any reading it "
              "produces describes a different execution.\n", file=sys.stderr)
        print("--- expected (derived)\n" + expected, file=sys.stderr)
        print("--- actual\n" + actual, file=sys.stderr)
        return 1
    lines = expected.count("\n") + 1
    print("PASS: probe element is derived from the production element; "
          f"{lines} lines identical apart from task name, worker and probe jar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
