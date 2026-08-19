from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "repo"))

import build_hlr_import_bundle as hlr  # noqa: E402
import check_language_skeleton as skeleton_check  # noqa: E402
from check_workspace_location import location_findings  # noqa: E402
from schema_subset import validate_json_schema  # noqa: E402


class ControlledToolingTests(unittest.TestCase):
    def test_escaped_ampersand_remains_in_normative_cell(self) -> None:
        source = (
            r"GOV-001 & The system shall preserve Q\&A text. & H-18 & I/A \\" + "\n"
        )
        records = hlr.parse_records(source)
        self.assertEqual(1, len(records))
        self.assertEqual("The system shall preserve Q&A text.", records[0]["normative_text_plain"])
        self.assertEqual(["I", "A"], records[0]["verification_methods"])

    def test_source_metadata_is_parsed_not_hardcoded(self) -> None:
        source = "\n".join(
            (
                r"\NLMeta{Document identifier}{TEST-HLR}",
                r"\NLMeta{Requirements version}{7.3 - Controlled}",
                r"\NLMeta{Date}{19 August 2026}",
            )
        )
        self.assertEqual(
            {
                "document_id": "TEST-HLR",
                "requirements_version": "7.3",
                "source_date": "2026-08-19",
            },
            hlr.parse_source_metadata(source),
        )

    def test_schema_rejects_invalid_bundle(self) -> None:
        bundle = json.loads((REPO_ROOT / "mps" / "import" / "hlr-baseline.json").read_text(encoding="utf-8"))
        schema = json.loads((REPO_ROOT / "mps" / "import" / "hlr-baseline.schema.json").read_text(encoding="utf-8"))
        invalid = copy.deepcopy(bundle)
        invalid["record_count"] = 118
        with self.assertRaisesRegex(ValueError, "record_count"):
            validate_json_schema(invalid, schema)

    def test_location_gate_flags_sync_and_whitespace(self) -> None:
        test_path = "C:" + r"\Users\Example\OneDrive - Institution\Treatment Planning System"
        findings = location_findings(Path(test_path))
        self.assertEqual(["path is inside OneDrive", "path contains whitespace"], findings)

    def test_root_and_non_root_concepts_must_be_disjoint(self) -> None:
        document = json.loads((REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json").read_text(encoding="utf-8"))
        invalid = copy.deepcopy(document["languages"])
        invalid[0]["non_root_concepts"].append(invalid[0]["root_concepts"][0])
        errors, _ = skeleton_check.validate_concept_collections(invalid)
        self.assertTrue(any("both root and non-root" in error for error in errors))

    def test_controlled_schema_ids_are_stable_urns(self) -> None:
        schema_paths = [
            REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.schema.json",
            REPO_ROOT / "mps" / "import" / "hlr-baseline.schema.json",
            *(REPO_ROOT / "spec" / "schemas").glob("*.schema.json"),
        ]
        ids = [json.loads(path.read_text(encoding="utf-8"))["$id"] for path in schema_paths]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(value.startswith("urn:gcpl:nltps:schema:") for value in ids))


if __name__ == "__main__":
    unittest.main()
