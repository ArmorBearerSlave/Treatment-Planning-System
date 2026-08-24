"""NF-21, NF-24, NF-25. Every mandatory structural-gates control must still execute.

GitHub Actions stops a job at its first failing step. A control that stands substantively
nonzero -- one whose RED is the correct answer and is expected to persist -- therefore strands
every mandatory control positioned behind it. The evidence reconciler is exactly that: exit 1,
seven declared evidence obligations still OPEN. It ran thirteenth of thirty-four, and the
twenty-one steps after it had never executed in CI for as long as that RED had stood. They did
not fail; CI established nothing about them, while presenting their absence in the same shape
as their success. That is NF-21, repaired at C8B by moving the reconciler last.

NF-24. The observer written to hold that property asked the wrong question. It treated the
PRESENCE of `continue-on-error` or `if` on a step as proof that execution survives an earlier
failure. Neither key means that, and the two do not even answer the same question:

    continue-on-error   is about whether THIS step's own failure stops the job
    if                  is about whether THIS step runs at all

`if: success()` is the default condition and does not run after an earlier failure.
`continue-on-error: false` is the default value and tolerates nothing. Writing either -- that
is, writing down what the platform already does -- silently emptied the observer's stranded
population. With `if: success()` on all twenty-one downstream steps of the historical topology,
it reported no reachability problem at all. A maintainer could reintroduce the defect while
believing they had made the workflow more explicit.

So the predicate here is not "does the step declare an execution-control key". It is:

    will this step still execute after the known preceding substantive failure?

answered by VALUE over a conservative recognised subset, with everything outside that subset
returning UNRESOLVED rather than PASS. An observer that cannot establish a measurement must say
so; silently passing is the failure mode this register keeps finding.

NF-25. The claim is scoped to structural-gates, which is the population this observer enforces.
The earlier wording said "every mandatory control in the controlled workflow" while evaluating
one job, and the workflow also declares document-build. That job carries no mandatory control:
its two commands are producers with no check mode, spec/readiness.yaml cites them as evidence
that the tools exist rather than that CI runs them, no gate reads their output, and its product
is residualised there as not a governed release. Its non-execution is therefore not a
reachability defect -- but the claim was still overbroad, so it is narrowed here and a control
fails if a job outside this scope ever acquires something control-shaped.
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "controlled-spec-gates.yml"

ENFORCED_JOB = "structural-gates"

# Three-valued, because "cannot establish" is a real answer and must not be spelled as PASS.
PRESERVED, NOT_PRESERVED, UNRESOLVED = "PRESERVED", "NOT_PRESERVED", "UNRESOLVED"

# The `if` conditions whose meaning is recognised. Deliberately a small closed set: a general
# GitHub Actions expression evaluator would be a second implementation of somebody else's
# semantics, and every form outside this set is reported unresolved rather than assumed.
RUNS_AFTER_EARLIER_FAILURE = {"always()", "failure()", "!cancelled()"}
DOES_NOT_RUN_AFTER_EARLIER_FAILURE = {"success()", "cancelled()"}

DYNAMIC = re.compile(r"\$\{\{")


def workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def runs_after_earlier_failure(step: dict) -> str:
    """Whether this step still executes once an earlier step in the job has failed.

    Governed by `if` alone. `continue-on-error` is not consulted here: it says what happens to
    the job when THIS step fails, which is a different question, and conflating the two is
    half of NF-24.
    """
    if "if" not in step:
        return NOT_PRESERVED                      # default is success()
    condition = step["if"]
    if not isinstance(condition, str):
        return UNRESOLVED
    text = condition.strip()
    if DYNAMIC.search(text):
        return UNRESOLVED
    if text in RUNS_AFTER_EARLIER_FAILURE:
        return PRESERVED
    if text in DOES_NOT_RUN_AFTER_EARLIER_FAILURE:
        return NOT_PRESERVED
    return UNRESOLVED


def failure_is_tolerated(step: dict) -> str:
    """Whether this step failing leaves the job running, so later steps still execute.

    Governed by `continue-on-error` alone, and by its VALUE. Absent means false, and an
    explicit false means false; only a literal true tolerates the failure. A dynamic
    expression is unresolved, never assumed safe.
    """
    if "continue-on-error" not in step:
        return NOT_PRESERVED
    value = step["continue-on-error"]
    if isinstance(value, bool):
        return PRESERVED if value else NOT_PRESERVED
    if isinstance(value, str) and DYNAMIC.search(value):
        return UNRESOLVED
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        return PRESERVED if value.strip().lower() == "true" else NOT_PRESERVED
    return UNRESOLVED


def looks_like_a_control(command: str) -> bool:
    """Whether a command is a control, by the repository's own naming and flag conventions.

    Derived rather than listed: a check flag in either the POSIX or PowerShell spelling, a
    tool whose basename begins with check_, the regression suite, or the terminal cleanliness
    diff. Used to answer NF-25's scope question mechanically instead of by assertion.
    """
    if "--check" in command or "-Check" in command:
        return True
    if "unittest discover" in command:
        return True
    if command.strip().startswith("git diff --exit-code"):
        return True
    match = re.search(r"([\w]+)\.py\b", command)
    return bool(match and match.group(1).startswith("check_"))


def control_steps(job: str = ENFORCED_JOB) -> list[dict]:
    """The ordered steps of a job that run something, excluding environment setup."""
    steps = workflow()["jobs"][job]["steps"]
    out = []
    for position, step in enumerate(steps, start=1):
        run = step.get("run")
        if not run:
            continue
        if re.search(r"pip install|apt-get", str(run)):
            continue
        out.append({"position": position, "name": step.get("name", "<unnamed>"),
                    "run": run.strip(), "step": step})
    return out


def commands(step: dict) -> list[str]:
    return [line.strip() for line in step["run"].splitlines() if line.strip()]


_EXIT_CODES: dict = {}


def run_control(command: str) -> int:
    """Execute one control and return its exit code.

    Memoised within a run, keyed on the command AND the current workflow bytes. The controls
    are a property of the repository state rather than of the topology, so re-running
    twenty-eight of them for every question is waste -- but the mutation controls rewrite the
    workflow and at least one control scans repository files, so the workflow content is part
    of the key rather than assumed irrelevant.
    """
    key = (command, WORKFLOW.read_bytes())
    if key not in _EXIT_CODES:
        argv = [sys.executable, *command.split()[1:]] if command.startswith("python ") \
            else command.split()
        _EXIT_CODES[key] = subprocess.run(argv, capture_output=True, text=True,
                                          cwd=str(REPO_ROOT)).returncode
    return _EXIT_CODES[key]


def standing_nonzero_controls() -> list[dict]:
    """Controls nonzero in the repository's current state, established by executing them.

    Derived rather than declared. Naming which control is red would make this agree with a
    list instead of with the repository, and the two agree until they do not.
    """
    nonzero = []
    for step in control_steps():
        for command in commands(step):
            if "unittest discover" in command or not command.startswith("python tools/"):
                continue
            if run_control(command) != 0:
                nonzero.append({**step, "command": command})
                break
    return nonzero


def unresolved_measurements() -> list[str]:
    """Steps whose execution semantics this observer cannot establish.

    NF-24 and section 32. These are neither PASS nor FAIL: they are the observer saying its
    supported subset does not cover what the workflow declares. Reported separately so an
    unsupported form cannot arrive as a quiet pass.
    """
    out = []
    for step in control_steps():
        for label, verdict in (("if", runs_after_earlier_failure(step["step"])),
                               ("continue-on-error", failure_is_tolerated(step["step"]))):
            if verdict != UNRESOLVED:
                continue
            if label not in step["step"]:
                continue
            out.append(f"step {step['position']} ({step['name']!r}): {label} is "
                       f"{step['step'][label]!r}, which is outside the recognised semantics; "
                       f"the measurement is unresolved, not a pass")
    return out


def reachability_problems() -> list[str]:
    """No mandatory control may sit behind a standing-nonzero step that stops the job.

    Two independent ways a later step survives, and they are asked of different steps:
    the blocker's own failure may be tolerated, or the later step may declare that it runs
    regardless. UNRESOLVED counts as stranded here and is also reported by
    unresolved_measurements, so an unsupported form fails closed in both directions.
    """
    steps = control_steps()
    problems = []
    for blocker in standing_nonzero_controls():
        if failure_is_tolerated(blocker["step"]) == PRESERVED:
            continue
        stranded = [s for s in steps
                    if s["position"] > blocker["position"]
                    and runs_after_earlier_failure(s["step"]) != PRESERVED]
        if stranded:
            problems.append(
                f"step {blocker['position']} ({blocker['name']!r}) exits nonzero and its "
                f"failure is not tolerated, so {len(stranded)} later mandatory control(s) do "
                f"not execute, beginning with {stranded[0]['position']} "
                f"({stranded[0]['name']!r})")
    return problems


# Control CLASSES required to be reachable, named by the tool implementing each, so the
# assertion is about what must run rather than about how many steps there happen to be.
REQUIRED_REACHABLE = {
    "module graph": "check_module_graph.py",
    "enum persistence": "check_enum_persistence.py",
    "stage-B equivalence": "check_stage_b_equivalence.py",
    "role ontology": "check_role_ontology.py",
    "trace graph": "build_trace_graph.py",
    "approval state": "check_approval_state.py",
    "gate readiness": "check_gate_readiness.py",
    "terminal cleanliness": "git diff --exit-code",
}


def topology(steps: list[dict]) -> str:
    """A disposable workflow built from (name, extra-keys) pairs, for the mutation controls."""
    lines = ["name: synthetic", "on: [push]", "jobs:", f"  {ENFORCED_JOB}:",
             "    runs-on: ubuntu-latest", "    steps:"]
    for name, extra in steps:
        lines.append(f"      - name: {name}")
        for key, value in extra.items():
            lines.append(f"        {key}: {value}")
        lines.append("        run: python tools/spec/check_controlled_specs.py")
    return "\n".join(lines) + "\n"


class ExecutionPreservationSemantics(unittest.TestCase):
    """NF-24. Value semantics, over the forms the workflow language actually uses."""

    def test_if_conditions(self):
        for condition, expected in (("always()", PRESERVED),
                                    ("failure()", PRESERVED),
                                    ("!cancelled()", PRESERVED),
                                    ("success()", NOT_PRESERVED),
                                    ("cancelled()", NOT_PRESERVED),
                                    ("github.ref == 'refs/heads/main'", UNRESOLVED),
                                    ("${{ always() }}", UNRESOLVED)):
            with self.subTest(condition=condition):
                self.assertEqual(expected, runs_after_earlier_failure({"if": condition}))

    def test_no_if_means_the_default_which_does_not_survive_a_failure(self):
        self.assertEqual(NOT_PRESERVED, runs_after_earlier_failure({}))

    def test_continue_on_error_values(self):
        for value, expected in ((True, PRESERVED), (False, NOT_PRESERVED),
                                ("true", PRESERVED), ("false", NOT_PRESERVED),
                                ("${{ github.event_name == 'push' }}", UNRESOLVED)):
            with self.subTest(value=value):
                self.assertEqual(expected,
                                 failure_is_tolerated({"continue-on-error": value}))

    def test_no_continue_on_error_means_false(self):
        self.assertEqual(NOT_PRESERVED, failure_is_tolerated({}))

    def test_the_two_keys_answer_different_questions(self):
        """Section 18. Executing is not the same as having one's own failure ignored."""
        self.assertEqual(NOT_PRESERVED,
                         runs_after_earlier_failure({"continue-on-error": True}),
                         "tolerating this step's failure says nothing about whether it runs")
        self.assertEqual(NOT_PRESERVED,
                         failure_is_tolerated({"if": "always()"}),
                         "running regardless says nothing about whether its failure is "
                         "tolerated")


