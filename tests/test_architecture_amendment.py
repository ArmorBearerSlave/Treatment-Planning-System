"""Negative tests for the post-MPS-1 architecture-amendment gates.

Each gate added by the amendment is driven with the defect it exists to catch. A gate
that has only ever seen valid input is not evidence that it works, and these gates were
written before the architecture they police exists, so the fixtures are synthetic
blueprints rather than the live one.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import check_module_graph as graph  # noqa: E402
import check_concept_features as features  # noqa: E402


def language(
    name: str,
    *,
    materialized_at: str = "MPS-0",
    concepts_at: str = "MPS-1",
    dependencies: list[dict] | None = None,
    roots: list[str] | None = None,
    nonroots: list[str] | None = None,
) -> dict:
    return {
        "name": name,
        "materialized_at": materialized_at,
        "concepts_materialized_at": concepts_at,
        "dependencies": dependencies or [],
        "owns": [],
        "root_concepts": roots or [],
        "non_root_concepts": nonroots or [],
        "required_constraints": [],
    }


class CheckpointScopingTests(unittest.TestCase):
    """A blueprint must be able to declare a language before it is materialized."""

    def setUp(self) -> None:
        self.blueprint = {
            "languages": [
                language("a.now", materialized_at="MPS-0"),
                language("a.later", materialized_at="MPS-3"),
            ]
        }

    def test_language_declared_for_a_later_checkpoint_is_out_of_scope(self) -> None:
        in_scope = [e["name"] for e in graph.languages_at(self.blueprint, "MPS-1")]
        self.assertEqual(in_scope, ["a.now"])

    def test_language_is_in_scope_once_its_checkpoint_arrives(self) -> None:
        in_scope = [e["name"] for e in graph.languages_at(self.blueprint, "MPS-3")]
        self.assertEqual(in_scope, ["a.now", "a.later"])

    def test_no_checkpoint_means_the_whole_declared_inventory(self) -> None:
        in_scope = [e["name"] for e in graph.languages_at(self.blueprint, None)]
        self.assertEqual(in_scope, ["a.now", "a.later"])

    def test_malformed_checkpoint_label_is_rejected_not_treated_as_zero(self) -> None:
        with self.assertRaises(ValueError):
            graph.checkpoint_ordinal("MPS1")
        with self.assertRaises(ValueError):
            graph.checkpoint_ordinal("")

    def test_ceiling_counts_only_inventories_that_have_arrived(self) -> None:
        blueprint = {
            "languages": [
                language("a.early", concepts_at="MPS-1", roots=["R1"], nonroots=["N1", "N2"]),
                language("a.late", concepts_at="MPS-4", roots=["R2"], nonroots=["N3"]),
            ]
        }
        self.assertEqual(graph.expected_concept_count(blueprint, "MPS-1"), 3)
        self.assertEqual(graph.expected_concept_count(blueprint, "MPS-4"), 5)

    def test_empty_module_contributes_no_concepts_before_its_inventory_lands(self) -> None:
        # The distinction the two fields exist for: the module is present from MPS-0 but
        # charging its inventory to MPS-0 would make the ceiling wrong.
        blueprint = {
            "languages": [
                language(
                    "a.mod", materialized_at="MPS-0", concepts_at="MPS-2", nonroots=["N1"]
                )
            ]
        }
        self.assertEqual(graph.expected_concept_count(blueprint, "MPS-0"), 0)
        self.assertEqual(graph.expected_concept_count(blueprint, "MPS-2"), 1)


class LiveBlueprintDerivationTests(unittest.TestCase):
    """The MPS-1 ceiling must come from the blueprint, not a literal."""

    def test_mps1_ceiling_is_derived_as_forty(self) -> None:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(graph.expected_concept_count(blueprint, "MPS-1"), 40)

    def test_mps0_ceiling_is_derived_as_zero(self) -> None:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(graph.expected_concept_count(blueprint, "MPS-0"), 0)

    def test_every_declared_language_carries_both_checkpoints(self) -> None:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        for entry in blueprint["languages"]:
            self.assertIn("materialized_at", entry, entry["name"])
            self.assertIn("concepts_materialized_at", entry, entry["name"])
            graph.checkpoint_ordinal(entry["materialized_at"])
            graph.checkpoint_ordinal(entry["concepts_materialized_at"])


class TransitiveExtendsTests(unittest.TestCase):
    """Superconcept and containment legality both resolve through the EXTENDS chain."""

    def blueprint(self) -> dict:
        # core <- common <- prof, plus a DEFAULT-only sibling that must not confer rights.
        return {
            "languages": [
                language("core"),
                language("side"),
                language(
                    "common",
                    dependencies=[
                        {"module": "core", "kind": "EXTENDS"},
                        {"module": "side", "kind": "DEFAULT"},
                    ],
                ),
                language(
                    "prof",
                    dependencies=[{"module": "common", "kind": "EXTENDS"}],
                ),
            ]
        }

    def test_closure_reaches_through_the_chain(self) -> None:
        closure = features.extends_closure(self.blueprint())
        self.assertEqual(closure["prof"], {"common", "core"})
        self.assertEqual(closure["common"], {"core"})
        self.assertEqual(closure["core"], set())

    def test_default_dependency_never_enters_the_closure(self) -> None:
        closure = features.extends_closure(self.blueprint())
        self.assertNotIn("side", closure["common"])
        self.assertNotIn("side", closure["prof"])

    def test_two_hop_superconcept_is_accepted(self) -> None:
        # prof EXTENDS common EXTENDS core, so a core superconcept is two hops away.
        closure = features.extends_closure(self.blueprint())
        permitted = {"prof"} | closure["prof"]
        self.assertIn("core", permitted, "two-hop superconcept must be legal")

    def test_superconcept_from_a_default_only_target_is_rejected(self) -> None:
        closure = features.extends_closure(self.blueprint())
        permitted = {"common"} | closure["common"]
        self.assertNotIn("side", permitted, "DEFAULT must not confer superconcept rights")

    def test_containment_of_an_extends_ancestor_concept_is_accepted(self) -> None:
        closure = features.extends_closure(self.blueprint())
        permitted = {"prof"} | closure["prof"]
        self.assertIn("common", permitted)
        self.assertIn("core", permitted)

    def test_containment_of_a_default_only_concept_is_rejected(self) -> None:
        closure = features.extends_closure(self.blueprint())
        permitted = {"common"} | closure["common"]
        self.assertNotIn("side", permitted, "DEFAULT permits references, not containment")

    def test_cycle_terminates_instead_of_recursing(self) -> None:
        cyclic = {
            "languages": [
                language("a", dependencies=[{"module": "b", "kind": "EXTENDS"}]),
                language("b", dependencies=[{"module": "a", "kind": "EXTENDS"}]),
            ]
        }
        closure = features.extends_closure(cyclic)
        # Terminates, and a language is never its own ancestor.
        self.assertEqual(closure["a"], {"b"})
        self.assertEqual(closure["b"], {"a"})


class ContainmentGateTests(unittest.TestCase):
    """Drive the real gate, not just the helper, over a synthetic specification."""

    def run_gate(self, blueprint: dict, spec: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            bp = Path(tmp) / "skeleton.json"
            fp = Path(tmp) / "features.yaml"
            bp.write_text(json.dumps(blueprint), encoding="utf-8")
            fp.write_text(json.dumps(spec), encoding="utf-8")  # YAML is a JSON superset
            original = (features.BLUEPRINT_PATH, features.FEATURES_PATH)
            features.BLUEPRINT_PATH, features.FEATURES_PATH = bp, fp
            try:
                errors, _ = features.check()
            finally:
                features.BLUEPRINT_PATH, features.FEATURES_PATH = original
        return errors

    def concept(self, name: str, *, superconcept: str, children: list[dict] | None = None) -> dict:
        return {
            "name": name,
            "rootable": False,
            "abstract": False,
            "superconcept": superconcept,
            "intent": "fixture",
            "editor": "<name>",
            "properties": [],
            "children": children or [],
            "references": [],
            "constraints": [],
        }

    def scaffold(self, prof_children: list[dict], prof_super: str) -> tuple[dict, dict]:
        blueprint = {
            "languages": [
                language("core", roots=[], nonroots=["CoreThing"]),
                language("side", roots=[], nonroots=["SideThing"]),
                language(
                    "common",
                    dependencies=[
                        {"module": "core", "kind": "EXTENDS"},
                        {"module": "side", "kind": "DEFAULT"},
                    ],
                    nonroots=["CommonThing"],
                ),
                language(
                    "prof",
                    dependencies=[{"module": "common", "kind": "EXTENDS"}],
                    roots=["ProfRoot"],
                    nonroots=[],
                ),
            ]
        }
        spec = {
            "datatypes": [],
            "languages": {
                "core": {"concepts": [self.concept("CoreThing", superconcept="BaseConcept")],
                         "constraints": []},
                "side": {"concepts": [self.concept("SideThing", superconcept="BaseConcept")],
                         "constraints": []},
                "common": {"concepts": [self.concept("CommonThing", superconcept="BaseConcept")],
                           "constraints": []},
                "prof": {
                    "concepts": [
                        {
                            "name": "ProfRoot",
                            "rootable": True,
                            "abstract": False,
                            "superconcept": prof_super,
                            "intent": "fixture",
                            "editor": "<name>",
                            "properties": [],
                            "children": prof_children,
                            "references": [],
                            "constraints": [],
                        }
                    ],
                    "constraints": [],
                },
            },
        }
        return blueprint, spec

    def test_two_hop_superconcept_accepted_by_the_gate(self) -> None:
        blueprint, spec = self.scaffold([], "CoreThing")
        errors = self.run_gate(blueprint, spec)
        self.assertEqual([e for e in errors if "superconcept" in e or "EXTENDS" in e], [])

    def test_superconcept_from_default_only_rejected_by_the_gate(self) -> None:
        blueprint, spec = self.scaffold([], "SideThing")
        errors = self.run_gate(blueprint, spec)
        self.assertTrue(
            any("SideThing" in e and "EXTENDS" in e for e in errors),
            f"expected a DEFAULT-superconcept rejection, got {errors}",
        )

    def test_containment_of_extends_ancestor_accepted_by_the_gate(self) -> None:
        child = {"name": "held", "target": "CoreThing", "cardinality": "0..n"}
        blueprint, spec = self.scaffold([child], "BaseConcept")
        errors = self.run_gate(blueprint, spec)
        self.assertEqual([e for e in errors if "contains" in e], [])

    def test_containment_of_default_only_rejected_by_the_gate(self) -> None:
        child = {"name": "held", "target": "SideThing", "cardinality": "0..n"}
        blueprint, spec = self.scaffold([child], "BaseConcept")
        errors = self.run_gate(blueprint, spec)
        self.assertTrue(
            any("contains SideThing" in e for e in errors),
            f"expected a containment rejection, got {errors}",
        )


if __name__ == "__main__":
    unittest.main()
