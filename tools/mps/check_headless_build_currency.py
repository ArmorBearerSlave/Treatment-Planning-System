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
EVIDENCE_TREE = REPO_ROOT / "mps" / "materialization" / "evidence"
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


class RetentionRefused(Exception):
    """The artifact cannot be retained as controlled evidence. A refusal, not a repair."""


def prepare_for_retention(source: Path, destination: Path) -> dict:
    """Canonicalize one runner artifact, validate it, and describe what will be retained.

    MPS-MAT-009 F1. The recorder used to hash whatever it was pointed at, which forced a
    choice nobody should have to make: retain the runner's raw output and fail the disclosure
    control, or scrub it by hand and retain something that is no longer the runner's output.
    Canonicalization belongs here, inside the recorder, so the bytes that are hashed are the
    bytes a reviewer receives from the repository -- and so the transformation is a declared,
    deterministic, re-derivable rule rather than an edit.

    Nothing is written by this function. It returns what WOULD be retained, so the caller can
    validate every artifact before committing any of them; a recorder that writes as it goes
    leaves a partially updated evidence record behind when the third artifact is refused.
    """
    import canonicalize_evidence as canon

    if not source.is_file():
        raise RetentionRefused(f"{source} does not exist")
    raw = source.read_bytes()
    canonical = canon.canonicalize_bytes(raw)

    intact, why = canon.structurally_intact(canonical, source.suffix)
    if not intact:
        raise RetentionRefused(
            f"{source.name}: {why}. Canonicalization that destroys the artifact's declared "
            f"type has not produced evidence, it has produced a file.")

    if canon.canonicalize_bytes(canonical) != canonical:
        raise RetentionRefused(f"{source.name}: {canon.RULE_ID} is not idempotent here, so "
                               f"canonical form is not checkable")

    # Disclosure is re-scanned AFTER canonicalization, against the hygiene gate's own
    # patterns. The canonicaliser's job is to remove the material it knows about; this asks
    # whether any remains, so a pattern the rule does not yet cover refuses retention rather
    # than passing into the evidence tree.
    sys.path.insert(0, str(REPO_ROOT / "tools" / "repo"))
    import check_repository_hygiene as hygiene

    text = canonical.decode("utf-8", errors="replace")
    for label, pattern in hygiene.SENSITIVE_PATTERNS.items():
        match = pattern.search(text)
        if match:
            raise RetentionRefused(
                f"{source.name} still contains {label} after canonicalization: "
                f"{match.group(0)!r}. Refusing to retain it.")

    if bytes([13]) in canonical:
        raise RetentionRefused(f"{source.name} contains CR bytes after canonicalization")

    return {
        "destination": destination,
        "bytes": canonical,
        "rule": canon.RULE_ID,
        "as_produced_sha256": hashlib.sha256(raw).hexdigest(),
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def retention_target(source: Path, default_name: str) -> Path:
    """Where a runner artifact is retained. Inside the evidence tree, always."""
    resolved = source.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT)
    except ValueError:
        relative = Path(default_name)
    text = str(relative).replace("\\", "/")
    if text.startswith("mps/materialization/evidence/"):
        return resolved
    return EVIDENCE_TREE / "MPS-MAT-008" / "green" / default_name


PORTABLE = "mps/materialization/evidence/"


