"""The recorder cannot retain evidence that would fail the controls it must satisfy.

MPS-MAT-009 F1. Canonicalization was moved inside the recorder so the invalid state is
unreachable rather than merely discouraged. That is only true if every refusal path actually
refuses, so each is driven here, and each must leave nothing behind: a recorder that writes
three artifacts and then refuses the fourth has produced a partially updated evidence record,
which reads as a complete one.

The canonicalizer's own history is the reason the type-preservation controls exist. Its first
version substituted a readable placeholder that happened to contain angle brackets, and
silently destroyed every JUnit report it touched -- reporting success while emitting a file no
XML parser would read. Nothing else in the suite would have noticed until a consumer tried to
parse the retained evidence.
"""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import canonicalize_evidence as canon  # noqa: E402
import check_headless_build_currency as currency  # noqa: E402

DISCLOSURE = "C:" + chr(92) + "Users" + chr(92) + "someone"


class CanonicalizationPreservesType(unittest.TestCase):

    def test_xml_stays_parseable_after_canonicalization(self):
        raw = ('<testsuite tests="1" home="' + DISCLOSURE
               + '"><testcase name="t"/></testsuite>').encode("utf-8")
        canonical = canon.canonicalize_bytes(raw)
        self.assertNotIn("Users", canonical.decode("utf-8"))
        intact, why = canon.structurally_intact(canonical, ".xml")
        self.assertTrue(intact, why)

    def test_json_stays_parseable_after_canonicalization(self):
        raw = ('{"path": "' + DISCLOSURE.replace(chr(92), chr(92) * 2) + '"}').encode("utf-8")
        canonical = canon.canonicalize_bytes(raw)
        intact, why = canon.structurally_intact(canonical, ".json")
        self.assertTrue(intact, why)

    def test_the_placeholder_carries_no_xml_metacharacters(self):
        """The specific defect: a placeholder with angle brackets destroys XML silently."""
        for _, _, replacement in canon.SUBSTITUTIONS:
            self.assertNotIn("<", replacement)
            self.assertNotIn(">", replacement)
            self.assertNotIn("&", replacement)

    def test_canonicalization_is_idempotent(self):
        raw = ("a " + DISCLOSURE + " b" + chr(10)).encode("utf-8")
        once = canon.canonicalize_bytes(raw)
        self.assertEqual(once, canon.canonicalize_bytes(once))
        self.assertTrue(canon.is_canonical(once))

    def test_canonicalization_cannot_report_success_while_emitting_an_invalid_artifact(self):
        """A rule that broke the type must raise, not return a digest."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "broken.xml"
            source.write_bytes(b"<a>unclosed")
            with self.assertRaises(canon.NotCanonical):
                canon.canonicalize_file(source, Path(tmp) / "out.xml")
            self.assertFalse((Path(tmp) / "out.xml").exists(),
                             "nothing may be written when the artifact does not validate")

    def test_line_endings_are_normalised(self):
        raw = b"a" + bytes([13, 10]) + b"b" + bytes([13, 10])
        self.assertNotIn(bytes([13]), canon.canonicalize_bytes(raw))


class RecorderRefusals(unittest.TestCase):
    """Every state that must be unreachable, driven through the retention path."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def source(self, name: str, content: bytes) -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def test_a_missing_artifact_is_refused(self):
        with self.assertRaises(currency.RetentionRefused):
            currency.prepare_for_retention(self.root / "absent.xml", self.root / "out.xml")

    def test_an_artifact_that_fails_type_validation_is_refused(self):
        source = self.source("bad.xml", b"<a>unclosed")
        with self.assertRaises(currency.RetentionRefused) as caught:
            currency.prepare_for_retention(source, self.root / "out.xml")
        self.assertIn("declared type", str(caught.exception))

    def test_host_disclosure_is_removed_rather_than_refused_when_the_rule_covers_it(self):
        """The normal path: the recorder canonicalizes, so retention succeeds cleanly."""
        source = self.source("log.log", ("built at " + DISCLOSURE + chr(10)).encode())
        prepared = currency.prepare_for_retention(source, self.root / "out.log")
        self.assertNotIn("Users", prepared["bytes"].decode("utf-8"))
        self.assertNotEqual(prepared["as_produced_sha256"], prepared["canonical_sha256"])

    def test_disclosure_the_rule_does_not_cover_is_refused_not_retained(self):
        """A secret is not a path, so canonicalization cannot remove it; retention refuses."""
        source = self.source("tok.log", ("AKIA" + "B" * 16 + chr(10)).encode())
        with self.assertRaises(currency.RetentionRefused) as caught:
            currency.prepare_for_retention(source, self.root / "out.log")
        self.assertIn("AWS access key", str(caught.exception))

    def test_the_recorded_digest_describes_the_retained_bytes_not_the_raw_bytes(self):
        import hashlib

        raw = ("x " + DISCLOSURE + chr(10)).encode()
        source = self.source("d.log", raw)
        prepared = currency.prepare_for_retention(source, self.root / "out.log")
        self.assertEqual(prepared["as_produced_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(prepared["canonical_sha256"],
                         hashlib.sha256(prepared["bytes"]).hexdigest())
        self.assertNotEqual(prepared["canonical_sha256"], prepared["as_produced_sha256"])

    def test_preparation_writes_nothing(self):
        """Validation happens before any artifact lands, so a later refusal leaves no trace."""
        source = self.source("ok.log", b"fine" + bytes([10]))
        destination = self.root / "nested" / "out.log"
        currency.prepare_for_retention(source, destination)
        self.assertFalse(destination.exists())


class RecordedEvidenceIsCanonical(unittest.TestCase):
    """Properties of the record as committed."""

    def test_every_required_artifact_is_in_canonical_form(self):
        import json

        evidence = json.loads(
            (REPO_ROOT / "mps" / "materialization"
             / "headless-acceptance-evidence.json").read_text(encoding="utf-8"))
        required = currency.required_artifacts(evidence)
        self.assertTrue(required)
        for label, reference in required:
            with self.subTest(artifact=reference):
                raw = (REPO_ROOT / reference).read_bytes()
                self.assertEqual(canon.canonicalize_bytes(raw), raw,
                                 f"{label} is retained in non-canonical form")

    def test_canonicalization_metadata_records_both_digests(self):
        import json

        evidence = json.loads(
            (REPO_ROOT / "mps" / "materialization"
             / "headless-acceptance-evidence.json").read_text(encoding="utf-8"))
        import hashlib

        for branch, key in (("build", "log"), ("model_tests", "report")):
            meta = (evidence.get(branch) or {}).get(key + "_canonicalization")
            self.assertIsNotNone(meta, f"{branch}: the record must say what rule produced "
                                       f"the retained form")
            self.assertEqual(canon.RULE_ID, meta["rule"])
            self.assertTrue(meta["as_produced_sha256"])
            # The recorded digest must describe the bytes a reviewer receives, never the raw
            # bytes the runner emitted. Whether the two DIFFER depends on whether that
            # artifact carried anything the rule removes, so equality is not a defect here --
            # cold-build.log happens to contain no host paths and canonicalizes to itself.
            retained = REPO_ROOT / evidence[branch][key]
            self.assertEqual(hashlib.sha256(retained.read_bytes()).hexdigest(),
                             evidence[branch][key + "_sha256"])

    def test_an_artifact_that_needed_canonicalizing_records_two_distinct_digests(self):
        """The green JUnit report carried host paths, so its two digests must differ."""
        import json

        evidence = json.loads(
            (REPO_ROOT / "mps" / "materialization"
             / "headless-acceptance-evidence.json").read_text(encoding="utf-8"))
        meta = evidence["model_tests"]["report_canonicalization"]
        self.assertNotEqual(meta["as_produced_sha256"],
                            evidence["model_tests"]["report_sha256"],
                            "the runner's raw report contained host paths; the retained "
                            "form must therefore be a different artifact by digest")


if __name__ == "__main__":
    unittest.main()
