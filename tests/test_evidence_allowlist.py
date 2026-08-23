"""The retained-evidence allowlist exempts one rule, for named files, and nothing more.

MPS-MAT-009 F1. The allowlist is the narrow third option between two unacceptable ones:
exempting the evidence tree wholesale, which converts a disclosure control into a directory
rule, and hand-scrubbing retained artifacts, which makes them no longer the runner's output.

An exemption register is itself a control, so it is tested like one. The question that
matters is not "does the allowlist work" -- an allowlist that exempts everything works. It is
"what does it still refuse", and the answer has to include the case where an allowlisted file
carries prohibited content, because that is the shape a silent bypass takes.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "repo"))

import check_repository_hygiene as hygiene  # noqa: E402

ALLOWLIST = REPO_ROOT / "mps" / "materialization" / "evidence-allowlist.yaml"

# Assembled rather than written literally, so this file does not trip the scan it exercises.
DISCLOSURE = "C:" + chr(92) + "Users" + chr(92) + "someone" + chr(92) + "secret"


class AllowlistIsWellFormed(unittest.TestCase):

    def test_it_loads_without_problems(self):
        allowed, problems = hygiene.load_generated_type_allowlist()
        self.assertEqual([], problems)
        self.assertTrue(allowed)

    def test_every_entry_states_what_it_exempts_and_why(self):
        body = yaml.safe_load(ALLOWLIST.read_text(encoding="utf-8"))
        for entry in body["entries"]:
            for field in hygiene.ALLOWLIST_REQUIRED_FIELDS:
                self.assertTrue(entry.get(field), f"{entry.get('path')} lacks {field}")
            self.assertTrue((REPO_ROOT / entry["path"]).is_file(), entry["path"])

    def test_entries_are_exact_paths_never_directories_or_globs(self):
        body = yaml.safe_load(ALLOWLIST.read_text(encoding="utf-8"))
        for entry in body["entries"]:
            path = entry["path"]
            self.assertNotIn("*", path, "a glob would exempt files nobody reviewed")
            self.assertFalse(path.endswith("/"), "a directory exemption is not per-file")
            self.assertTrue((REPO_ROOT / path).is_file())

    def test_the_evidence_tree_is_not_exempt_wholesale(self):
        allowed, _ = hygiene.load_generated_type_allowlist()
        for path in allowed:
            self.assertNotEqual(path.rstrip("/"), "mps/materialization/evidence")

    def test_a_stale_entry_is_refused(self):
        """An exemption must not outlive the artifact it was written for."""
        original = ALLOWLIST.read_text(encoding="utf-8")
        body = yaml.safe_load(original)
        body["entries"].append({
            "path": "mps/materialization/evidence/does-not-exist.log",
            "artifact_class": "x", "reason": "y", "supports": {"acceptance_item": "z"}})
        try:
            ALLOWLIST.write_text(yaml.safe_dump(body), encoding="utf-8")
            _, problems = hygiene.load_generated_type_allowlist()
            self.assertTrue(any("does not exist" in p for p in problems))
        finally:
            ALLOWLIST.write_text(original, encoding="utf-8", newline="")

    def test_an_entry_without_a_stated_reason_is_refused(self):
        original = ALLOWLIST.read_text(encoding="utf-8")
        body = yaml.safe_load(original)
        body["entries"].append({
            "path": "mps/materialization/evidence/MPS-MAT-008/green/junit.xml",
            "artifact_class": "x", "supports": {"acceptance_item": "z"}})
        try:
            ALLOWLIST.write_text(yaml.safe_dump(body), encoding="utf-8")
            _, problems = hygiene.load_generated_type_allowlist()
            self.assertTrue(any("is missing" in p for p in problems))
        finally:
            ALLOWLIST.write_text(original, encoding="utf-8", newline="")


class ExemptionScope(unittest.TestCase):
    """generated-artifact-type exemption applies; nothing else does."""

    def setUp(self):
        self.allowed, problems = hygiene.load_generated_type_allowlist()
        self.assertEqual([], problems)
        self.listed = sorted(self.allowed)[0]
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_generated_type_exemption_applies_to_a_listed_path(self):
        clean = Path(self.tmp.name) / "clean.log"
        clean.write_bytes(b"BUILD SUCCESSFUL" + bytes([10]))
        errors, _ = hygiene.file_problems(self.listed, clean, self.allowed)
        self.assertEqual([], errors)

    def test_generated_type_rejection_still_applies_to_an_unlisted_path(self):
        """A newly retained generated artifact nobody listed stays non-passing."""
        clean = Path(self.tmp.name) / "other.log"
        clean.write_bytes(b"BUILD SUCCESSFUL" + bytes([10]))
        unlisted = "mps/materialization/evidence/MPS-MAT-008/green/newly-added.log"
        errors, _ = hygiene.file_problems(unlisted, clean, self.allowed)
        self.assertTrue(any("generated artifact type" in e for e in errors))

    def test_disclosure_scanning_still_applies_to_an_allowlisted_artifact(self):
        """The control that stops the allowlist becoming a disclosure bypass.

        generated-artifact type exemption -> applies
        disclosure exemption              -> does NOT apply
        hygiene result                    -> RED
        """
        dirty = Path(self.tmp.name) / "dirty.log"
        dirty.write_bytes(("built from " + DISCLOSURE + chr(10)).encode("utf-8"))
        errors, _ = hygiene.file_problems(self.listed, dirty, self.allowed)
        self.assertTrue(errors, "an allowlisted artifact must still be disclosure-scanned")
        self.assertTrue(any("user-profile" in e for e in errors), errors)
        # And specifically: the generated-type rule was suppressed, so the ONLY reason it is
        # red is disclosure. That is what makes this a scope test rather than a smoke test.
        self.assertFalse(any("generated artifact type" in e for e in errors))

    def test_secret_scanning_still_applies_to_an_allowlisted_artifact(self):
        dirty = Path(self.tmp.name) / "secret.log"
        dirty.write_bytes(("AKIA" + "A" * 16 + chr(10)).encode("utf-8"))
        errors, _ = hygiene.file_problems(self.listed, dirty, self.allowed)
        self.assertTrue(any("AWS access key" in e for e in errors), errors)

    def test_crlf_detection_still_applies_to_an_allowlisted_artifact(self):
        dirty = Path(self.tmp.name) / "crlf.log"
        dirty.write_bytes(b"line" + bytes([13, 10]))
        _, carries_crlf = hygiene.file_problems(self.listed, dirty, self.allowed)
        self.assertTrue(carries_crlf)


class DisclosureCoverage(unittest.TestCase):
    """The retained-evidence types must all be inside the scanned population."""

    def test_every_retained_evidence_type_is_disclosure_scanned(self):
        tree = REPO_ROOT / "mps" / "materialization" / "evidence"
        unscanned = sorted({p.suffix.casefold() for p in tree.rglob("*")
                            if p.is_file() and p.suffix.casefold()
                            not in hygiene.TEXT_SUFFIXES})
        self.assertEqual([], unscanned,
                         f"retained evidence of these types is never disclosure-scanned: "
                         f"{unscanned}")


if __name__ == "__main__":
    unittest.main()
