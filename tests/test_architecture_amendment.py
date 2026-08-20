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


class StagedInventoryTests(unittest.TestCase):
    """Each checkpoint must own a distinct, correctly allocated inventory.

    Realization was briefly tagged MPS-2, which both charged clinical-intent work with
    realization's concepts and collapsed MPS-3 and MPS-4 onto one ceiling. The defect was
    latent: later checkpoints fail earlier on module presence, so the count was never
    printed. These assertions pin the allocation so it cannot silently collapse again.
    """

    def ceilings(self) -> dict[str, int]:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        return {
            label: graph.expected_concept_count(blueprint, label)
            for label in ("MPS-1", "MPS-2", "MPS-3", "MPS-4")
        }

    def test_staged_inventory_is_forty_sixtyeight_eighty_ninetyseven(self) -> None:
        self.assertEqual(
            self.ceilings(),
            {"MPS-1": 40, "MPS-2": 68, "MPS-3": 80, "MPS-4": 97},
        )

    def test_every_checkpoint_ceiling_is_strictly_larger_than_the_last(self) -> None:
        # A checkpoint that adds languages but not concepts has no distinct inventory,
        # which is exactly the collapse this test exists to catch.
        values = list(self.ceilings().values())
        for earlier, later in zip(values, values[1:]):
            self.assertLess(earlier, later)

    def test_realization_concepts_are_allocated_to_the_final_checkpoint(self) -> None:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        entry = next(e for e in blueprint["languages"] if e["name"] == "nltps.realization")
        self.assertEqual(entry["concepts_materialized_at"], "MPS-4")
        # The module itself has existed since MPS-0; only its inventory moved.
        self.assertEqual(entry["materialized_at"], "MPS-0")

    def test_realization_does_not_contribute_before_its_checkpoint(self) -> None:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        realization = next(
            e for e in blueprint["languages"] if e["name"] == "nltps.realization"
        )
        size = len(realization["root_concepts"]) + len(realization["non_root_concepts"])
        self.assertEqual(
            graph.expected_concept_count(blueprint, "MPS-4")
            - graph.expected_concept_count(blueprint, "MPS-3"),
            size,
        )

    def test_explain_reports_every_declared_checkpoint(self) -> None:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            graph.declared_checkpoints(blueprint),
            ["MPS-0", "MPS-1", "MPS-2", "MPS-3", "MPS-4"],
        )


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