class ReachabilityMutations(unittest.TestCase):
    """NF-24. The historical bypass, and the forms that genuinely do preserve execution."""

    BLOCKER = ("Reconcile declared evidence obligations against observed evidence",
               {"run": "python tools/mps/check_evidence_reconciliation.py"})

    def observe(self, source: str):
        original = WORKFLOW.read_text(encoding="utf-8")
        try:
            WORKFLOW.write_text(source, encoding="utf-8", newline="\n")
            return reachability_problems(), unresolved_measurements()
        finally:
            WORKFLOW.write_text(original, encoding="utf-8", newline="\n")
            assert WORKFLOW.read_text(encoding="utf-8") == original

    def build(self, downstream_keys: dict, blocker_keys: dict | None = None):
        return topology([
            ("Early normally-green control", {}),
            ("Reconcile declared evidence obligations against observed evidence",
             blocker_keys or {}),
            ("Later mandatory control", downstream_keys),
            ("Confirm generated-source checks leave no diff", downstream_keys),
        ]).replace("      - name: Reconcile declared evidence obligations against observed "
                   "evidence\n        run: python tools/spec/check_controlled_specs.py",
                   "      - name: Reconcile declared evidence obligations against observed "
                   "evidence\n        run: python tools/mps/check_evidence_reconciliation.py")

    def test_reconciler_early_with_plain_downstream_steps_is_unreachable(self):
        problems, unresolved = self.observe(self.build({}))
        self.assertTrue(any("do not execute" in p for p in problems), problems)
        self.assertEqual([], unresolved)

    def test_if_success_does_not_preserve_execution(self):
        """The historical bypass. C8's observer went silent here."""
        problems, _ = self.observe(self.build({"if": "success()"}))
        self.assertTrue(any("do not execute" in p for p in problems),
                        "if: success() is the default and strands nothing less than nothing")

    def test_continue_on_error_false_downstream_does_not_preserve_execution(self):
        problems, _ = self.observe(self.build({"continue-on-error": "false"}))
        self.assertTrue(any("do not execute" in p for p in problems), problems)

    def test_an_arbitrary_condition_is_unresolved_not_a_pass(self):
        problems, unresolved = self.observe(
            self.build({"if": "github.ref == 'refs/heads/main'"}))
        self.assertTrue(problems, "an unresolved form must still fail closed")
        self.assertTrue(any("unresolved, not a pass" in u for u in unresolved), unresolved)

    def test_a_dynamic_expression_is_unresolved_not_a_pass(self):
        problems, unresolved = self.observe(
            self.build({"continue-on-error": "${{ github.event_name == 'push' }}"}))
        self.assertTrue(problems)
        self.assertTrue(any("unresolved, not a pass" in u for u in unresolved), unresolved)

    def test_a_genuinely_preserving_downstream_form_is_accepted(self):
        """Section 20. The observer must not simply reject every if or continue-on-error."""
        problems, unresolved = self.observe(self.build({"if": "always()"}))
        self.assertEqual([], problems, "if: always() genuinely runs after an earlier failure")
        self.assertEqual([], unresolved)

    def test_a_tolerated_blocker_failure_also_preserves_execution(self):
        """The other of the two independent mechanisms, on the other step."""
        problems, unresolved = self.observe(
            self.build({}, blocker_keys={"continue-on-error": "true"}))
        self.assertEqual([], problems,
                         "a blocker whose own failure is tolerated strands nothing")
        self.assertEqual([], unresolved)

    def test_the_historical_topology_is_still_reported(self):
        """Failure sensitivity against the real workflow as it stood at 2f10b3e."""
        historical = subprocess.run(
            ["git", "show", "2f10b3e:.github/workflows/controlled-spec-gates.yml"],
            capture_output=True, text=True, cwd=str(REPO_ROOT))
        self.assertEqual(0, historical.returncode)
        problems, _ = self.observe(historical.stdout)
        self.assertTrue(any("do not execute" in p for p in problems), problems)

    def test_the_historical_topology_with_the_bypass_is_still_reported(self):
        """NF-24 exactly: the real historical defect plus the key that used to hide it."""
        historical = subprocess.run(
            ["git", "show", "2f10b3e:.github/workflows/controlled-spec-gates.yml"],
            capture_output=True, text=True, cwd=str(REPO_ROOT))
        self.assertEqual(0, historical.returncode)
        source, seen = [], False
        for line in historical.stdout.splitlines(keepends=True):
            if line.strip().startswith("run: ") and seen:
                indent = " " * (len(line) - len(line.lstrip()))
                source.append(f"{indent}if: success()\n")
            source.append(line)
            if "check_evidence_reconciliation.py" in line:
                seen = True
        problems, _ = self.observe("".join(source))
        self.assertTrue(any("do not execute" in p for p in problems),
                        "the bypass that silenced the C8 observer must not silence this one")


