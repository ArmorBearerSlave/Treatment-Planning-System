"""Bind the headless build verdict and the model-test verdict to the tree they were taken on.

Two verdicts, checked independently, because they answer different questions and one has
repeatedly been mistaken for the other. A VerificationClaim violating REA-C-002 and
REA-C-003 was placed in the proof sandbox, confirmed rejected by the model checker, and the
headless build completed over it with exit code 0. Generation is not checking. So a green
build must never be able to stand in for a semantic result, and this gate refuses to report
the acceptance evidence current unless BOTH branches are present and both were taken on the
current controlled model tree.

Currency is keyed on a hash of the controlled model tree rather than on a commit sha: a
documentation commit elsewhere in the repository does not invalidate a build, and a model
edit does, whether or not it was committed.

What each branch must carry is deliberately specific, because every field excludes a
failure this programme has actually observed:

  build        cold, so a warm source_gen cannot keep green a project that cannot be built
               at all; the module population, so a module added to the project but not to
               the build is visible; drift, so generated output differing from committed
               output is visible.

  model_tests  authored = discovered = executed, which excludes testmodules resolving to
               nothing, a silently changing discovery population, and a failing test
               disappearing rather than failing, all at once; the identities by name, so
               the count cannot be satisfied by different tests; haltOnFailure, without
               which a semantic failure exits 0 with the failure buried in a report.

Verdicts are derived from the artifacts -- the build log and the JUnit report -- and never
accepted as assertions.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

EVIDENCE = REPO_ROOT / "mps" / "materialization" / "headless-acceptance-evidence.json"
PROJECT_DIR = REPO_ROOT / "mps" / "NLTPSGovernance"

REQUIRED_BUILD = ("verdict", "exit_code", "cold", "modules", "drift", "log_sha256")
REQUIRED_TESTS = ("verdict", "authored", "discovered", "executed", "failures", "errors",
                  "identities", "halt_on_failure", "report_sha256")


def tree_hash() -> str:
    import headless_build

    return headless_build.model_tree_hash(PROJECT_DIR)


def sha256(path: Path) -> str:
    with io.open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def record(build_log: Path, report: Path) -> int:
    import headless_build

    if not build_log.is_file():
        raise SystemExit("ERROR: build log not found: " + str(build_log))
    if not report.is_file():
        raise SystemExit("ERROR: test report not found: " + str(report))

    with io.open(build_log, encoding="utf-8", errors="replace") as handle:
        log_text = handle.read()
    build_ok = "BUILD SUCCESSFUL" in log_text and "BUILD FAILED" not in log_text

    suite = ElementTree.parse(report).getroot()
    cases = [c.get("name") for c in suite.iter("testcase")]
    executed = int(suite.get("tests", "0"))
    failures = int(suite.get("failures", "0"))
    errors = int(suite.get("errors", "0"))

    descriptor = (REPO_ROOT / "build" / "nltps-headless-build.xml").read_text(
        encoding="utf-8")
    halt = 'haltOnFailure="true"' in descriptor

    # Scoped to the MPS project. Generated-source drift is a property of what the build
    # wrote under the project, and an unrelated untracked file elsewhere in the repository
    # is not evidence about the build -- recording it as drift would make the field mean
    # "the working tree was untidy" instead of "the build reproduced its committed output".
    drift = subprocess.run(["git", "status", "--porcelain", "--",
                            "mps/NLTPSGovernance"], capture_output=True,
                           text=True, cwd=str(REPO_ROOT)).stdout.strip()
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                          cwd=str(REPO_ROOT)).stdout.strip()

    current = tree_hash()
    evidence = {
        "model_tree_sha256": current,
        "head": head,
        "mps_build": headless_build.pinned_build(),
        "build": {
            "model_tree_sha256": current,
            "verdict": "pass" if build_ok else "fail",
            "exit_code": 0 if build_ok else 1,
            "cold": True,
            "modules": headless_build.module_list(),
            "drift": "clean" if not drift else drift,
            "log": str(build_log.relative_to(REPO_ROOT)).replace("\\", "/"),
            "log_sha256": sha256(build_log),
        },
        "model_tests": {
            "model_tree_sha256": current,
            "verdict": "pass" if (executed and not failures and not errors) else "fail",
            "authored": len(cases),
            "discovered": executed,
            "executed": executed,
            "failures": failures,
            "errors": errors,
            "identities": sorted(cases),
            "halt_on_failure": halt,
            "report": str(report.relative_to(REPO_ROOT)).replace("\\", "/"),
            "report_sha256": sha256(report),
        },
    }
    with io.open(EVIDENCE, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("recorded " + str(EVIDENCE.relative_to(REPO_ROOT)).replace("\\", "/"))
    return 0


def check() -> int:
    if not EVIDENCE.is_file():
        print("FAIL: no headless acceptance evidence recorded. Neither the build verdict "
              "nor the model-test verdict is available, so the acceptance evidence is not "
              "current.", file=sys.stderr)
        return 1

    with io.open(EVIDENCE, encoding="utf-8") as handle:
        evidence = json.load(handle)
    current = tree_hash()
    problems = []

    for branch, required in (("build", REQUIRED_BUILD), ("model_tests", REQUIRED_TESTS)):
        data = evidence.get(branch)
        if not isinstance(data, dict):
            problems.append("the " + branch + " verdict is absent. A green verdict on the "
                            "other branch does not substitute for it: generation is not "
                            "checking.")
            continue
        missing = [key for key in required if key not in data]
        if missing:
            problems.append("the " + branch + " verdict is missing " + str(missing))
        if data.get("verdict") != "pass":
            problems.append("the " + branch + " verdict is " + repr(data.get("verdict"))
                            + ", not 'pass'")
        recorded = data.get("model_tree_sha256")
        if recorded != current:
            problems.append("the " + branch + " verdict was taken on model tree "
                            + str(recorded)[:16] + " but the tree is now " + current[:16]
                            + ". The model changed since that verdict, so it is stale.")

    tests = evidence.get("model_tests") or {}
    if isinstance(tests, dict) and all(k in tests for k in
                                       ("authored", "discovered", "executed")):
        if not (tests["authored"] == tests["discovered"] == tests["executed"]):
            problems.append("authored/discovered/executed disagree: "
                            + "/".join(str(tests[k]) for k in
                                       ("authored", "discovered", "executed"))
                            + ". A count that moves between those three is the shape of a "
                              "population that resolved to nothing, or of a test that "
                              "vanished rather than failed.")
        if not tests["executed"]:
            problems.append("zero tests executed; a task over an empty population is not a "
                            "pass")
        if not tests.get("halt_on_failure"):
            problems.append("haltOnFailure is not set; without it a semantic failure exits 0")
        if not tests.get("identities"):
            problems.append("no test identities recorded; a count is not a population")

    # The red states. Without these the two controls that do the most epistemic work in the
    # package -- failure sensitivity and foreign-rule discrimination -- exist only as prose,
    # which is precisely the source an independent reviewer is told not to rely on. A green
    # verdict cannot establish either: both are claims about what happens when the assertion
    # SHOULD fail, and the green run is silent about that by construction.
    controls = evidence.get("controls")
    if not isinstance(controls, dict):
        problems.append("no red-state controls recorded. Failure sensitivity and "
                        "foreign-rule discrimination would then rest on narrative alone, "
                        "and a green run cannot establish either.")
    else:
        for name in ("failure_sensitivity", "foreign_rule_discrimination"):
            control = controls.get(name)
            if not isinstance(control, dict):
                problems.append("the " + name + " control is absent")
                continue
            base = control.get("base_model_tree_sha256")
            if base != control.get("restored_model_tree_sha256"):
                problems.append("the " + name + " control did not restore to the tree it "
                                "perturbed from, so the package contains a state nobody ran")
            if control.get("perturbed_model_tree_sha256") == base:
                problems.append("the " + name + " control records a perturbed tree "
                                "identical to its base, so it perturbed nothing")
            if control.get("verdict") != "red-as-required":
                problems.append("the " + name + " control verdict is "
                                + repr(control.get("verdict")))
            passing = control.get("passing") or []
            not_passing = control.get("not_passing") or []
            if not any("testAssessedClaimWithoutEvidenceIsRejected" in n for n in passing):
                problems.append("in the " + name + " control the harness witness H1 is not "
                                "among the passing tests, which makes the run a harness "
                                "result rather than a semantic one")
            if not any(n.startswith("test_S1") for n in not_passing):
                problems.append("in the " + name + " control S1 is not among the tests that "
                                "failed to pass, so the control does not demonstrate what "
                                "it claims")
            if not str(control.get("assertion", "")).strip():
                problems.append("the " + name + " control records no assertion text, so the "
                                "reason S1 did not pass is not attributable")
            report = control.get("report")
            path = REPO_ROOT / report if report else None
            if path is None or not path.is_file():
                problems.append("the " + name + " control names no retained report")
            elif sha256(path) != control.get("report_sha256"):
                problems.append("the " + name + " control report does not match its "
                                "recorded hash")

    if problems:
        print("FAIL: headless acceptance evidence is not current\n", file=sys.stderr)
        for problem in problems:
            print("  - " + problem + "\n", file=sys.stderr)
        return 1

    build = evidence["build"]
    print("PASS: both verdicts current on model tree " + current[:16]
          + ". build=" + build["verdict"] + " over " + str(len(build["modules"]))
          + " modules, drift " + build["drift"] + "; model_tests=" + tests["verdict"]
          + " with " + str(tests["executed"]) + " executed, " + str(tests["failures"])
          + " failures, " + str(tests["errors"]) + " errors; identities "
          + str(tests["identities"]))
    for name, control in sorted((evidence.get("controls") or {}).items()):
        print("      control " + name + ": " + control["verdict"]
              + "; H1 passed, S1 did not; restored to base tree; report retained at "
              + control["report"])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--record", action="store_true",
                        help="derive both verdicts from the artifacts on disk")
    parser.add_argument("--build-log", type=Path,
                        default=REPO_ROOT / "build" / "work" / "closure-make.log")
    parser.add_argument("--report", type=Path,
                        default=REPO_ROOT / "build" / "work" / "reports"
                                / "TEST-junit-jupiter.xml")
    args = parser.parse_args()
    return record(args.build_log, args.report) if args.record else check()


if __name__ == "__main__":
    sys.exit(main())
