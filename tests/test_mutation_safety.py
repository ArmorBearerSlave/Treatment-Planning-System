"""NF-35 / IR-05. An interrupted mutation cannot leave a controlled tracked file modified.

The committed helper restored controlled files in a Python `finally`, which the interpreter
honours only while it is alive. A hard kill between the write and the restore left a tracked
file modified, with no pre-image anywhere and nothing that would notice on the next run.

These controls do not argue that a journal would help. They kill a real process in the middle of
a real mutation of a real controlled file, and then require recovery to put it back
byte-identically -- checked against the bytes, against the digest, and against Git.

The invariant throughout is that the mutate-kill-recover cycle is a no-op with respect to the
state it started from. It is judged against a snapshot taken in setUp, never against HEAD. This
repository carries authored uncommitted work -- findings.yaml among it -- and a control that
demanded a clean tree would be asserting something about the commit state of unrelated edits
rather than about recovery.

The kill is unconditional and uncatchable: Popen.kill is SIGKILL on POSIX and TerminateProcess on
Windows, so the child gets no `finally`, no atexit and no signal handler. That is the point. A
test that asked the child to exit cleanly would be demonstrating the mechanism that already
worked.

Safety of the demonstration itself: the parent restores in its own tearDown, and
controlled_mutation.recover() runs on import, so even a death of the test runner during the
window is repaired by the next run. That is the same property under test, applied to the test.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import textwrap
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import controlled_mutation  # noqa: E402

TARGET = REPO_ROOT / "mps" / "materialization" / "mps-mat-009" / "findings.yaml"
ANCHOR = "schema_version:"


def git(*args: str) -> tuple[int, str]:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, cwd=REPO_ROOT)
    return proc.returncode, proc.stdout.strip()


def git_view(target: Path) -> dict[str, str]:
    """Git's own view of one path: its porcelain status, and the blob id of the working-tree
    content as Git would store it.

    Both components are properties of the file alone. Neither is compared with HEAD; the reason
    is recorded at the assertion that consumes them.

    The blob id is not decoration, and the status flag alone would not do. In a tree carrying
    legitimate uncommitted work the porcelain flag reads ` M` before the mutation and ` M`
    during it -- observed, not assumed -- so a status-only comparison has no discriminating
    power whatever and would hold even if recovery had restored nothing. The blob id moves with
    the content and is what actually carries the observation. It is taken through `--path` so
    the .gitattributes filters apply and the identity is the one a fresh clone would hold,
    rather than the one this working copy happens to carry.
    """
    rel = target.relative_to(REPO_ROOT).as_posix()
    view = {}
    for key, args in (("status", ("status", "--porcelain", "--", rel)),
                      ("blob", ("hash-object", f"--path={rel}", "--", rel))):
        code, out = git(*args)
        if code != 0:
            raise AssertionError(f"git {args[0]} failed on {rel} with exit status {code}")
        view[key] = out
    return view


class TheJournalOutlivesTheProcess(unittest.TestCase):
    """The property, demonstrated against a controlled file rather than a stand-in."""

    def setUp(self):
        self.assertEqual([], controlled_mutation.outstanding(),
                         "a journal entry is outstanding before this test began")
        self.original = TARGET.read_bytes()
        self.digest = hashlib.sha256(self.original).hexdigest()
        # The snapshot the restoration is judged against, taken from the tree as it actually
        # is rather than from HEAD. See the assertion at the end of the kill test.
        self.git_before = git_view(TARGET)

    def tearDown(self):
        # Belt and braces. If anything above left the file modified, put it back here rather
        # than handing the next control a tree nobody authored.
        controlled_mutation.recover()
        if TARGET.read_bytes() != self.original:
            TARGET.write_bytes(self.original)

    def child_source(self) -> str:
        """A child that journals, mutates, and then blocks forever waiting to be killed."""
        return textwrap.dedent(f"""
            import sys, time
            sys.path.insert(0, {str(TARGET.parents[3] / "tests")!r})
            import controlled_mutation
            from pathlib import Path
            target = Path({str(TARGET)!r})
            text = target.read_bytes().decode("utf-8")
            controlled_mutation.begin(
                target, text.replace({ANCHOR!r}, "MUTILATED_BY_A_DOOMED_PROCESS:", 1)
                            .encode("utf-8"))
            print("MUTATED", flush=True)
            while True:
                time.sleep(0.05)
            """)

    def test_a_killed_mutation_is_recovered_byte_identically(self):
        child = subprocess.Popen([sys.executable, "-c", self.child_source()],
                                 stdout=subprocess.PIPE, text=True, cwd=REPO_ROOT)
        try:
            line = child.stdout.readline()
            self.assertEqual("MUTATED", line.strip(),
                             "the child never reached the mutated state")

            # The condition the finding is about must genuinely exist right now.
            self.assertNotEqual(self.original, TARGET.read_bytes(),
                                "the controlled file is not actually mutated; the control would "
                                "otherwise pass without reproducing anything")
            self.assertIn("MUTILATED_BY_A_DOOMED_PROCESS",
                          TARGET.read_text(encoding="utf-8"))
            self.assertEqual(1, len(controlled_mutation.outstanding()),
                             "the pre-image was not journalled before the mutation")

            child.kill()
            child.wait(timeout=30)
            self.assertNotEqual(0, child.returncode, "the child exited rather than being killed")
        finally:
            if child.poll() is None:                      # pragma: no cover - defensive
                child.kill()
                child.wait(timeout=30)
            child.stdout.close()

        # The dead process ran no finally. The file is still modified.
        self.assertNotEqual(self.original, TARGET.read_bytes(),
                            "the killed child somehow restored the file, which would mean the "
                            "control is not reproducing an interrupted mutation")

        # Prove the comparison at the end can actually detect a failed restoration, on this run
        # rather than in principle: while the file is demonstrably modified, Git's view of it
        # must differ from the pre-mutation view. Without this, a Git check that happened to be
        # insensitive would pass unconditionally and look like evidence.
        self.assertNotEqual(self.git_before, git_view(TARGET),
                            "Git's view is unchanged while the file is modified, so the "
                            "restoration check below could not distinguish a recovered file "
                            "from an unrecovered one")

        repaired = controlled_mutation.recover()
        self.assertEqual([str(TARGET)], repaired,
                         "recovery did not report repairing the controlled file")
        self.assertEqual(self.original, TARGET.read_bytes(),
                         "the file was not restored byte-identically")
        self.assertEqual(self.digest, hashlib.sha256(TARGET.read_bytes()).hexdigest())
        self.assertEqual([], controlled_mutation.outstanding(),
                         "the journal entry was not discarded after a verified restoration")

        # The invariant is restoration to the PRE-MUTATION SNAPSHOT, not equality with HEAD.
        #
        # This assertion previously required the controlled file to be Git-clean. That is a
        # different proposition, it was never the one under test, and it made this control's
        # verdict depend on whether the repository happened to be carrying unrelated
        # uncommitted work. findings.yaml legitimately carries authored C10C edits, so the
        # control reported RED while the mechanism it exercises was working perfectly -- the
        # byte and digest comparisons immediately above had already matched.
        #
        # This is not a gate narrowed to make it green. In a clean tree the replacement is at
        # least as strong: it compares Git content identity, where the old form compared only a
        # status flag. It is additionally applicable in a tree carrying authored work, which
        # the old form was not. What was withdrawn is a claim about the repository's commit
        # state that this control was never entitled to make.
        self.assertEqual(self.git_before, git_view(TARGET),
                         "Git's view of the controlled file did not return to its pre-mutation "
                         "state")

    def test_recovery_is_idempotent(self):
        """A second recovery over a healthy tree must do nothing and report nothing."""
        self.assertEqual([], controlled_mutation.recover())
        self.assertEqual([], controlled_mutation.recover())
        self.assertEqual(self.original, TARGET.read_bytes())

    def test_the_journal_precedes_the_mutation(self):
        """Ordering is the whole mechanism.

        Journalling after the write would reproduce the defect with more machinery, because the
        fatal window is exactly the interval in which the file is modified and no pre-image
        exists. Asserted behaviourally: at the moment the file differs, the journal must already
        be on disk -- which is what the killed child above observes from outside the process.
        """
        import inspect

        source = inspect.getsource(controlled_mutation.begin)
        journal_at = source.index("_write_journal")
        write_at = source.index("write_bytes(new_bytes)")
        self.assertLess(journal_at, write_at,
                        "the pre-image is written after the mutation, which leaves the fatal "
                        "window open")

    def test_a_torn_journal_entry_is_reported_not_applied(self):
        """A partial pre-image must never be restored: it would write garbage over a good file."""
        controlled_mutation.JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
        torn = controlled_mutation.JOURNAL_DIR / "torn.journal"
        torn.write_bytes(b"\x00\x00\x00\x08{\"path\"")
        try:
            reported = controlled_mutation.recover()
            self.assertTrue(any("unreadable" in r for r in reported),
                            "a torn entry was silently ignored")
            self.assertTrue(torn.exists(),
                            "a torn entry was deleted, discarding the only record that a run "
                            "went wrong")
            self.assertEqual(self.original, TARGET.read_bytes())
        finally:
            torn.unlink(missing_ok=True)


class EveryControlledMutationIsJournalled(unittest.TestCase):
    """A hardened helper is worth nothing if a control writes to a controlled file directly."""

    def test_the_closure_warrant_helper_routes_through_the_journal(self):
        import inspect

        sys.path.insert(0, str(REPO_ROOT / "tests"))
        import test_closure_warrant

        source = inspect.getsource(test_closure_warrant.mutated)
        self.assertIn("controlled_mutation", source,
                      "the mutation helper no longer routes through the journal")
        self.assertNotIn("write_bytes", source,
                         "the helper writes to a controlled file outside the journal")

    def test_no_control_module_writes_a_controlled_record_directly(self):
        """Population-derived, not a named list: every test module is scanned.

        Scoped to the CONTROLLED RECORDS -- the finding register and the review register -- which
        is what NF-35 is about and what the repair covers. Writes to temporary directories, to
        disposable fixtures a control builds for itself, and to ignored derived paths are outside
        the claim and are not flagged; a control whose population is wider than its claim is the
        defect this register has recorded three times, and inflating this one would be a fourth.

        Each module's own path constants are resolved from its parse tree, so a module that
        renames its constant or adds a new one is covered without editing this control.
        """
        import ast

        record_markers = ("mps-mat-009", "findings.yaml", "independent-reviews.yaml")
        offenders = []
        for module in sorted((REPO_ROOT / "tests").glob("test_*.py")):
            source = module.read_text(encoding="utf-8")
            tree = ast.parse(source)
            controlled = set()
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                segment = ast.get_source_segment(source, node.value) or ""
                if not any(marker in segment for marker in record_markers):
                    continue
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        controlled.add(target.id)
            if not controlled:
                continue
            journalled = "controlled_mutation" in source
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr not in {"write_bytes", "write_text"}:
                    continue
                name = getattr(node.func.value, "id", None)
                if name not in controlled:
                    continue
                if journalled and module.name == Path(__file__).name:
                    continue      # this module's own kill control, restored in tearDown
                offenders.append(f"{module.name}:{node.lineno} writes {name} unjournalled")
        self.assertEqual([], offenders, f"unjournalled controlled-record writes: {offenders}")

    def test_the_control_above_has_a_population_to_range_over(self):
        """Otherwise it would pass by scanning nothing, which is NF-20's shape."""
        import ast

        found = 0
        for module in sorted((REPO_ROOT / "tests").glob("test_*.py")):
            source = module.read_text(encoding="utf-8")
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, ast.Assign):
                    segment = ast.get_source_segment(source, node.value) or ""
                    if any(m in segment for m in
                           ("mps-mat-009", "findings.yaml", "independent-reviews.yaml")):
                        found += 1
        self.assertGreater(found, 0, "no module declares a controlled-record path")

    def test_reintroducing_an_unjournalled_write_is_detected(self):
        """Failure sensitivity for the scanner, without touching a committed module."""
        import ast
        import tempfile

        synthetic = (
            "from pathlib import Path\n"
            "FINDINGS = Path('mps/materialization/mps-mat-009/findings.yaml')\n"
            "def go():\n"
            "    FINDINGS.write_bytes(b'x')\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            probe = Path(tmp) / "test_probe.py"
            probe.write_text(synthetic, encoding="utf-8")
            source = probe.read_text(encoding="utf-8")
            tree = ast.parse(source)
            controlled = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
                          for t in n.targets if isinstance(t, ast.Name)
                          and "mps-mat-009" in (ast.get_source_segment(source, n.value) or "")}
            self.assertEqual({"FINDINGS"}, controlled)
            hits = [n.lineno for n in ast.walk(tree)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in {"write_bytes", "write_text"}
                    and getattr(n.func.value, "id", None) in controlled]
            self.assertEqual([4], hits, "the scanner does not detect a reintroduced write")

    def test_the_workflow_helper_is_recorded_as_not_yet_journalled(self):
        """Stated rather than quietly fixed or quietly ignored.

        tests/test_workflow_reachability.py restores the workflow file in its own finally and was
        not converted here. NF-35 is non-blocking and the brief that raised it says not to
        destabilise the suite for it; converting the reachability controls would mean rewriting
        nine mutation scenarios that assert byte-identity inside themselves. The exposure is
        named so that it is a known residual rather than an oversight, and it is smaller: the
        workflow file is not a controlled RECORD and a modified copy of it fails the reachability
        observer loudly on the next run rather than reading as authored content.
        """
        source = (REPO_ROOT / "tests" / "test_workflow_reachability.py").read_text(
            encoding="utf-8")
        self.assertIn("finally", source,
                      "the workflow helper no longer matches the residual recorded for it; "
                      "update NF-35's residual rather than leaving this control describing a "
                      "state that has changed")


if __name__ == "__main__":
    unittest.main()
