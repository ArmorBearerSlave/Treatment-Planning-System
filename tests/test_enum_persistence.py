"""Negative tests for the enum persistence-integrity gate.

The gate exists because MPS-3 found that writing a foreign enumeration member is accepted
in silence: ok:true from the tool, nothing from the node check, nothing from the model
check, nothing from the build. A gate written for that defect has to be driven with that
defect, or it is only evidence that valid input passes.

Every fixture puts the enumeration declaration and the instance value in *separate model
files*, because the defect is a cross-model resolution failure. A fixture that synthesised
both together could pass while resolving nothing.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import check_enum_persistence as gate  # noqa: E402


STRUCTURE_REF = "r:11111111-1111-4111-1111-111111111111(testlang.structure)"
OTHER_REF = "r:33333333-3333-4333-3333-333333333333(otherlang.structure)"
INSTANCE_REF = "r:22222222-2222-4222-2222-222222222222(testsol.cases)"

STRUCTURE_REGISTRY = """  <registry>
    <language id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure">
      <concept id="3348158742936976480" name="EnumerationMemberDeclaration" index="25R33">
        <property id="1421157252384165432" name="memberId" index="3tVfz5" />
      </concept>
      <concept id="3348158742936976479" name="EnumerationDeclaration" index="25R3W">
        <child id="3348158742936976577" name="members" index="25R1y" />
      </concept>
      <concept id="1071489288299" name="PropertyDeclaration" index="1TJgyi">
        <property id="241647608299431129" name="propertyId" index="IQ2nx" />
        <reference id="1082985295845" name="dataType" index="AX2Wp" />
      </concept>
      <concept id="1071489090640" name="ConceptDeclaration" index="1TIwiD">
        <child id="1071489727084" name="propertyDeclaration" index="1TKVEl" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="INamedConcept" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
"""


def enum_node(node_id: str, name: str, members: list[tuple[str, str]]) -> str:
    body = "".join(
        f"""    <node concept="25R33" id="{node_id}_{mname}" role="25R1y">
      <property role="3tVfz5" value="{mid}" />
      <property role="TrG5h" value="{mname}" />
    </node>
"""
        for mname, mid in members
    )
    return f"""  <node concept="25R3W" id="{node_id}">
    <property role="TrG5h" value="{name}" />
{body}  </node>
"""


def structure_model(ref: str, enums: str, property_decl: str = "", imports: str = "") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<model ref="{ref}">
  <persistence version="9" />
{imports}{STRUCTURE_REGISTRY}{enums}{property_decl}</model>
"""


def concept_with_property(datatype_ref: str) -> str:
    return f"""  <node concept="1TIwiD" id="theConcept">
    <property role="TrG5h" value="Thing" />
    <node concept="1TJgyi" id="theProperty" role="1TKVEl">
      <property role="IQ2nx" value="900900" />
      <property role="TrG5h" value="kind" />
      {datatype_ref}
    </node>
  </node>
"""


def instance_model(value: str, ref: str = INSTANCE_REF, node_id: str = "n1") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<model ref="{ref}">
  <persistence version="9" />
  <registry>
    <language id="99999999-9999-4999-9999-999999999999" name="testlang">
      <concept id="500500" name="testlang.structure.Thing" index="Cx">
        <property id="900900" name="kind" index="Px" />
      </concept>
    </language>
  </registry>
  <node concept="Cx" id="{node_id}">
    <property role="Px" value="{value}" />
  </node>
