"""Two coverage controls on the headless build descriptor.

The build descriptor has always claimed the first of these in prose -- "the list is the
build's statement of coverage, and tests/test_headless_build.py holds it equal to the
project's own modules.xml". That test did not exist. A control described in a comment and
never written is worse than no control, because a reader has no way to tell the difference
and will reasonably assume coverage is enforced.

The second control comes from the defect recorded at 875fcee. nltps.modeltests declared a
dependency on nltps.proof, nothing supplied nltps.proof to the launchtests worker, the
dependency failed to resolve, ClassLoaderManager reported NOT_IN_REPO for nltps.modeltests
itself and handed test discovery a system-delegating classloader that could not see
classes_gen. The symptom was a ClassNotFoundException naming the test class, which pointed
at everything except the cause. Nothing about that failure was specific to nltps.proof:
any later project-local dependency added to a test module recreates it under a different
name, with the same misleading symptom.

So this checks that the project-local dependency closure of every module offered for test
discovery is actually supplied to the worker -- through <repository> or <testmodules> --
rather than left to resolve by luck.

Neither control says anything about clinical correctness, and passing proves only that the
descriptor is internally consistent with the project.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_FILE = REPO_ROOT / "build" / "nltps-headless-build.xml"
PROJECT_DIR = REPO_ROOT / "mps" / "NLTPSGovernance"
MODULES_XML = PROJECT_DIR / ".mps" / "modules.xml"

DESCRIPTOR_SUFFIXES = (".msd", ".mpl", ".devkit")
# 4745dc6f-8462-405d-b92b-cf0ea82dac23(nltps.proof) -> nltps.proof
DEPENDENCY = re.compile(r"\(([^)]+)\)\s*$")


def _target(name: str):
    root = ElementTree.parse(BUILD_FILE).getroot()
    found = [t for t in root.iter("target") if t.get("name") == name]
    if len(found) != 1:
        raise SystemExit(f"ERROR: expected exactly one target named {name!r}, "
                         f"found {len(found)}")
    return found[0]


def make_modules() -> list[str]:
    return [Path(e.get("file")).name for e in _target("make").iter("module")
            if e.get("file")]


def project_modules() -> dict[str, str]:
    """Module name -> descriptor file name, from the project's own registry."""
    root = ElementTree.parse(MODULES_XML).getroot()
    modules = {}
    for element in root.iter("modulePath"):
        path = element.get("path")
        if not path:
            continue
        name = Path(path).name
        modules[Path(name).stem] = name
    return modules


def supplied_to_worker() -> tuple[set[str], set[str]]:
    """(repository modules, test modules) named in the test target, by file name."""
    target = _target("test")
    repository = {Path(e.get("file")).name
                  for r in target.iter("repository") for e in r.iter("module")
                  if e.get("file")}
    tests = set()
    for element in target.iter("testmodules"):
        for fileset in element.iter("fileset"):
            value = fileset.get("file")
            if value:
                tests.add(Path(value).name)
    return repository, tests


def declared_dependencies(descriptor: Path) -> list[str]:
    """Project-local dependency names declared by a module descriptor."""
    with io.open(descriptor, encoding="utf-8") as handle:
        text = handle.read()
    names = []
    for block in re.findall(r"<dependencies>(.*?)</dependencies>", text, re.DOTALL):
        for raw in re.findall(r"<dependency[^>]*>([^<]+)</dependency>", block):
            match = DEPENDENCY.search(raw.strip())
            if match:
                names.append(match.group(1))
    return names


def main() -> int:
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter
                            ).parse_args()
    failures = []

    declared = make_modules()
    project = project_modules()
    if sorted(declared) != sorted(project.values()):
        failures.append(
            "the make target does not cover the project.\n"
            f"  only in make:        {sorted(set(declared) - set(project.values()))}\n"
            f"  only in modules.xml: {sorted(set(project.values()) - set(declared))}")
    if len(declared) != len(set(declared)):
        failures.append(f"the make target names a module more than once: {declared}")

    repository, tests = supplied_to_worker()
    supplied = repository | tests
    for test_module in sorted(tests):
        descriptor = next((p for p in PROJECT_DIR.rglob(test_module)), None)
        if descriptor is None:
            failures.append(f"test module descriptor not found in project: {test_module}")
            continue
        for dependency in declared_dependencies(descriptor):
            if dependency not in project:
                continue  # not project-local; MPS supplies it
            expected = project[dependency]
            if expected not in supplied:
                failures.append(
                    f"{test_module} declares a project-local dependency on {dependency}, "
                    f"but {expected} is supplied to the worker neither through <repository> "
                    f"nor <testmodules>. At discovery time that dependency will not resolve, "
                    f"ClassLoaderManager will report NOT_IN_REPO for {test_module}, and test "
                    f"discovery will be handed a system-delegating classloader that cannot "
                    f"see classes_gen. The symptom is a ClassNotFoundException naming the "
                    f"test class, which points at everything except this.")

    if failures:
        print("FAIL: headless build coverage\n", file=sys.stderr)
        for failure in failures:
            print("  - " + failure + "\n", file=sys.stderr)
        return 1

    print(f"PASS: make covers all {len(declared)} project modules; "
          f"project-local dependency closure of {len(tests)} test module(s) is supplied "
          f"({len(repository)} via <repository>, {len(tests)} via <testmodules>)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