class WorkflowReachability(unittest.TestCase):

    def test_the_workflow_parses_and_declares_control_steps(self):
        self.assertTrue(control_steps(), "no control steps derived")

    def test_no_mandatory_control_is_stranded(self):
        self.assertEqual([], reachability_problems())

    def test_every_declared_execution_semantics_is_resolvable(self):
        self.assertEqual([], unresolved_measurements())

    def test_the_reconciler_is_still_substantively_red(self):
        """Exit 1 is a valid measurement reporting substantive failure. 2 would be invalid."""
        self.assertEqual(1, run_control("python tools/mps/check_evidence_reconciliation.py"),
                         "0 would mean it was neutralized and 2 that it could not measure")

    def test_the_workflow_still_fails_while_the_reconciler_does(self):
        reconciler = [s for s in control_steps()
                      if "check_evidence_reconciliation.py" in s["run"]]
        self.assertEqual(1, len(reconciler))
        self.assertEqual(NOT_PRESERVED, failure_is_tolerated(reconciler[0]["step"]),
                         "tolerating it would turn a substantive evidence failure into a "
                         "passing workflow")

    def test_every_required_control_class_is_reachable(self):
        steps = control_steps()
        blockers = [b["position"] for b in standing_nonzero_controls()
                    if failure_is_tolerated(b["step"]) != PRESERVED]
        first = min(blockers) if blockers else len(steps) + 1
        for label, marker in REQUIRED_REACHABLE.items():
            with self.subTest(control=label):
                found = [s for s in steps if marker in s["run"]]
                self.assertTrue(found, f"{label} is not in the workflow at all")
                self.assertTrue(any(s["position"] < first
                                    or runs_after_earlier_failure(s["step"]) == PRESERVED
                                    for s in found),
                                f"{label} is behind a standing-nonzero control")

    def test_the_invariant_is_reachability_and_not_a_step_count(self):
        import inspect

        for fn in (control_steps, standing_nonzero_controls, reachability_problems,
                   runs_after_earlier_failure, failure_is_tolerated):
            with self.subTest(observer=fn.__name__):
                body = inspect.getsource(fn)
                self.assertNotIn("== 34", body)
                self.assertNotIn("== 21", body)
                self.assertNotIn("len(steps) ==", body)


