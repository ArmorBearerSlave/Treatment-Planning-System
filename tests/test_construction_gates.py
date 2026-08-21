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
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
import check_module_graph as trace_graph  # noqa: E402
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


class ConceptCountingTests(unittest.TestCase):
    """A structure aspect represents features as nodes too, so counting raw <node>
    elements counts features rather than concepts. These fixtures mirror the MPS
    persistence-9 layout: a registry mapping index aliases to concept types, then
    nodes referencing those aliases."""

    EMPTY = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model ref="r:x(nltps.foundation.structure)">'
        '<persistence version="9" /><languages /><imports /><registry />'
        "</model>"
    )

    # Two concepts carrying seven feature nodes between them.
    POPULATED = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model ref="r:x(nltps.foundation.structure)">'
        '<persistence version="9" />'
        "<registry>"
        '<language id="c72da2b9" name="jetbrains.mps.lang.structure">'
        '<concept id="1071489090640"'
        ' name="jetbrains.mps.lang.structure.structure.ConceptDeclaration"'
        ' flags="ig" index="1TIwiD" />'
        '<concept id="1071489288299"'
        ' name="jetbrains.mps.lang.structure.structure.PropertyDeclaration"'
        ' flags="ig" index="1TJgyj" />'
        '<concept id="1071489288298"'
        ' name="jetbrains.mps.lang.structure.structure.LinkDeclaration"'
        ' flags="ig" index="1TJgyi" />'
        "</language></registry>"
        '<node concept="1TIwiD" id="1"><property role="n" value="GovernedElement" />'
        '<node concept="1TJgyj" id="2" /><node concept="1TJgyj" id="3" />'
        '<node concept="1TJgyi" id="4" /><node concept="1TJgyi" id="5" /></node>'
        '<node concept="1TIwiD" id="6"><node concept="1TJgyj" id="7" />'
        '<node concept="1TJgyi" id="8" /><node concept="1TJgyi" id="9" /></node>'
        "</model>"
    )

    # Nodes present but no ConceptDeclaration registered: unverifiable, must fail closed.
    UNRESOLVABLE = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model ref="r:x(nltps.foundation.structure)">'
        "<registry />"
        '<node concept="unknown" id="1" />'
        "</model>"
    )

    def test_empty_aspect_counts_zero(self) -> None:
        self.assertEqual((0, 0), trace_graph.count_declared_concepts(self.EMPTY))

    def test_features_are_not_counted_as_concepts(self) -> None:
        declared, nodes = trace_graph.count_declared_concepts(self.POPULATED)
        self.assertEqual(2, declared)
        self.assertEqual(9, nodes)
        # The defect this replaces: the raw node count would have reported 9 concepts
        # and tripped a ceiling of 30 after roughly seven real concepts.
        self.assertGreater(nodes, declared)

    def test_ceiling_compares_against_declarations_not_nodes(self) -> None:
        declared, nodes = trace_graph.count_declared_concepts(self.POPULATED)
        ceiling = 3
        self.assertLessEqual(declared, ceiling)
        self.assertGreater(nodes, ceiling)

    def test_unresolvable_registry_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be verified"):
            trace_graph.count_declared_concepts(self.UNRESOLVABLE)


class SessionControlsGateTests(unittest.TestCase):
    """CLAUDE.md is read first by every session and overrides default behaviour, so a
    stale copy makes a session reconstruct removed controls while every other gate
    stays green. Each assertion is driven with the drift it exists to catch."""

    def setUp(self) -> None:
        sys.path.insert(0, str(REPO_ROOT / "tools" / "spec"))
        import check_session_controls

        self.gate = check_session_controls
        self.original = self.gate.CONTROLS_PATH.read_text(encoding="utf-8")

    def tearDown(self) -> None:
        self.gate.CONTROLS_PATH.write_text(self.original, encoding="utf-8", newline="\n")

    def _mutate(self, old: str, new: str) -> list[str]:
        self.assertIn(old, self.original, "fixture anchor missing from CLAUDE.md")
        self.gate.CONTROLS_PATH.write_text(
            self.original.replace(old, new, 1), encoding="utf-8", newline="\n"
        )
        return self.gate.check()[0]

    def test_current_file_passes(self) -> None:
        self.assertEqual([], self.gate.check()[0])

    def test_dropping_a_checkpoint_is_rejected(self) -> None:
        errors = self._mutate("    MPS-4  realization", "    XXX-4  realization")
        self.assertTrue(any("describes checkpoints" in e for e in errors))

    def test_claiming_an_open_checkpoint_is_closed_is_rejected(self) -> None:
        # MPS-3 is the open checkpoint now that MPS-2 has closed; the fixture tracks
        # the frontier rather than naming a checkpoint that has since been accepted.
        errors = self._mutate(
            "    MPS-3  the four professional role projections",
            "    MPS-3  the four professional role projections       closed",
        )
        self.assertTrue(any("marks MPS-3 closed" in e for e in errors))

    def test_prescribing_a_missing_script_is_rejected(self) -> None:
        errors = self._mutate(
            "python tools/mps/check_role_ontology.py",
            "python tools/mps/check_nonexistent_thing.py",
        )
        self.assertTrue(any("script is missing" in e for e in errors))

    def test_citing_a_missing_path_is_rejected(self) -> None:
        errors = self._mutate(
            "`mps/bootstrap/mps2-role-ontology.yaml`",
            "`mps/bootstrap/does-not-exist.yaml`",
        )
        self.assertTrue(any("path that does not exist" in e for e in errors))

    def test_unexplained_deferral_class_is_rejected(self) -> None:
        errors = self._mutate("`literal_example_substitution`", "`some_other_class`")
        self.assertTrue(any("literal_example_substitution" in e for e in errors))

    def test_retired_invocation_is_rejected(self) -> None:
        errors = self._mutate(
            "python tools/mps/check_module_graph.py --checkpoint MPS-N",
            "python tools/mps/check_module_graph.py --max-concepts <checkpoint bound>",
        )
        self.assertTrue(any("still prescribes" in e for e in errors))

    def test_checklist_and_plan_gate_agree_on_checkpoints(self) -> None:
        self.assertEqual(self.gate.plan_checkpoints(), self.gate.gate_checkpoints())

    def test_closure_is_derived_from_acceptance_state(self) -> None:
        closed = self.gate.closed_checkpoints()
        self.assertIn("MPS-0", closed)
        self.assertIn("MPS-1", closed)
        self.assertIn("MPS-2", closed)
        self.assertNotIn("MPS-3", closed)
        self.assertNotIn("MPS-4", closed)