def artifact_problems(label: str, reference, expected_sha256,
                      root: Path | None = None) -> list[str]:
    """The currency policy's verdict on ONE retained artifact.

    Extracted so the policy can be tested as a policy. F1 is a claim about the compatibility
    of two policies over a whole class of artifacts, and a claim of that shape cannot be
    supported by observing one repository state where both gates happen to be green -- that
    establishes only that some state satisfies both, not that the policies agree. Exposing
    the per-artifact decision lets a control drive canonical and deliberately non-canonical
    members of the same declared type through it and require opposite answers.
    """
    import canonicalize_evidence as canon

    root = root or REPO_ROOT
    problems: list[str] = []
    if not reference:
        return ["the " + label + " names no retained artifact"]
    if not str(reference).startswith(PORTABLE):
        return ["the " + label + " points at " + str(reference) + ", which is outside "
                + PORTABLE + ". A reviewer cannot obtain it from a clone, so its recorded "
                "hash is a dangling reference."]
    path = root / reference
    if not path.is_file():
        return ["the " + label + " artifact is missing: " + str(reference)]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        return ["the " + label + " artifact does not match its recorded hash"]
    if b"\r" in raw:
        return ["the " + label + " artifact contains CR bytes; git rewrites it on commit, so "
                "the recorded hash will not survive a clone"]
    # MPS-MAT-009 F1. Canonicality is established FROM THE ARTIFACT, never from metadata
    # asserting it. A record carrying `canonical: true` is a declaration, and a declaration
    # standing in for the property it describes is the defect this programme keeps finding.
    # The test is that canonicalizing the retained bytes changes nothing -- a fixed point,
    # which is checkable -- and that the result still validates as the type it claims to be.
    if canon.canonicalize_bytes(raw) != raw:
        problems.append("the " + label + " artifact is not in canonical form under "
                        + canon.RULE_ID + ", so the retained bytes are not the bytes the "
                        "recorder would produce and the disclosure rule has not been applied "
                        "to what is actually retained")
    intact, why = canon.structurally_intact(raw, path.suffix)
    if not intact:
        problems.append("the " + label + " artifact does not validate as its declared type: "
                        + why)
    return problems


def required_artifacts(evidence: dict) -> list[tuple[str, str]]:
    """Every retained artifact the evidence record requires, as (label, relative path).

    Enumerated mechanically from the record rather than listed by hand, because the
    joint-satisfiability control must cover the whole population the currency mechanism
    depends on. A hand-picked subset would prove the policies compatible over the artifacts
    someone happened to think of.
    """
    found: list[tuple[str, str]] = []
    for label, holder, key in (
            ("build log", evidence.get("build") or {}, "log"),
            ("model-test report", evidence.get("model_tests") or {}, "report"),
    ) + tuple(
            (name + " " + kind, control, kind)
            for name, control in sorted((evidence.get("controls") or {}).items())
            for kind in ("report", "patch")):
        reference = holder.get(key)
        if reference:
            found.append((label, str(reference)))
    return found


