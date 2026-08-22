"""Negative tests for the HLR category classification in the import bundle builder.

Every one of these is a way the corpus could arrive partially or wrongly classified while
still looking plausible. The category is a mandatory field on the requirement roots MPS-4
will create, so a gap here does not surface as a missing value: it surfaces much later as
a modelling error, long after the decision that caused it is out of sight.

Nothing in the pipeline reads requirement wording. These fixtures exist to prove that the
classification comes from the controlled alias table or fails.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import build_hlr_import_bundle as hlr  # noqa: E402

BS = chr(92)


def row(category_id: str, source_id: str) -> str:
    """One categorized row, in the shape the controlled document actually uses."""
    return (BS + "mbox{" + category_id + "} & " + BS + "mbox{" + source_id + "} & "
            "The NL-TPS shall do the thing. & WF & I " + BS + BS + "\n")


def records(*ids: str) -> list[dict[str, object]]:
    return [{"id": i, "domain": i.split("-")[0]} for i in ids]


class ClassificationParsingTests(unittest.TestCase):
    def test_a_well_formed_table_is_read(self) -> None:
        text = row("HFR-NLI-001", "NLI-001") + row("HOR-GOV-001", "GOV-001")
        mapping = hlr.parse_classification(text)
        self.assertEqual(mapping["NLI-001"],
                         {"category_id": "HFR-NLI-001", "category": "functional"})
        self.assertEqual(mapping["GOV-001"]["category"], "operational")

    def test_the_safety_prefix_maps_to_the_assurance_category(self) -> None:
        mapping = hlr.parse_classification(row("HNFR-SAF-001", "SAF-001"))
        self.assertEqual(mapping["SAF-001"]["category"],
                         "cross_cutting_safety_and_assurance_constraint")

    def test_a_repeated_source_id_is_rejected_not_collapsed(self) -> None:
        text = row("HFR-NLI-001", "NLI-001") + row("HOR-NLI-001", "NLI-001")
        with self.assertRaises(ValueError) as caught:
            hlr.parse_classification(text)
        self.assertIn("more than once", str(caught.exception))

    def test_an_unknown_prefix_is_not_read_as_a_category(self) -> None:
        # HXR is not a controlled prefix. It must not silently become a category; the
        # row simply does not parse, and the HLR then has no alias at all.
        mapping = hlr.parse_classification(row("HXR-NLI-001", "NLI-001"))
        self.assertEqual(mapping, {})


class ClassificationValidationTests(unittest.TestCase):
    """Drive validate_classification with each way the corpus could be wrong."""

    def setUp(self) -> None:
        self._quality = hlr.QUALITY_SPEC
        self._tmp = tempfile.TemporaryDirectory()
        # A permissive stand-in, so only the tests that mean to exercise the
        # quality-attribute cross-check are affected by it.
        path = Path(self._tmp.name) / "quality.yaml"
        path.write_text("SAF-001 SAF-002 HFE-001\n", encoding="utf-8")
        hlr.QUALITY_SPEC = path

    def tearDown(self) -> None:
        hlr.QUALITY_SPEC = self._quality
        self._tmp.cleanup()

    def counts(self, functional: int, assurance: int, operational: int):
        """A synthetic corpus with the requested category distribution."""
        recs, mapping = [], {}
        plan = [("HFR", "NLI", "functional", functional),
                ("HNFR", "SAF", "cross_cutting_safety_and_assurance_constraint", assurance),
                ("HOR", "GOV", "operational", operational)]
        for prefix, domain, category, count in plan:
            for index in range(1, count + 1):
                sid = f"{domain}-{index:03d}"
                recs.append({"id": sid, "domain": domain})
                mapping[sid] = {"category_id": f"{prefix}-{domain}-{index:03d}",
                                "category": category}
        return recs, mapping

    def test_the_expected_distribution_is_accepted(self) -> None:
        recs, mapping = self.counts(69, 25, 25)
        hlr.QUALITY_SPEC.write_text(
            " ".join(m for m in mapping if m.startswith("SAF")), encoding="utf-8")
        hlr.validate_classification(recs, mapping)  # must not raise

    def test_an_hlr_with_no_alias_is_rejected(self) -> None:
        recs, mapping = self.counts(69, 25, 25)
        recs.append({"id": "PLN-001", "domain": "PLN"})
        with self.assertRaises(ValueError) as caught:
            hlr.validate_classification(recs, mapping)
        self.assertIn("no category alias", str(caught.exception))

    def test_an_alias_naming_a_missing_hlr_is_rejected(self) -> None:
        recs, mapping = self.counts(69, 25, 25)
        mapping["PLN-999"] = {"category_id": "HFR-PLN-999", "category": "functional"}
        with self.assertRaises(ValueError) as caught:
            hlr.validate_classification(recs, mapping)
        self.assertIn("does not exist", str(caught.exception))

    def test_a_duplicate_category_id_is_rejected(self) -> None:
        recs, mapping = self.counts(69, 25, 25)
        mapping["GOV-001"]["category_id"] = mapping["GOV-002"]["category_id"]
        with self.assertRaises(ValueError) as caught:
            hlr.validate_classification(recs, mapping)
        self.assertIn("duplicate category IDs", str(caught.exception))

    def test_an_alias_pointing_at_the_wrong_requirement_is_rejected(self) -> None:
        # Both ids exist and the counts still balance; only the domains disagree.
        recs, mapping = self.counts(69, 25, 25)
        mapping["GOV-001"]["category_id"] = "HOR-VAL-001"
        with self.assertRaises(ValueError) as caught:
            hlr.validate_classification(recs, mapping)
        self.assertIn("their domains differ", str(caught.exception))

    def test_a_wrong_distribution_is_rejected(self) -> None:
        recs, mapping = self.counts(70, 24, 25)
        with self.assertRaises(ValueError) as caught:
            hlr.validate_classification(recs, mapping)
        self.assertIn("category counts differ", str(caught.exception))

    def test_a_short_corpus_is_rejected(self) -> None:
        recs, mapping = self.counts(68, 25, 25)
        with self.assertRaises(ValueError) as caught:
            hlr.validate_classification(recs, mapping)
        message = str(caught.exception)
        self.assertTrue("118" in message or "category counts differ" in message, message)

    def test_disagreement_with_the_quality_register_is_rejected(self) -> None:
        recs, mapping = self.counts(69, 25, 25)
        hlr.QUALITY_SPEC.write_text("SAF-001\n", encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            hlr.validate_classification(recs, mapping)
        self.assertIn("absent from", str(caught.exception))


class LiveCorpusTests(unittest.TestCase):
    """The committed artifacts, not fixtures."""

    def setUp(self) -> None:
        self.bundle = hlr.build_bundle(hlr.DEFAULT_SOURCE, hlr.DEFAULT_CLASSIFICATION)

    def test_every_record_carries_exactly_one_controlled_category(self) -> None:
        for record in self.bundle["records"]:
            self.assertIn(record["category"], hlr.EXPECTED_CATEGORY_COUNTS, record["id"])
            self.assertTrue(record["category_id"], record["id"])

    def test_the_distribution_is_the_controlled_one(self) -> None:
        counts: dict[str, int] = {}
        for record in self.bundle["records"]:
            counts[str(record["category"])] = counts.get(str(record["category"]), 0) + 1
        self.assertEqual(counts, hlr.EXPECTED_CATEGORY_COUNTS)
        self.assertEqual(sum(counts.values()), 119)

    def test_the_classification_source_is_fingerprinted(self) -> None:
        source = self.bundle["classification_source"]
        self.assertTrue(source["path"].endswith(".tex"))
        self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")

    def test_the_record_fingerprint_still_covers_only_the_hlr_source_row(self) -> None:
        """Adding the category must not change what record_sha256 means.

        It is the fingerprint of the HLR source row and Stage B equivalence compares it
        against that document. Folding in a value from a different document would quietly
        redefine it.
        """
        self.assertEqual(
            next(r["record_sha256"] for r in self.bundle["records"] if r["id"] == "GOV-001"),
            "913189cef6c9b17d7b8c8bbd78d200a8605fd082041fa5d2206f2f8d0ba78448",
        )

    def test_no_category_is_derivable_from_domain_alone(self) -> None:
        """ACC spans all three categories, so a domain shortcut would be wrong.

        This is why the alias table is read per requirement rather than per domain.
        """
        acc = {str(r["category"]) for r in self.bundle["records"]
               if str(r["id"]).startswith("ACC-")}
        self.assertEqual(len(acc), 3, f"expected ACC to span three categories, got {acc}")
