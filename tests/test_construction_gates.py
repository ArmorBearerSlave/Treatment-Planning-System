"""Negative tests for the construction-phase gates.

Each test drives a gate with the defect it exists to catch. A gate that only ever
sees valid input is not evidence that it works.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "spec"))

import build_trace_graph as trace  # noqa: E402
from mps.schema_subset import validate_json_schema  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "spec" / "schemas"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


CATALOG_ROW = (
    r"\mbox{FC-ACC-01} & Quality & Accreditation Profile Runtime & Publishes approved "
    r"ACR ROPA and ASTRO APEx profiles, resolves scoped applicability, maintains atomic "
    r"trace and evidence state, and prevents system-generated accreditation claims. & T-GOV \\"
)


class ComponentImportTests(unittest.TestCase):
    def test_catalog_row_yields_responsibility_not_layer(self) -> None:
        parts = trace.split_latex_row(CATALOG_ROW)
        self.assertEqual(trace.COMPONENT_CATALOG_COLUMNS, len(parts))
        self.assertEqual("Quality", trace.to_plain(parts[1]))
        self.assertEqual("Accreditation Profile Runtime", trace.to_plain(parts[2]))
        responsibility = trace.to_plain(parts[3])
        self.assertTrue(responsibility.startswith("Publishes approved ACR ROPA"))
        self.assertGreaterEqual(len(responsibility), trace.COMPONENT_RESPONSIBILITY_MIN_CHARS)
        self.assertEqual("T-GOV", trace.to_plain(trace.strip_row_terminator(parts[4])))

    def test_label_length_responsibility_is_rejected(self) -> None:
        entities = {
            "C-X-01": {
                "id": "C-X-01",
                "entity_type": "CORE-COMP",
                "name": "Example",
                "lead_team": "T-SYS",
                "statement_plain": "Universal",
            }
        }
        with self.assertRaisesRegex(ValueError, "responsibility is 9 characters"):
            trace.validate_component_fields(entities)

    def test_cross_view_repetition_is_not_an_import_failure(self) -> None:
        shared = "A" * 80
        entities = {
            "C-SAFE-01": {
                "id": "C-SAFE-01",
                "entity_type": "CORE-COMP",
                "name": "Deterministic Safety Kernel",
                "lead_team": "T-SYS",
                "statement_plain": shared,
            },
            "FC-SAFE-01": {
                "id": "FC-SAFE-01",
                "entity_type": "CAT-COMP",
                "name": "Deterministic Safety Kernel",
                "lead_team": "T-SYS",
                "statement_plain": shared,
            },
        }
        trace.validate_component_fields(entities)

    def test_within_view_repetition_is_an_import_failure(self) -> None:
        shared = "B" * 80
        entities = {
            "C-ONE-01": {
                "id": "C-ONE-01",
                "entity_type": "CORE-COMP",
                "name": "One",
                "lead_team": "T-SYS",
                "statement_plain": shared,
            },
            "C-TWO-01": {
                "id": "C-TWO-01",
                "entity_type": "CORE-COMP",
                "name": "Two",
                "lead_team": "T-SYS",
                "statement_plain": shared,
            },
        }
        with self.assertRaisesRegex(ValueError, "duplicates the responsibility"):
            trace.validate_component_fields(entities)


class MqaTaxonomyTests(unittest.TestCase):
    def test_mqa_identifiers_resolve_to_three_types(self) -> None:
        self.assertEqual("MQA-REQ", trace.mqa_type_for("MQA-001"))
        self.assertEqual("MQA-SUB", trace.mqa_type_for("MQA-001-01"))
        self.assertEqual("MQA-COMP", trace.mqa_type_for("MQA-A01"))

    def test_vv_claim_prefix_differs_per_mqa_class(self) -> None:
        self.assertEqual("VVC-MQA-R:MQA-001", trace.vv_claim_id("MQA-001", "MQA-REQ"))
        self.assertEqual("VVC-MQA-S:MQA-001-01", trace.vv_claim_id("MQA-001-01", "MQA-SUB"))
        self.assertEqual("VVC-MQA-C:MQA-A01", trace.vv_claim_id("MQA-A01", "MQA-COMP"))

    def test_materialized_graph_types_match_declared_counts_per_key(self) -> None:
        document = json.loads(
            (REPO_ROOT / "mps" / "import" / "traceability.json").read_text(encoding="utf-8")
        )
        actual: dict[str, int] = {}
        for record in document["records"]:
            actual[record["entity_type"]] = actual.get(record["entity_type"], 0) + 1
        self.assertEqual(document["entity_type_counts"], actual)
        self.assertEqual(
            {"MQA-REQ": 12, "MQA-SUB": 36, "MQA-COMP": 8},
            {key: actual[key] for key in ("MQA-REQ", "MQA-SUB", "MQA-COMP")},
        )


class SchemaSubsetTests(unittest.TestCase):
    def test_conditional_rule_applies_only_to_its_branch(self) -> None:
        schema = {
            "type": "object",
            "properties": {"kind": {"type": "string"}, "value": {"type": "string"}},
            "allOf": [
                {
                    "if": {"properties": {"kind": {"const": "long"}}, "required": ["kind"]},
                    "then": {"properties": {"value": {"minLength": 10}}},
                }
            ],
        }
        validate_json_schema({"kind": "short", "value": "ok"}, schema)
        with self.assertRaisesRegex(ValueError, "shorter than 10"):
            validate_json_schema({"kind": "long", "value": "ok"}, schema)

    def test_nested_conditionals_evaluate_independently(self) -> None:
        schema = {
            "type": "object",
            "properties": {"a": {"type": "string"}, "b": {"type": "string"}, "c": {"type": "string"}},
            "allOf": [
                {
                    "if": {"properties": {"a": {"const": "x"}}, "required": ["a"]},
                    "then": {
                        "allOf": [
                            {
                                "if": {"properties": {"b": {"const": "y"}}, "required": ["b"]},
                                "then": {"required": ["c"]},
                            }
                        ]
                    },
                }
            ],
        }
        validate_json_schema({"a": "x", "b": "y", "c": "present"}, schema)
        validate_json_schema({"a": "x", "b": "n"}, schema)
        validate_json_schema({"a": "n", "b": "y"}, schema)
        with self.assertRaisesRegex(ValueError, "missing required property 'c'"):
            validate_json_schema({"a": "x", "b": "y"}, schema)

    def test_errors_before_a_conditional_are_not_discarded(self) -> None:
        schema = {
            "type": "object",
            "required": ["missing"],
            "properties": {"k": {"type": "string"}},
            "allOf": [
                {
                    "if": {"properties": {"k": {"const": "q"}}, "required": ["k"]},
                    "then": {"required": ["also_missing"]},
                }
            ],
        }
        with self.assertRaises(ValueError) as caught:
            validate_json_schema({"k": "q"}, schema)
        message = str(caught.exception)
        self.assertIn("'missing'", message)
        self.assertIn("'also_missing'", message)

    def test_type_union_accepts_null(self) -> None:
        schema = {"type": "object", "properties": {"reviewer": {"type": ["string", "null"]}}}
        validate_json_schema({"reviewer": None}, schema)
        validate_json_schema({"reviewer": "name"}, schema)
        with self.assertRaisesRegex(ValueError, "expected"):
            validate_json_schema({"reviewer": 7}, schema)


class ConstructionSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        document = json.loads(
            (REPO_ROOT / "mps" / "import" / "traceability.json").read_text(encoding="utf-8")
        )
        self.trace_by_id = {record["id"]: record for record in document["records"]}
        import yaml

        self.exemplars = yaml.safe_load(
            (REPO_ROOT / "spec" / "construction" / "exemplars.yaml").read_text(encoding="utf-8")
        )

    def test_exemplars_validate(self) -> None:
        for section, schema_name in (
            ("components", "component.schema.json"),
            ("requirements", "requirement.schema.json"),
            ("subrequirements", "subrequirement.schema.json"),
        ):
            schema = load_schema(schema_name)
            for record in self.exemplars[section]:
                validate_json_schema(record, schema)

    def test_name_only_component_is_rejected(self) -> None:
        schema = load_schema("component.schema.json")
        record = copy.deepcopy(self.exemplars["components"][0])
        record["responsibility"] = "Deterministic Safety Kernel"
        with self.assertRaisesRegex(ValueError, "shorter than 60"):
            validate_json_schema(record, schema)

    def test_component_without_an_interface_contract_is_rejected(self) -> None:
        schema = load_schema("component.schema.json")
        record = copy.deepcopy(self.exemplars["components"][0])
        record["interface_contracts"] = []
        with self.assertRaisesRegex(ValueError, "fewer than 1 items"):
            validate_json_schema(record, schema)

    def test_component_without_failure_behavior_is_rejected(self) -> None:
        schema = load_schema("component.schema.json")
        record = copy.deepcopy(self.exemplars["components"][0])
        del record["failure_behavior"]
        with self.assertRaisesRegex(ValueError, "failure_behavior"):
            validate_json_schema(record, schema)

    def test_reviewed_component_requires_source_explicit_hazards(self) -> None:
        schema = load_schema("component.schema.json")
        record = copy.deepcopy(self.exemplars["components"][0])
        record["construction_state"] = "reviewed"
        record["reviewed_by"] = "a reviewer"
        record["review_date"] = "2026-08-19"
        record["hazard_rationale"] = "Reviewed against the ConOps hazard analysis for Zone 1."
        with self.assertRaisesRegex(ValueError, "source_explicit"):
            validate_json_schema(record, schema)
        record["hazard_basis"] = "source_explicit"
        validate_json_schema(record, schema)

    def test_quantitative_acceptance_requires_a_unit_and_tolerance_source(self) -> None:
        schema = load_schema("requirement.schema.json")
        record = copy.deepcopy(self.exemplars["requirements"][0])
        record["acceptance_kind"] = "quantitative"
        with self.assertRaises(ValueError):
            validate_json_schema(record, schema)

    def test_unknown_field_is_rejected(self) -> None:
        schema = load_schema("requirement.schema.json")
        record = copy.deepcopy(self.exemplars["requirements"][0])
        record["priority"] = "high"
        with self.assertRaisesRegex(ValueError, "unexpected properties"):
            validate_json_schema(record, schema)

    def test_inherited_child_cannot_claim_a_constructed_state(self) -> None:
        schema = load_schema("subrequirement.schema.json")
        record = copy.deepcopy(self.exemplars["subrequirements"][0])
        record["treatment"] = "inherited"
        record["construction_state"] = "approved"
        with self.assertRaisesRegex(ValueError, "trace_only"):
            validate_json_schema(record, schema)

    def test_exemplar_hashes_match_the_trace_graph(self) -> None:
        component = self.exemplars["components"][0]
        self.assertEqual(
            self.trace_by_id[component["id"]]["statement_sha256"],
            component["responsibility_sha256"],
        )
        for section in ("requirements", "subrequirements"):
            for record in self.exemplars[section]:
                self.assertEqual(
                    self.trace_by_id[record["id"]]["statement_sha256"],
                    record["canonical_statement_sha256"],
                )


if __name__ == "__main__":
    unittest.main()