class EnforcedScopeIsTheDeclaredScope(unittest.TestCase):
    """NF-25. The claim covers structural-gates, and nothing outside it carries a control."""

    def test_the_control_shape_predicate_matches_the_repository_conventions(self):
        self.assertTrue(looks_like_a_control("python tools/spec/check_approval_state.py"))
        self.assertTrue(looks_like_a_control("python tools/spec/build_trace_graph.py --check"))
        self.assertTrue(looks_like_a_control("./scripts/generate_vv_check_matrix.ps1 -Check"))
        self.assertTrue(looks_like_a_control("git diff --exit-code"))
        self.assertTrue(looks_like_a_control("python -m unittest discover -s tests -v"))
        self.assertFalse(looks_like_a_control("python tools/docs/compile_controlled_docs.py"))
        self.assertFalse(looks_like_a_control(
            "python tools/release/build_pdf_manifest.py --release-status review"))

    def test_every_command_in_the_enforced_job_is_control_shaped(self):
        for step in control_steps():
            for command in commands(step):
                with self.subTest(command=command):
                    self.assertTrue(looks_like_a_control(command),
                                    "an unrecognised command in the enforced job would sit "
                                    "outside the shape this scope claim relies on")

    def test_no_job_outside_the_enforced_scope_carries_a_control(self):
        """The scope narrowing cannot quietly become wrong later.

        document-build's non-execution is not a reachability defect because it carries no
        control. If that ever stops being true, this fails rather than continuing to describe
        one job while claiming the workflow.
        """
        jobs = workflow()["jobs"]
        self.assertIn(ENFORCED_JOB, jobs)
        for job, spec in jobs.items():
            if job == ENFORCED_JOB:
                continue
            for step in spec.get("steps", []):
                for line in str(step.get("run", "")).strip().splitlines():
                    command = line.strip()
                    if not command or "pip install" in command or "apt-get" in command:
                        continue
                    with self.subTest(job=job, command=command):
                        self.assertFalse(
                            looks_like_a_control(command),
                            f"job {job!r} now carries a control, so the reachability claim "
                            f"scoped to {ENFORCED_JOB!r} no longer covers the mandatory "
                            f"population")

    def test_the_out_of_scope_job_is_publication_and_depends_on_the_enforced_one(self):
        """The topology is recorded, not repaired: the dependency is deliberate."""
        jobs = workflow()["jobs"]
        other = [j for j in jobs if j != ENFORCED_JOB]
        self.assertEqual(["document-build"], other)
        self.assertEqual(ENFORCED_JOB, jobs["document-build"].get("needs"))
        self.assertNotIn("if", jobs["document-build"],
                         "no job-level condition is added; publishing from a checkpoint whose "
                         "assurance obligations are unmet is a governance decision")


if __name__ == "__main__":
    unittest.main()
