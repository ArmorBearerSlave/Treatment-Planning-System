"""Negative tests for the neutral export and the Stage B equivalence comparison.

An equivalence check that cannot fail is worse than none: it produces a green table for
119 requirements while comparing nothing. Every test here is a way the model could differ
from the controlled source, and every one of them must be caught and named.

The failure categories come from mps4-concept-features.yaml, equivalence_contract. A
category that no test drives is a category nothing has shown to work.
"""

from __future__ import annotations

import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import check_stage_b_equivalence as stage_b  # noqa: E402
import export_hlr_corpus as exporter  # noqa: E402

# Resolved rather than spelled out: the corpus is a single file or a folder of roots
# depending on its persistence mode, and this suite must not care which.
MODEL = exporter.corpus_model()
BUNDLE = REPO_ROOT / "mps" / "import" / "hlr-baseline.json"
EXPORT = REPO_ROOT / "mps" / "import" / "hlr-corpus-export.json"


def load(path: Path):
    with io.open(path, encoding="utf-8") as handle:
        return json.loads(handle.read())


class ExportShapeTests(unittest.TestCase):
    """The export carries the canonical fields and none of the excluded ones."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.records = load(EXPORT)

    def test_the_export_covers_the_whole_corpus(self) -> None:
        self.assertEqual(len(self.records), load(BUNDLE)["record_count"])

    def test_every_canonical_field_is_present_on_every_record(self) -> None:
        canonical = {"id", "domain", "category", "category_id", "statement_latex",
                     "verification_methods", "hazards", "source_hazard_text",
                     "record_provenance", "source_artifact_provenance", "lifecycle_state",
                     "authoritative", "bundle_id"}
        for record in self.records:
            self.assertEqual(set(record), canonical, record.get("id"))

    def test_no_mps_identity_leaks_into_the_export(self) -> None:
        # Node ids, model references and the model filename are representation. If any of
        # them reached the export, the export would stop being comparable to the document.
        with io.open(EXPORT, encoding="utf-8") as handle:
            text = handle.read()
        for leaked in ("nltps.corpus.hlr", "r:42669edd", ".mps", "1365532761"):
            self.assertNotIn(leaked, text, leaked)

    def test_records_are_ordered_by_id(self) -> None:
        ids = [r["id"] for r in self.records]
        self.assertEqual(ids, sorted(ids))

    def test_the_file_is_lf_with_a_trailing_newline(self) -> None:
        with io.open(EXPORT, "rb") as handle:
            raw = handle.read()
        self.assertNotIn(b"\r\n", raw)
        self.assertTrue(raw.endswith(b"\n"))

    def test_the_export_is_reproducible_from_the_model(self) -> None:
        rebuilt = json.dumps(exporter.export(MODEL), indent=2, sort_keys=True,
                             ensure_ascii=False) + "\n"
        with io.open(EXPORT, encoding="utf-8", newline="") as handle:
            self.assertEqual(rebuilt, handle.read())


class EquivalenceFailureTests(unittest.TestCase):
    """Drive every named failure category by perturbing one exported record."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = load(BUNDLE)
        cls.export = load(EXPORT)
        cls.identity = stage_b.root_identity(MODEL)

    def run_against(self, records) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            export_path = Path(tmp) / "export.json"
            table_path = Path(tmp) / "table.csv"
            with io.open(export_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(records))
            _, problems = stage_b.run(BUNDLE, export_path, MODEL, table_path)
            return problems

    def perturb(self, index: int, **changes):
        records = copy.deepcopy(self.export)
        records[index].update(changes)
        return records

    def assertCategory(self, problems, category) -> None:
        self.assertTrue(problems, "the comparison reported nothing")
        self.assertTrue(any(p.startswith(category + ":") for p in problems),
                        f"{category} not among {problems[:4]}")

    def test_an_unperturbed_export_is_equivalent(self) -> None:
        # The positive control. Without it, a check that rejects everything would pass
        # every test below.
        self.assertEqual(self.run_against(self.export), [])

    def test_a_changed_statement_is_a_text_mismatch(self) -> None:
        self.assertCategory(self.run_against(
            self.perturb(0, statement_latex="something else")), "text_mismatch")

    def test_a_changed_identifier_is_a_missing_root(self) -> None:
        # Renaming the id makes one source id unrepresented and adds one the source does
        # not have; both must be reported rather than netting out to zero.
        problems = self.run_against(self.perturb(0, id="NOT-A-REAL-ID"))
        self.assertCategory(problems, "missing_root")
        self.assertCategory(problems, "extra_root")

    def test_a_duplicated_record_is_a_duplicate_root(self) -> None:
        records = copy.deepcopy(self.export)
        records.append(copy.deepcopy(records[0]))
        self.assertCategory(self.run_against(records), "duplicate_root")

    def test_a_changed_domain_is_a_feature_mismatch(self) -> None:
        self.assertCategory(self.run_against(self.perturb(0, domain="SAF")),
                            "feature_mismatch")

    def test_a_changed_category_id_is_a_feature_mismatch(self) -> None:
        self.assertCategory(self.run_against(self.perturb(0, category_id="HFR-ZZZ-999")),
                            "feature_mismatch")

    def test_a_dropped_verification_method_is_a_feature_mismatch(self) -> None:
        self.assertCategory(self.run_against(self.perturb(0, verification_methods=["I"])),
                            "feature_mismatch")

    def test_a_changed_record_hash_is_a_provenance_mismatch(self) -> None:
        record = copy.deepcopy(self.export[0]["record_provenance"])
        record["sha256"] = "0" * 64
        self.assertCategory(self.run_against(self.perturb(0, record_provenance=record)),
                            "provenance_mismatch")

    def test_a_changed_source_line_is_a_provenance_mismatch(self) -> None:
        record = copy.deepcopy(self.export[0]["record_provenance"])
        record["source_line"] = record["source_line"] + 1
        self.assertCategory(self.run_against(self.perturb(0, record_provenance=record)),
                            "provenance_mismatch")

    def test_a_changed_artifact_hash_is_a_provenance_mismatch(self) -> None:
        artifact = copy.deepcopy(self.export[0]["source_artifact_provenance"])
        artifact["sha256"] = "0" * 64
        self.assertCategory(
            self.run_against(self.perturb(0, source_artifact_provenance=artifact)),
            "provenance_mismatch")

    def test_a_lifecycle_state_other_than_proposed_is_a_lifecycle_mismatch(self) -> None:
        self.assertCategory(self.run_against(self.perturb(0, lifecycle_state="approved")),
                            "lifecycle_mismatch")

    def test_an_authoritative_root_is_a_feature_mismatch(self) -> None:
        self.assertCategory(self.run_against(self.perturb(0, authoritative=True)),
                            "feature_mismatch")

    def test_a_changed_source_hazard_text_is_a_hazard_mismatch(self) -> None:
        self.assertCategory(self.run_against(self.perturb(0, source_hazard_text="H-01")),
                            "hazard_mismatch")

    def test_an_added_hazard_is_a_hazard_mismatch(self) -> None:
        # This is the curated-analysis import the mirror exists to refuse. SAF-001's source
        # row names H-04 and nothing else; spec/allocations.yaml also gives it H-13 and
        # H-18, and importing those would make Stage B compare the model against an
        # analysis rather than against the document.
        index = next(i for i, r in enumerate(self.export) if r["id"] == "SAF-001")
        problems = self.run_against(
            self.perturb(index, hazards=["H-04", "H-13", "H-18"]))
        self.assertCategory(problems, "hazard_mismatch")
        self.assertTrue(any("not named in this requirement" in p for p in problems),
                        problems[:4])

    def test_a_dropped_hazard_is_a_hazard_mismatch(self) -> None:
        index = next(i for i, r in enumerate(self.export) if r["id"] == "SAF-001")
        self.assertCategory(self.run_against(self.perturb(index, hazards=[])),
                            "hazard_mismatch")