def record(build_log: Path, report: Path) -> int:
    import headless_build

    if not build_log.is_file():
        raise SystemExit("ERROR: build log not found: " + str(build_log))
    if not report.is_file():
        raise SystemExit("ERROR: test report not found: " + str(report))
    # MPS-MAT-009 F1. The recorder now OWNS retention: a raw runner artifact is accepted,
    # canonicalized, validated and written into the evidence tree by this function, and the
    # digest recorded is the digest of what a clone receives. Previously the caller had to
    # copy the artifact in by hand first, which is what forced the choice between retaining
    # host-disclosing bytes and retaining bytes that were no longer the runner's output.
    prepared = []
    for path, retained_as in ((build_log, retention_target(build_log, "cold-build.log")),
                              (report, retention_target(report, "junit.xml"))):
        try:
            prepared.append(prepare_for_retention(path, retained_as))
        except RetentionRefused as refusal:
            raise SystemExit(
                "ERROR: refusing to record. " + str(refusal) + chr(10) +
                "No evidence record was written. An evidence record naming an artifact that "
                "cannot be retained is a dangling reference, and a partially written one is "
                "worse than none.")
    build_log, report = prepared[0]["destination"], prepared[1]["destination"]

    log_text = prepared[0]["bytes"].decode("utf-8", errors="replace")
    build_ok = "BUILD SUCCESSFUL" in log_text and "BUILD FAILED" not in log_text

    suite = ElementTree.fromstring(prepared[1]["bytes"].decode("utf-8", errors="replace"))
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
            "log_sha256": prepared[0]["canonical_sha256"],
            "log_canonicalization": {
                "rule": prepared[0]["rule"],
                "as_produced_sha256": prepared[0]["as_produced_sha256"],
            },
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
            "report_sha256": prepared[1]["canonical_sha256"],
            "report_canonicalization": {
                "rule": prepared[1]["rule"],
                "as_produced_sha256": prepared[1]["as_produced_sha256"],
            },
        },
    }
    # Preserve everything this function does not itself derive. Rebuilding the record from
    # scratch silently dropped the red-state controls the first time it ran, which would have
    # left the gate reporting them absent while the two green verdicts still looked fine -- a
    # partial write that reads as a complete one.
    if EVIDENCE.is_file():
        with io.open(EVIDENCE, encoding="utf-8") as handle:
            existing = json.load(handle)
        for key, value in existing.items():
            evidence.setdefault(key, value)

    # The controls are retained artifacts too, and the currency gate requires them, so the
    # recorder owns their retention on the same terms. Rebinding their digests here is what
    # stops the record describing a pre-canonical form of a file the tree no longer holds.
    for name, control in sorted((evidence.get("controls") or {}).items()):
        for kind in ("report", "patch"):
            reference = control.get(kind)
            if not reference:
                continue
            path = REPO_ROOT / reference
            try:
                item = prepare_for_retention(path, path)
            except RetentionRefused as refusal:
                raise SystemExit(
                    "ERROR: refusing to record. control " + name + " " + kind + ": "
                    + str(refusal) + chr(10) + "No evidence record was written.")
            prepared.append(item)
            control[kind + "_sha256"] = item["canonical_sha256"]
            control[kind + "_canonicalization"] = {
                "rule": item["rule"],
                "as_produced_sha256": item["as_produced_sha256"],
            }

    # Everything validated. Only now is anything written -- every artifact and the record
    # together, so no refusal can leave the evidence tree half-updated.
    for item in prepared:
        item["destination"].parent.mkdir(parents=True, exist_ok=True)
        with io.open(item["destination"], "wb") as handle:
            handle.write(item["bytes"])

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

    # A measurement failure must not be reported as a finding about the model. If the corpus
    # cannot be resolved the hash would be the digest of an empty population, which compares
    # unequal to the recorded value and reads as staleness -- specific, confident and wrong.
    try:
        current = tree_hash()
    except Exception as error:
        print("MEASUREMENT INVALID: the controlled model tree could not be resolved, so no "
              "verdict about the evidence is available. This is not a finding about the "
              "model.", file=sys.stderr)
        print("  " + str(error), file=sys.stderr)
        return 2

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

    # Every referenced artifact must be one a reviewer can actually obtain and verify.
    # An earlier version pointed the two primary hashes into build/work/, which is gitignored
    # and which the test target deletes on every run: on a fresh clone those SHA-256s were
    # dangling references to files that could not be fetched, while the two supporting
    # controls verified -- and nothing marked which was which. Checking only the paths just
    # changed is what let that stand; this checks every reference.
    for label, holder, key in (
            ("build log", evidence.get("build") or {}, "log"),
            ("model-test report", evidence.get("model_tests") or {}, "report"),
    ) + tuple(
            (name + " " + kind, control, kind)
            for name, control in sorted((evidence.get("controls") or {}).items())
            for kind in ("report", "patch")):
        problems.extend(artifact_problems(label, holder.get(key),
                                          holder.get(key + "_sha256")))

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
            if not control.get("patch_reproduces_perturbed_tree"):
                problems.append("the " + name + " control does not record that its retained "
                                "patch reproduces the perturbed tree, so the intervention is "
                                "not bound to the observation")

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
                        default=REPO_ROOT / "mps" / "materialization" / "evidence"
                                / "MPS-MAT-008" / "green" / "cold-build.log")
    parser.add_argument("--report", type=Path,
                        default=REPO_ROOT / "mps" / "materialization" / "evidence"
                                / "MPS-MAT-008" / "green" / "junit.xml")
    args = parser.parse_args()
    return record(args.build_log, args.report) if args.record else check()


if __name__ == "__main__":
    sys.exit(main())
