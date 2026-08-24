"""NF-21. Every mandatory control in the controlled workflow must have an execution path.

GitHub Actions stops a job at its first failing step. A control that stands substantively
nonzero -- one whose RED is the correct answer and is expected to persist -- therefore strands
every mandatory control positioned behind it. The evidence reconciler is exactly that: exit 1,
seven declared evidence obligations still OPEN, and expected to stay that way until they are
resolved. It ran thirteenth of thirty-four, and the twenty-one steps after it had never
executed in CI for as long as the RED had stood. They did not fail; CI established nothing
about them, while presenting their absence in the same shape as their success.

The invariant here is REACHABILITY, not the reconciler's current position and not today's step
count. A literal count would be the fragile-cardinality defect this register already carries
three times over: it would pass while describing a workflow that no longer exists. So the
populations are derived from the workflow file, and the standing-nonzero set is derived by
executing the controls rather than by asserting which ones are red.

The RED itself is untouched. Nothing here makes the workflow green, and a control that turns
the reconciler's substantive failure into a pass would be defeating the observer rather than
satisfying it.
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

# A step is execution-preserving when it declares one of these: its failure does not stop the
# job, or later steps run regardless. Read as a set rather than tested one at a time so a new
# mechanism is added in one place.
EXECUTION_PRESERVING_KEYS = ("continue-on-error", "if")


def workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def control_steps(job: str = "structural-gates") -> list[dict]:
    """The ordered steps of a job that actually run a control.

    Derived: a step is a control if it runs something. Setup steps -- checkout, Python
    install, dependency install -- are excluded by name-independent shape, because they
    establish the conditions rather than assert anything.
    """
    steps = workflow()["jobs"][job]["steps"]
    out = []
    for position, step in enumerate(steps, start=1):
        run = step.get("run")
        if not run:
            continue
        if re.search(r"pip install|actions/", str(run)):
            continue
        out.append({"position": position, "name": step.get("name", "<unnamed>"),
                    "run": run.strip(), "step": step})
    return out


def commands(step: dict) -> list[str]:
    return [line.strip() for line in step["run"].splitlines() if line.strip()]


def is_execution_preserving(step: dict) -> bool:
    """True when the step declares something that keeps later steps running.

    Accepts either a derived control record or a raw workflow step, because both are natural
    to hand it and a signature that quietly requires one is how the caller gets it wrong.
    """
    raw = step.get("step", step)
    return any(key in raw for key in EXECUTION_PRESERVING_KEYS)


def run_control(command: str) -> int:
    """Execute one control command and return its exit code."""
    if command.startswith("python "):
        argv = [sys.executable, *command.split()[1:]]
    else:
        argv = command.split()
    result = subprocess.run(argv, capture_output=True, text=True, cwd=str(REPO_ROOT))
    return result.returncode


def standing_nonzero_controls() -> list[dict]:
    """Controls that are nonzero in the repository's current state, by execution.

    Derived rather than declared. Asserting which control is red would make this observer
    agree with a list instead of with the repository, and the two agree until they do not --
    which is how a control stops testing the thing and starts testing its own copy of it.

    Only cheap, side-effect-free checks are executed. The regression step is excluded: it runs
    this file, and a control that runs itself does not terminate.
    """
    nonzero = []
    for step in control_steps():
        for command in commands(step):
            if "unittest discover" in command or command.startswith("git "):
                continue
            if not command.startswith("python tools/"):
                continue
            if run_control(command) != 0:
                nonzero.append({**step, "command": command})
                break
    return nonzero


def reachability_problems() -> list[str]:
    """No mandatory control may sit behind a standing-nonzero one with nothing preserving it."""
    steps = control_steps()
    problems = []
    for blocker in standing_nonzero_controls():
        if is_execution_preserving(blocker["step"]):
            continue
        stranded = [s for s in steps if s["position"] > blocker["position"]
                    and not is_execution_preserving(s["step"])]
        if stranded:
            problems.append(
                f"step {blocker['position']} ({blocker['name']!r}) exits nonzero and declares "
                f"no execution-preserving mechanism, so {len(stranded)} later mandatory "
                f"control(s) are unreachable, beginning with "
                f"{stranded[0]['position']} ({stranded[0]['name']!r})")
    return problems


# Control CLASSES required to be reachable. Named by the tool that implements each, so the
# assertion is about what must run rather than about how many steps there happen to be. A
# class whose tool is not in the workflow at all is reported too: a control that was removed
# is not a control that passed.
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


class WorkflowReachability(unittest.TestCase):

    def test_the_workflow_parses_and_declares_control_steps(self):
        steps = control_steps()
        self.assertTrue(steps, "no control steps derived; the parser has stopped observing")

    def test_no_mandatory_control_is_stranded_behind_a_standing_nonzero_one(self):
        self.assertEqual([], reachability_problems())

    def test_the_reconciler_is_still_substantively_red(self):
        """The repair must not have made it pass. That would be defeating the observer.

        Exit 1 is a valid measurement reporting a substantive failure. Exit 2 would be
        measurement-invalid and would mean the instrument established nothing, which is a
        different condition and must not be read as the standing RED.
        """
        code = run_control("python tools/mps/check_evidence_reconciliation.py")
        self.assertEqual(1, code,
                         "the standing substantive RED must remain; 0 would mean it was "
                         "neutralized and 2 would mean the measurement was invalid")

    def test_the_workflow_still_fails_while_the_reconciler_does(self):
        """Reachability must not have been bought with a green workflow."""
        reconciler = [s for s in control_steps()
                      if "check_evidence_reconciliation.py" in s["run"]]
        self.assertEqual(1, len(reconciler), "exactly one reconciler step")
        self.assertFalse(is_execution_preserving(reconciler[0]["step"]),
                         "its failure must still fail the job; continue-on-error here would "
                         "turn a substantive evidence failure into a passing workflow")

    def test_every_required_control_class_is_reachable(self):
        steps = control_steps()
        blockers = [b["position"] for b in standing_nonzero_controls()
                    if not is_execution_preserving(b["step"])]
        first_blocker = min(blockers) if blockers else len(steps) + 1
        for label, marker in REQUIRED_REACHABLE.items():
            with self.subTest(control=label):
                found = [s for s in steps if marker in s["run"]]
                self.assertTrue(found, f"{label} is not in the workflow at all")
                self.assertTrue(
                    any(s["position"] < first_blocker for s in found),
                    f"{label} is positioned behind a standing-nonzero control")

    def test_the_invariant_is_reachability_and_not_a_step_count(self):
        """Scoped to the observer functions, not the file.

        Scanning the whole module matches the literals in this assertion and fails on itself,
        which is a control testing its own source instead of the code it is about. That exact
        mistake was made twice already in this repository, so it is not repeated here.
        """
        import inspect

        for fn in (control_steps, standing_nonzero_controls, reachability_problems,
                   is_execution_preserving):
            body = inspect.getsource(fn)
            with self.subTest(observer=fn.__name__):
                self.assertNotIn("== 34", body)
                self.assertNotIn("== 21", body)
                self.assertNotIn("len(steps) ==", body)
        self.assertNotIn("34", str(sorted(REQUIRED_REACHABLE)),
                         "the required set names control classes, never positions")

    def test_moving_a_standing_nonzero_control_earlier_is_detected(self):
        """Failure sensitivity, against the historical topology rather than a synthetic one."""
        original = WORKFLOW.read_text(encoding="utf-8")
        try:
            historical = subprocess.run(
                ["git", "show", "2f10b3e:.github/workflows/controlled-spec-gates.yml"],
                capture_output=True, text=True, cwd=str(REPO_ROOT))
            self.assertEqual(0, historical.returncode)
            WORKFLOW.write_text(historical.stdout, encoding="utf-8", newline="\n")
            problems = reachability_problems()
        finally:
            WORKFLOW.write_text(original, encoding="utf-8", newline="\n")
        self.assertTrue(any("unreachable" in p for p in problems),
                        "the topology at 2f10b3e must be reported as unreachable")
        self.assertEqual(original, WORKFLOW.read_text(encoding="utf-8"),
                         "the workflow must be restored byte-identically")


if __name__ == "__main__":
    unittest.main()