class MirrorFidelityTests(unittest.TestCase):
    """What the model holds is the source row, not the downstream hazard analysis."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.export = {r["id"]: r for r in load(EXPORT)}

    def test_the_frozen_hazard_profile_is_reproduced(self) -> None:
        expected = load(BUNDLE)["expected_hazard_allocation"]
        with_hazards = [r for r in self.export.values() if r["hazards"]]
        links = sum(len(r["hazards"]) for r in self.export.values())
        distinct = {h for r in self.export.values() for h in r["hazards"]}
        self.assertEqual(len(with_hazards), expected["records_with_hazards"])
        self.assertEqual(len(self.export) - len(with_hazards),
                         expected["records_without_hazards"])
        self.assertEqual(len(distinct), expected["distinct_hazards"])
        self.assertEqual(links, expected["total_links"])

    def test_saf_001_carries_only_the_hazard_its_source_row_names(self) -> None:
        self.assertEqual(self.export["SAF-001"]["hazards"], ["H-04"])

    def test_saf_005_carries_only_the_hazard_its_source_row_names(self) -> None:
        self.assertEqual(self.export["SAF-005"]["hazards"], ["H-16"])

    def test_a_requirement_whose_source_row_names_no_hazard_carries_none(self) -> None:
        for source_id in ("GOV-001", "SAF-006", "SAF-008"):
            self.assertEqual(self.export[source_id]["hazards"], [], source_id)

    def test_the_source_hazard_text_is_kept_even_where_no_hazard_was_typed(self) -> None:
        # The distinction the mirror has to preserve: not converted into a typed link is
        # not the same as not preserved.
        self.assertEqual(self.export["GOV-001"]["source_hazard_text"], "SCP; PRN; AUTH")
        self.assertEqual(self.export["GOV-001"]["hazards"], [])

    def test_the_latex_form_of_the_hazard_column_is_the_one_kept(self) -> None:
        # The plain form is a review projection. These four rows are where they differ.
        self.assertEqual(self.export["ACC-004"]["source_hazard_text"],
                         "APEx 1--3,14; ROPA; H-01,H-04,H-12")
        self.assertEqual(self.export["ACC-006"]["source_hazard_text"],
                         "APEx 11--12; ACR--AAPM TPS; H-08,H-15")

    def test_no_root_claims_to_be_authoritative(self) -> None:
        self.assertTrue(all(r["authoritative"] is False for r in self.export.values()))

    def test_every_root_sits_at_the_one_stage_a_lifecycle_state(self) -> None:
        self.assertEqual({r["lifecycle_state"] for r in self.export.values()}, {"proposed"})


if __name__ == "__main__":
    unittest.main()
