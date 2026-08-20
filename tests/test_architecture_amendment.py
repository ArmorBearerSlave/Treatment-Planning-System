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

    def test_staged_inventory_matches_the_frozen_allocation(self) -> None:
        self.assertEqual(
            self.ceilings(),
            {"MPS-1": 40, "MPS-2": 66, "MPS-3": 78, "MPS-4": 95},
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


class FrozenRoleOntologyTests(unittest.TestCase):
    """The MPS-2 role shape, frozen before the feature specification is drafted."""

    def blueprint(self) -> dict:
        return json.loads(graph.BLUEPRINT_PATH.read_text(encoding="utf-8"))

    def language(self, name: str) -> dict:
        return next(e for e in self.blueprint()["languages"] if e["name"] == name)

    def test_superseded_role_and_permission_are_gone(self) -> None:
        names = self.language("nltps.clinicalintent")["non_root_concepts"]
        # ProfessionalRole and OperationalRole replace Role; RoleCapability replaces
        # Permission. Keeping the old names would leave concepts with no semantics.
        self.assertNotIn("Role", names)
        self.assertNotIn("Permission", names)

    def test_clinicalintent_carries_the_authorization_model(self) -> None:
        entry = self.language("nltps.clinicalintent")
        names = set(entry["root_concepts"]) | set(entry["non_root_concepts"])
        for required in (
            "ProfessionalRole",
            "OperationalRole",
            "RoleCapability",
            "AuthorizedActor",
            "AuthorityPolicy",
            "ActionDefinition",
            "WorkflowState",
        ):
            self.assertIn(required, names, required)
        self.assertEqual(len(names), 20)

    def test_roles_common_is_exactly_the_frozen_six(self) -> None:
        entry = self.language("nltps.roles.common")
        self.assertEqual(
            entry["non_root_concepts"],
            [
                "RoleProjection",
                "RoleCommand",
                "SemanticTargetRef",
                "ActionRef",
                "WorkflowStateRef",
                "OperationalRoleRef",
            ],
        )
        self.assertNotIn("CapabilityRef", entry["non_root_concepts"])

    def test_roles_common_declares_no_root(self) -> None:
        # An infrastructure language supplies abstract bases and holders only. Marking an
        # abstract base rootable would advertise a root nobody can instantiate: no MPS
        # platform concept is both abstract and rootable.
        self.assertEqual(self.language("nltps.roles.common")["root_concepts"], [])

    def test_authorization_model_needs_no_roles_common_dependency(self) -> None:
        # RoleCapability is atomic, so clinicalintent never contains a roles.common
        # holder. The reverse edge would close a cycle against roles.common's DEFAULT
        # dependency on clinicalintent.
        deps = {
            d["module"] for d in self.language("nltps.clinicalintent")["dependencies"]
        }
        self.assertNotIn("nltps.roles.common", deps)

    def test_clinicalintent_may_not_contain_a_roles_common_concept(self) -> None:
        closure = features.extends_closure(self.blueprint())
        permitted = {"nltps.clinicalintent"} | closure["nltps.clinicalintent"]
        self.assertNotIn("nltps.roles.common", permitted)

    def test_language_with_no_concepts_at_all_is_still_rejected(self) -> None:
        # Relaxing the root requirement must not let an empty language through.
        sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
        import check_language_skeleton as skeleton

        errors, _ = skeleton.validate_concept_collections(
            [{"name": "nltps.empty", "root_concepts": [], "non_root_concepts": []}]
        )
        self.assertTrue(
            any("declares no concepts at all" in e for e in errors),
            f"an empty language must still fail, got {errors}",
        )

    def test_infrastructure_language_without_a_root_is_accepted(self) -> None:
        sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
        import check_language_skeleton as skeleton

        errors, _ = skeleton.validate_concept_collections(
            [{
                "name": "nltps.holders",
                "root_concepts": [],
                "non_root_concepts": ["BaseThing", "ThingRef"],
            }]
        )
        self.assertEqual(errors, [])

    def test_professional_language_may_contain_a_roles_common_holder(self) -> None:
        closure = features.extends_closure(self.blueprint())
        permitted = {"nltps.roles.radonc"} | closure["nltps.roles.radonc"]
        self.assertIn("nltps.roles.common", permitted)


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


class CrossCheckpointReachabilityTests(unittest.TestCase):
    """Reachability must span checkpoints, or the lapse rule fails silently.

    The non-instantiability deferrals expire when their affected concept gains a
    container. That container arrives in a later checkpoint's feature specification, so
    reading only the MPS-1 file would leave the lapse blind at exactly the checkpoint it
    exists for -- and blind by not firing, which looks identical to compliance.
    """

    def mps2_host_for(self, target: str) -> dict:
        return {
            "datatypes": [],
            "languages": {
                "nltps.clinicalintent": {
                    "concepts": [{
                        "name": "PlanIntentDefinition",
                        "rootable": True,
                        "abstract": False,
                        "superconcept": "BaseConcept",
                        "properties": [],
                        "children": [
                            {"name": "held", "target": target, "cardinality": "0..n"}
                        ],
                        "references": [],
                        "constraints": [],
                    }],
                    "constraints": [],
                }
            },
        }

    def merged_with(self, spec: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            extra = Path(tmp) / "mps2-concept-features.yaml"
            extra.write_text(json.dumps(spec), encoding="utf-8")
            return features.load_features([features.FEATURES_PATH, extra])

    def test_mps2_gave_both_deferred_concepts_a_host(self) -> None:
        # Until the MPS-2 specification existed these were the two unreachable concepts and
        # their deferrals were valid. ConstraintDefinition.limit and EvidenceProfile.citations
        # changed that, which is what lapsed the deferrals.
        unreachable = features.compute_reachability()["unreachable"]
        self.assertNotIn("PhysicalQuantity", unreachable)
        self.assertNotIn("ExternalReference", unreachable)

    def test_only_the_rootless_projection_holders_remain_unreachable(self) -> None:
        # roles.common declares no root by design; its concrete holders are correctly
        # reported until MPS-3 supplies a rootable projection.
        self.assertEqual(
            features.compute_reachability()["unreachable"],
            ["ActionRef", "OperationalRoleRef", "SemanticTargetRef", "WorkflowStateRef"],
        )

    def test_a_later_checkpoint_container_makes_the_concept_reachable(self) -> None:
        merged = self.merged_with(self.mps2_host_for("PhysicalQuantity"))
        unreachable = features.compute_reachability(merged)["unreachable"]
        self.assertNotIn("PhysicalQuantity", unreachable)
        self.assertIn("ExternalReference", unreachable)

    def test_external_reference_host_is_seen_independently(self) -> None:
        merged = self.merged_with(self.mps2_host_for("ExternalReference"))
        unreachable = features.compute_reachability(merged)["unreachable"]
        self.assertNotIn("ExternalReference", unreachable)
        self.assertIn("PhysicalQuantity", unreachable)

    def test_default_load_spans_every_present_specification(self) -> None:
        self.assertEqual(
            [p.name for p in features.feature_specs()],
            ["mps1-concept-features.yaml", "mps2-concept-features.yaml"],
        )

    def test_a_later_specification_resolves_inherited_superconcepts(self) -> None:
        # An MPS-2 concept takes GovernedElement, declared by MPS-1. Resolving names
        # against one file alone would report a legal inheritance as unknown.
        merged = features.load_features()
        clinical = merged["languages"]["nltps.clinicalintent"]["concepts"]
        supers = {c["superconcept"] for c in clinical}
        self.assertEqual(supers, {"GovernedElement"})
        owners = {
            c["name"]
            for body in merged["languages"].values()
            for c in body["concepts"]
        }
        self.assertIn("GovernedElement", owners)


class DeferralTransitionTests(unittest.TestCase):
    """A lapse is an auditable transition; a semantic deferral must not rot unnoticed."""

    def gate(self):
        import check_materialization_plan as plan

        return plan

    def run_with(self, deferrals: list[dict], unreachable: list[str],
                 concepts: list[str]) -> list[str]:
        plan = self.gate()
        import yaml as _yaml

        document = _yaml.safe_load(plan.PLAN_PATH.read_text(encoding="utf-8"))
        for entry in document["acceptance_items"]:
            entry.pop("scoped_exclusions", None)
        document["acceptance_items"][0]["scoped_exclusions"] = deferrals
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.yaml"
            path.write_text(_yaml.safe_dump(document), encoding="utf-8")
            original_path = plan.PLAN_PATH
            original_reach = plan.compute_reachability
            plan.PLAN_PATH = path
            plan.compute_reachability = lambda *a, **k: {
                "unreachable": unreachable,
                "concepts": {name: {} for name in concepts},
            }
            try:
                errors = plan.check()
            finally:
                plan.PLAN_PATH = original_path
                plan.compute_reachability = original_reach
        return [e for e in errors if "deferral" in e]

    def test_active_deferral_over_a_reachable_concept_fails(self) -> None:
        errors = self.run_with(
            [{"constraint": "X-1", "deferral_class": "non_instantiability",
              "affected_concept": "Thing"}],
            unreachable=[], concepts=["Thing"])
        self.assertTrue(any("now reachable" in e for e in errors), errors)

    def test_lapse_declared_before_the_concept_is_reachable_fails(self) -> None:
        # Premature lapse is as wrong as a stale one, and easier to do by accident.
        errors = self.run_with(
            [{"constraint": "X-1", "deferral_class": "non_instantiability",
              "affected_concept": "Thing", "lapsed_at": "MPS-2",
              "carried_to": "MPS-MAT-005B"}],
            unreachable=["Thing"], concepts=["Thing"])
        self.assertTrue(any("may not lapse before" in e for e in errors), errors)

    def test_lapse_without_a_destination_fails(self) -> None:
        errors = self.run_with(
            [{"constraint": "X-1", "deferral_class": "non_instantiability",
              "affected_concept": "Thing", "lapsed_at": "MPS-2"}],
            unreachable=[], concepts=["Thing"])
        self.assertTrue(any("must land on a named checkpoint" in e for e in errors), errors)

    def test_lapse_carried_to_an_unknown_item_fails(self) -> None:
        errors = self.run_with(
            [{"constraint": "X-1", "deferral_class": "non_instantiability",
              "affected_concept": "Thing", "lapsed_at": "MPS-2",
              "carried_to": "MPS-MAT-999"}],
            unreachable=[], concepts=["Thing"])
        self.assertTrue(any("not an acceptance item" in e for e in errors), errors)

    def test_properly_lapsed_deferral_is_accepted(self) -> None:
        errors = self.run_with(
            [{"constraint": "X-1", "deferral_class": "non_instantiability",
              "affected_concept": "Thing", "lapsed_at": "MPS-2",
              "carried_to": "MPS-MAT-005B"}],
            unreachable=[], concepts=["Thing"])
        self.assertEqual(errors, [])

    def test_semantic_deferral_rots_loudly_once_its_concept_arrives(self) -> None:
        # The failure mode CLAUDE.md warns about: this class never lapses on reachability,
        # so without a detector it stays green forever.
        errors = self.run_with(
            [{"constraint": "X-7", "deferral_class": "semantic_model_absence",
              "reactivation_concept": "AuthorizedActor", "status": "deferred"}],
            unreachable=[], concepts=["AuthorizedActor"])
        self.assertTrue(any("does not lapse" in e for e in errors), errors)

    def test_semantic_deferral_stays_quiet_while_its_concept_is_absent(self) -> None:
        errors = self.run_with(
            [{"constraint": "X-7", "deferral_class": "semantic_model_absence",
              "reactivation_concept": "NotYetDeclared", "status": "deferred"}],
            unreachable=[], concepts=["Something"])
        self.assertEqual(errors, [])

    def test_reactivated_deferral_must_name_what_discharges_it(self) -> None:
        errors = self.run_with(
            [{"constraint": "X-7", "deferral_class": "semantic_model_absence",
              "reactivation_concept": "AuthorizedActor", "status": "reactivated at MPS-2"}],
            unreachable=[], concepts=["AuthorizedActor"])
        self.assertTrue(any("realized_by" in e for e in errors), errors)

    def test_live_checklist_records_the_transitions(self) -> None:
        import yaml as _yaml

        plan = self.gate()
        document = _yaml.safe_load(plan.PLAN_PATH.read_text(encoding="utf-8"))
        item = next(i for i in document["acceptance_items"] if i["id"] == "MPS-MAT-005A")
        by_label = {
            (d.get("constraint") or d.get("representation_proof")): d
            for d in item["scoped_exclusions"]
        }
        self.assertTrue(by_label["GOV-C-007"]["status"].startswith("reactivated"))
        self.assertEqual(by_label["GOV-C-007"]["realized_by"], "CLI-C-005")
        for label in ("FND-C-003", "FND-C-004", "PhysicalQuantity.magnitude",
                      "ExternalReference.retrievedDate"):
            self.assertEqual(by_label[label]["lapsed_at"], "MPS-2", label)
            self.assertEqual(by_label[label]["carried_to"], "MPS-MAT-005B", label)


class RoleOntologyFreezeTests(unittest.TestCase):
    """The frozen MPS-2 role shape, and the drifts the gate must refuse."""

    def freeze(self) -> dict:
        import check_role_ontology as ro

        return ro.load(ro.FREEZE_PATH)

    def spec_errors(self, concepts: list[dict], datatypes: list[dict] | None = None) -> list[str]:
        import check_role_ontology as ro

        spec = {
            "datatypes": datatypes if datatypes is not None
            else [{"name": "AutonomyLevelEnum"}, {"name": "ActorKindEnum"}],
            "languages": {"nltps.clinicalintent": {"concepts": concepts}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mps2-concept-features.yaml"
            path.write_text(json.dumps(spec), encoding="utf-8")
            original = ro.FEATURES_PATH
            ro.FEATURES_PATH = path
            try:
                errors, present = ro.check_specification(self.freeze())
            finally:
                ro.FEATURES_PATH = original
        self.assertTrue(present)
        return errors

    def concept(self, name: str, **kw) -> dict:
        base = {"name": name, "properties": [], "children": [], "references": []}
        base.update(kw)
        return base

    def conforming(self) -> list[dict]:
        frozen = self.freeze()["frozen_shape"]
        return [
            self.concept("ProfessionalRole"),
            self.concept("OperationalRole"),
            self.concept("RoleCapability", references=list(frozen["RoleCapability"]["references"])),
            self.concept(
                "ActionDefinition",
                properties=[{"name": "autonomyLevel", "type": "AutonomyLevelEnum",
                             "cardinality": "1"}],
            ),
            self.concept(
                "AuthorizedActor",
                references=list(frozen["AuthorizedActor"]["references"]),
            ),
        ]

    # --- the freeze record itself -----------------------------------------------------

    def test_blueprint_satisfies_the_freeze_now(self) -> None:
        import check_role_ontology as ro

        blueprint = json.loads(ro.BLUEPRINT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(ro.check_blueprint(self.freeze(), blueprint), [])

    def test_authority_class_is_not_the_autonomy_axis(self) -> None:
        # The MPS-1 enum is the ConOps evidence precedence tier and carries no A0-A4.
        import yaml

        mps1 = yaml.safe_load(
            (REPO_ROOT / "mps" / "bootstrap" / "mps1-concept-features.yaml").read_text(
                encoding="utf-8"
            )
        )
        values = next(
            t["values"] for t in mps1["datatypes"] if t["name"] == "AuthorityClassEnum"
        )
        self.assertFalse([v for v in values if v.lower().startswith(("a0", "a4"))])

    def test_autonomy_enum_is_frozen_with_five_levels(self) -> None:
        autonomy = next(
            d for d in self.freeze()["datatypes"] if d["name"] == "AutonomyLevelEnum"
        )
        self.assertEqual(
            autonomy["values"],
            ["A0_inform", "A1_draft", "A2_sandbox_execute", "A3_clinical_candidate",
             "A4_authorize_or_deliver"],
        )

    def test_freeze_does_not_move_the_ceiling(self) -> None:
        impact = self.freeze()["inventory_impact"]
        self.assertEqual(impact["clinicalintent_concepts"], 20)
        self.assertEqual(impact["mps2_cumulative_ceiling"], 66)

    # --- drifts the gate must refuse --------------------------------------------------

    def test_conforming_specification_is_accepted(self) -> None:
        self.assertEqual(self.spec_errors(self.conforming()), [])

    def test_professional_role_linking_to_operational_role_is_rejected(self) -> None:
        concepts = self.conforming()
        concepts[0]["children"] = [
            {"name": "functions", "target": "OperationalRole", "cardinality": "0..n"}
        ]
        errors = self.spec_errors(concepts)
        self.assertTrue(
            any("never stored on" in e for e in errors),
            f"the credential must not carry the mapping, got {errors}",
        )

    def test_capability_with_a_multi_valued_reference_is_rejected(self) -> None:
        concepts = self.conforming()
        for link in concepts[2]["references"]:
            if link["name"] == "operationalRole":
                link["cardinality"] = "0..n"
        errors = self.spec_errors(concepts)
        self.assertTrue(any("the tuple is atomic" in e for e in errors), errors)

    def test_capability_with_children_is_rejected(self) -> None:
        concepts = self.conforming()
        concepts[2]["children"] = [
            {"name": "targets", "target": "ClinicalObjectType", "cardinality": "0..n"}
        ]
        errors = self.spec_errors(concepts)
        self.assertTrue(any("scalar references only" in e for e in errors), errors)

    def test_missing_autonomy_enum_is_rejected(self) -> None:
        errors = self.spec_errors(self.conforming(), datatypes=[{"name": "ActorKindEnum"}])
        self.assertTrue(any("no AutonomyLevelEnum" in e for e in errors), errors)

    def test_action_without_autonomy_level_is_rejected(self) -> None:
        concepts = self.conforming()
        concepts[3]["properties"] = []
        errors = self.spec_errors(concepts)
        self.assertTrue(any("discriminator would be unreadable" in e for e in errors), errors)

    def test_autonomy_typed_as_authority_class_is_rejected(self) -> None:
        # The exact conflation the axis_separation note exists to prevent.
        concepts = self.conforming()
        concepts[3]["properties"] = [
            {"name": "autonomyLevel", "type": "AuthorityClassEnum", "cardinality": "1"}
        ]
        errors = self.spec_errors(concepts)
        self.assertTrue(any("different axes" in e for e in errors), errors)

    def test_multi_valued_actor_role_is_rejected(self) -> None:
        concepts = self.conforming()
        for link in concepts[4]["references"]:
            if link["name"] == "operationalRole":
                link["cardinality"] = "0..n"
        errors = self.spec_errors(concepts)
        self.assertTrue(any("second context instance" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