</model>
"""


class EnumPersistenceGateTests(unittest.TestCase):
    """Drive the real gate over separate structure and instance artifacts."""

    def run_gate(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, text in files.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            original = gate.MPS_ROOT
            gate.MPS_ROOT = root
            try:
                return gate.check()
            finally:
                gate.MPS_ROOT = original

    def scaffold(self, value: str, *, datatype_ref: str | None = None) -> dict[str, str]:
        """Enumeration in one file, the value that must resolve against it in another."""
        enums = (enum_node("enumA", "EnumA", [("a1", "111"), ("a2", "222")])
                 + enum_node("enumB", "EnumB", [("b1", "333")]))
        ref = datatype_ref or '<ref role="AX2Wp" node="enumA" resolve="EnumA" />'
        return {
            "languages/testlang/models/testlang.structure.mps":
                structure_model(STRUCTURE_REF, enums, concept_with_property(ref)),
            "sandbox/testsol/models/testsol.cases.mps": instance_model(value),
        }

    # ---------------------------------------------------------------- controls

    def test_a_declared_member_of_the_declared_enumeration_passes(self) -> None:
        self.assertEqual(self.run_gate(self.scaffold("111/a1")), [])

    def test_a_second_declared_member_also_passes(self) -> None:
        self.assertEqual(self.run_gate(self.scaffold("222/a2")), [])

    # ---------------------------------------------------------------- the MPS-3 shape

    def test_the_mps3_failure_shape_is_rejected(self) -> None:
        # Exactly what MPS persisted when a foreign member was written: a fragment of the
        # attempted name, and null where the resolved member belongs.
        errors = self.run_gate(self.scaffold("al_approval/null"))
        self.assertTrue(
            any("is not a member of the declared enumeration" in e for e in errors),
            f"expected the unresolved-member rejection, got {errors}",
        )
        self.assertTrue(any("'EnumA'" in e for e in errors), errors)

    def test_a_member_of_another_enumeration_is_rejected(self) -> None:
        errors = self.run_gate(self.scaffold("333/b1"))
        self.assertTrue(
            any("not a member of the declared enumeration" in e for e in errors),
            f"expected the foreign-member rejection, got {errors}",
        )

    def test_a_value_with_no_member_id_is_rejected(self) -> None:
        errors = self.run_gate(self.scaffold("/a1"))
        self.assertTrue(any("carries no member id" in e for e in errors), errors)

    def test_a_value_that_is_not_a_member_reference_is_rejected(self) -> None:
        errors = self.run_gate(self.scaffold("a1"))
        self.assertTrue(any("is not a member reference" in e for e in errors), errors)

    def test_a_datatype_that_does_not_resolve_is_rejected(self) -> None:
        errors = self.run_gate(self.scaffold(
            "111/a1", datatype_ref='<ref role="AX2Wp" node="ghostEnum" resolve="Ghost" />'))
        self.assertTrue(
            any("does not resolve to an EnumerationDeclaration" in e for e in errors),
            f"expected the unresolvable-datatype rejection, got {errors}",
        )

    # ---------------------------------------------------------------- cross-model

    def cross_model(self, value: str) -> dict[str, str]:
        """The enumeration lives in a third model, reached through an import index.

        This is the live shape: EvidenceProfile.requiredTier is declared in clinicalintent
        and typed by AuthorityClassEnum, which foundation owns.
        """
        imports = f'  <imports>\n    <import index="oth" ref="{OTHER_REF}" />\n  </imports>\n'
        return {
            "languages/otherlang/models/otherlang.structure.mps": structure_model(
                OTHER_REF, enum_node("farEnum", "FarEnum", [("f1", "777")])),
            "languages/testlang/models/testlang.structure.mps": structure_model(
                STRUCTURE_REF, "",
                concept_with_property('<ref role="AX2Wp" to="oth:farEnum" resolve="FarEnum" />'),
                imports=imports),
            "sandbox/testsol/models/testsol.cases.mps": instance_model(value),
        }

    def test_a_member_of_an_imported_enumeration_passes(self) -> None:
        self.assertEqual(self.run_gate(self.cross_model("777/f1")), [])

    def test_a_foreign_member_against_an_imported_enumeration_is_rejected(self) -> None:
        errors = self.run_gate(self.cross_model("999/notAMember"))
        self.assertTrue(
            any("'FarEnum'" in e and "not a member" in e for e in errors),
            f"expected rejection naming the imported enumeration, got {errors}",
        )

    def test_an_undeclared_import_index_is_rejected(self) -> None:
        files = self.cross_model("777/f1")
        files["languages/testlang/models/testlang.structure.mps"] = structure_model(
            STRUCTURE_REF, "",
            concept_with_property('<ref role="AX2Wp" to="missing:farEnum" resolve="FarEnum" />'))
        errors = self.run_gate(files)
        self.assertTrue(any("is not declared in this model" in e for e in errors), errors)

    # ---------------------------------------------------------------- id stability

    def test_the_same_member_persisting_with_two_ids_is_rejected(self) -> None:
        files = self.scaffold("111/a1")
        files["sandbox/testsol/models/second.cases.mps"] = instance_model(
            "222/a1", ref="r:44444444-4444-4444-4444-444444444444(second.cases)", node_id="n2")
        errors = self.run_gate(files)
        self.assertTrue(
            any("different member ids" in e for e in errors),
            f"expected the id-drift rejection, got {errors}",
        )

    # ---------------------------------------------------------------- teeth

    def test_the_rejection_depends_on_the_membership_check(self) -> None:
        """Bypass the membership rule and the MPS-3 fixture must stop being caught.

        Without this the suite cannot distinguish a gate that checks membership from one
        that rejects everything, or from one that happens to pass for another reason.
        """
        bad = self.scaffold("al_approval/null")
        self.assertTrue(self.run_gate(bad), "fixture must fail while the gate is intact")

        original = gate.check

        def blinded() -> list[str]:
            errors = original()
            return [e for e in errors if "not a member of the declared enumeration" not in e]

        gate.check = blinded
        try:
            self.assertEqual(self.run_gate(bad), [],
                             "with the membership rule removed the defect must go unnoticed")
        finally:
            gate.check = original
        self.assertTrue(self.run_gate(bad), "the gate must be intact again afterwards")

    # ---------------------------------------------------------------- live repository

    def test_the_live_repository_has_no_corrupt_enumeration_value(self) -> None:
        self.assertEqual(gate.check(), [])
