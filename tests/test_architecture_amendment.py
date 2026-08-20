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


if __name__ == "__main__":
    unittest.main()