MPL_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<language namespace="{name}" uuid="0000-{idx}">
  <models />
  <accessoryModels />
{dependencies}  <extendedLanguages>{extends}</extendedLanguages>
</language>
"""


class ExternalDependencyTests(unittest.TestCase):
    """POST-MPS1-01: MPS adds dependencies on its own; the gate must notice."""

    def write_module(self, root: Path, name: str, deps: list[str], extends: list[str]) -> None:
        directory = root / name
        directory.mkdir(parents=True, exist_ok=True)
        dep_block = ""
        if deps:
            lines = "".join(
                f'    <dependency reexport="false">uuid({d})</dependency>\n' for d in deps
            )
            dep_block = f"  <dependencies>\n{lines}  </dependencies>\n"
        ext = "".join(f"<extendedLanguage>uuid({e})</extendedLanguage>" for e in extends)
        (directory / f"{name}.mpl").write_text(
            MPL_TEMPLATE.format(name=name, idx=0, dependencies=dep_block, extends=ext),
            encoding="utf-8",
        )

    def test_explicit_external_dependency_is_read_from_the_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_module(root, "nltps.alpha", ["jetbrains.mps.lang.core", "JDK"], [])
            text = (root / "nltps.alpha" / "nltps.alpha.mpl").read_text(encoding="utf-8")
            found = graph.external_refs(text, "nltps.alpha")
            self.assertEqual(found, {"jetbrains.mps.lang.core", "JDK"})

    def test_nltps_dependencies_are_not_counted_as_external(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_module(root, "nltps.alpha", ["nltps.beta"], [])
            text = (root / "nltps.alpha" / "nltps.alpha.mpl").read_text(encoding="utf-8")
            self.assertEqual(graph.external_refs(text, "nltps.alpha"), set())

    def test_module_with_no_dependency_block_has_no_external_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_module(root, "nltps.alpha", [], [])
            text = (root / "nltps.alpha" / "nltps.alpha.mpl").read_text(encoding="utf-8")
            self.assertEqual(graph.external_refs(text, "nltps.alpha"), set())

    def run_gate_over(self, root: Path, blueprint: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            bp = Path(tmp) / "skeleton.json"
            bp.write_text(json.dumps(blueprint), encoding="utf-8")
            original = (graph.BLUEPRINT_PATH, graph.LANGUAGES_ROOT, graph.PROJECT_ROOT)
            graph.BLUEPRINT_PATH = bp
            graph.LANGUAGES_ROOT = root
            graph.PROJECT_ROOT = root.parent
            try:
                errors, _ = graph.check(None, None)
            finally:
                graph.BLUEPRINT_PATH, graph.LANGUAGES_ROOT, graph.PROJECT_ROOT = original
        return errors

    def blueprint_for(self, external: list[str]) -> dict:
        return {
            "project": {"name": "proj"},
            "languages": [
                {
                    "name": "nltps.alpha",
                    "materialized_at": "MPS-0",
                    "concepts_materialized_at": "MPS-1",
                    "dependencies": [],
                    "external_explicit": external,
                    "owns": [],
                    "root_concepts": [],
                    "non_root_concepts": [],
                    "required_constraints": [],
                }
            ],
        }

    def test_undeclared_external_dependency_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            languages = project / "languages"
            languages.mkdir(parents=True)
            self.write_module(languages, "nltps.alpha", ["jetbrains.mps.lang.core"], [])
            errors = self.run_gate_over(languages, self.blueprint_for([]))
        undeclared = [e for e in errors if "UNDECLARED EXTERNAL DEPENDENCY" in e]
        self.assertEqual(len(undeclared), 1, f"expected one rejection, got {errors}")
        message = undeclared[0]
        self.assertIn("module: nltps.alpha", message)
        self.assertIn("dependency: jetbrains.mps.lang.core", message)
        self.assertIn("expected explicit external dependencies: []", message)
        self.assertIn("model-aware tooling", message)

    def test_declared_external_dependency_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            languages = project / "languages"
            languages.mkdir(parents=True)
            self.write_module(languages, "nltps.alpha", ["jetbrains.mps.lang.core"], [])
            errors = self.run_gate_over(
                languages, self.blueprint_for(["jetbrains.mps.lang.core"])
            )
        self.assertEqual([e for e in errors if "EXTERNAL" in e], [])

    def test_declared_but_absent_external_dependency_is_reported(self) -> None:
        # The blueprint must not claim a dependency the descriptor does not carry.
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            languages = project / "languages"
            languages.mkdir(parents=True)
            self.write_module(languages, "nltps.alpha", [], [])
            errors = self.run_gate_over(languages, self.blueprint_for(["JDK"]))
        self.assertTrue(
            any("does not carry it" in e for e in errors),
            f"expected a missing-declared-dependency report, got {errors}",
        )

    def test_live_repository_declares_no_external_dependencies(self) -> None:
        blueprint = json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        for entry in blueprint["languages"]:
            self.assertEqual(
                entry["external_explicit"],
                [],
                f"{entry['name']} declares an external dependency; MPS-1 evidence showed "
                f"none was required",
            )


class GeneratedDocumentLineEndingTests(unittest.TestCase):
    """POST-MPS1-02: the generator must emit canonical LF on every host.

    StringBuilder.AppendLine follows Environment.NewLine, so an unnormalized build
    produced CRLF on Windows and LF on Linux. With .gitattributes pinning LF and the
    -Check comparison byte-exact, that made the same commit pass on CI and fail on every
    Windows workstation. These assertions fail on a machine where it currently happens to
    pass, which is the only way the fix cannot quietly regress.
    """

    SCRIPT = REPO_ROOT / "scripts" / "generate_vv_check_matrix.ps1"
    DOCUMENT = REPO_ROOT / "overleaf" / "NL_TPS_Verification_Validation_Check_Matrix.tex"

    def test_generator_normalizes_before_comparing_or_writing(self) -> None:
        source = self.SCRIPT.read_text(encoding="utf-8")
        assembly = [line for line in source.splitlines() if "$sb.ToString()" in line]
        self.assertEqual(len(assembly), 1, "expected exactly one assembly site")
        self.assertIn(
            ".Replace(", assembly[0],
            "the assembled text must be normalized; without it the byte-exact check is "
            "host-dependent",
        )

    def test_generator_still_compares_byte_exactly(self) -> None:
        # The fix must not have been achieved by weakening the comparison.
        source = self.SCRIPT.read_text(encoding="utf-8")
        self.assertIn("-cne", source, "the drift check must stay case- and byte-exact")

    def test_generated_document_contains_no_carriage_returns(self) -> None:
        data = self.DOCUMENT.read_bytes()
        self.assertEqual(
            data.count(b"\r"), 0,
            "the controlled document carries a carriage return; the generator or the "
            "checkout has reintroduced CRLF",
        )

    def test_generated_document_is_not_empty(self) -> None:
        # Guards against a normalization that silently truncates.
        self.assertGreater(self.DOCUMENT.read_bytes().count(b"\n"), 1000)


if __name__ == "__main__":
    unittest.main()
