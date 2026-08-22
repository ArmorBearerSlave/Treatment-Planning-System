"""Fixtures for the imported-HLR root classifier.

The classifier decides what counts as an imported requirement root. Getting that wrong is
expensive in both directions: counting a proof-sandbox requirement inflates the corpus
silently, and failing to count a real root makes it indistinguishable from a root that was
never imported. Worst of all is a root written into a language structure aspect, which
check_module_graph would count as a concept -- the MPS-4 ceiling would read 215 instead of
96, and the number would still look deliberate.

The five fixtures below are the ones hlr_root_classifier.required_fixtures names.
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import check_hlr_root_placement as placement  # noqa: E402
import export_hlr_corpus as exporter  # noqa: E402

IMPORT_MODEL = "r:00000000-0000-4000-0000-000000000001(test.corpus.hlr)"
OTHER_MODEL = "r:00000000-0000-4000-0000-000000000002(test.other)"

# The indices are arbitrary but must match between the registry and the body, exactly as
# MPS writes them. Only the concept and feature names carry meaning for the classifier.
HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<model ref="{ref}">
  <persistence version="9" />
  <languages />
  <imports />
  <registry>
    <language id="08070d1a-4999-4bfd-a38c-2b1b3ffd9ef4" name="nltps.realization">
      <concept id="1" name="nltps.realization.structure.ImportedHLR" flags="ng" index="hlr">
        <property id="11" name="bundleId" index="bid" />
      </concept>
    </language>
    <language id="4709dc1d-8658-45c6-b6ee-185bd2ba1b14" name="nltps.governance">
      <concept id="2" name="nltps.governance.structure.Requirement" flags="ng" index="req" />
    </language>
    <language id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation">
      <concept id="3" name="nltps.foundation.structure.ProvenanceRef" flags="ng" index="prov">
        <property id="31" name="sourcePath" index="spath" />
        <property id="32" name="sourceLine" index="sline" />
        <property id="33" name="sha256" index="sha" />
      </concept>
      <concept id="4" name="nltps.foundation.structure.StableId" flags="ng" index="sid">
        <property id="41" name="value" index="val" />
      </concept>
      <concept id="5" name="nltps.foundation.structure.GovernedElement" flags="ng" index="gov">
        <child id="51" name="provenance" index="pr" />
        <child id="52" name="identifier" index="idf" />
      </concept>
    </language>
  </registry>
"""

RECORD_PROVENANCE = """    <node concept="prov" id="{id}p1" role="pr">
      <property role="spath" value="overleaf/doc.tex" />
      <property role="sline" value="170" />
      <property role="sha" value="aa" />
    </node>
"""

ARTIFACT_PROVENANCE = """    <node concept="prov" id="{id}p2" role="pr">
      <property role="spath" value="overleaf/doc.tex" />
      <property role="sha" value="bb" />
    </node>
"""

# A second entry that also carries a line number: the two can no longer be told apart by
# role, which is exactly REA-C-006's other negative example.
AMBIGUOUS_PROVENANCE = """    <node concept="prov" id="{id}p2" role="pr">
      <property role="spath" value="overleaf/doc.tex" />
      <property role="sline" value="171" />
      <property role="sha" value="bb" />
    </node>
"""


def model(ref: str, roots: str) -> str:
    return HEADER.format(ref=ref) + roots + "</model>\n"


def hlr_root(node_id: str, identifier: str = "GOV-001", provenance: str = "both") -> str:
    body = f'    <node concept="sid" id="{node_id}i" role="idf">\n' \
           f'      <property role="val" value="{identifier}" />\n' \
           f'    </node>\n'
    if provenance in ("both", "record_only", "ambiguous"):
        body += RECORD_PROVENANCE.format(id=node_id)
    if provenance == "both":
        body += ARTIFACT_PROVENANCE.format(id=node_id)
    if provenance == "ambiguous":
        body += AMBIGUOUS_PROVENANCE.format(id=node_id)
    return f'  <node concept="hlr" id="{node_id}">\n' \
           f'    <property role="bid" value="TEST-BUNDLE" />\n' + body + '  </node>\n'


def requirement_root(node_id: str, identifier: str) -> str:
    """A governance Requirement, the shape the proof sandbox actually holds."""
    return (f'  <node concept="req" id="{node_id}">\n'
            f'    <node concept="sid" id="{node_id}i" role="idf">\n'
            f'      <property role="val" value="{identifier}" />\n'
            f'    </node>\n'
            f'  </node>\n')


class ClassifierTests(unittest.TestCase):

    def scan(self, files: dict[str, str]) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative, text in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(text)
            return placement.scan(root, import_model=IMPORT_MODEL)

    def test_a_valid_root_in_the_import_model_is_counted(self) -> None:
        result = self.scan({"corpus/models/test.corpus.hlr.mps":
                            model(IMPORT_MODEL, hlr_root("n1"))})
        self.assertEqual(len(result["counted"]), 1)
        self.assertEqual(result["invalid"], [])

    def test_a_proof_sandbox_identifier_is_not_counted(self) -> None:
        # GOV-001 and GOV-001-1 exist in nltps.proof.cases as governance Requirements. A
        # classifier keyed on identifier shape would count them; this one is keyed on
        # concept and model.
        result = self.scan({
            "sandbox/models/test.proof.cases.mps": model(
                OTHER_MODEL, requirement_root("p1", "GOV-001")
                + requirement_root("p2", "GOV-001-1")),
        })
        self.assertEqual(result["counted"], [])
        self.assertEqual(result["invalid"], [])

    def test_an_imported_root_in_the_wrong_model_is_invalid_placement(self) -> None:
        result = self.scan({"sandbox/models/test.other.mps":
                            model(OTHER_MODEL, hlr_root("n1"))})
        self.assertEqual(result["counted"], [])
        self.assertEqual(len(result["invalid"]), 1)
        self.assertIn("outside the designated import model", result["invalid"][0])

    def test_a_node_in_the_import_model_that_is_not_an_imported_hlr_is_not_counted(self) -> None:
        result = self.scan({"corpus/models/test.corpus.hlr.mps":
                            model(IMPORT_MODEL, requirement_root("r1", "GOV-001"))})
        self.assertEqual(result["counted"], [])
        self.assertEqual(result["invalid"], [])

    def test_an_imported_root_under_a_structure_aspect_is_rejected_not_counted(self) -> None:
        # The expensive failure. Counting it would leave the MPS-4 ceiling reading 215.
        result = self.scan({"languages/testlang/models/testlang.structure.mps":
                            model(IMPORT_MODEL, hlr_root("n1"))})
        self.assertEqual(result["counted"], [])
        self.assertEqual(len(result["invalid"]), 1)
        self.assertIn("structure aspect", result["invalid"][0])

    def test_a_root_with_one_provenance_entry_is_invalid_placement(self) -> None:
        result = self.scan({"corpus/models/test.corpus.hlr.mps":
                            model(IMPORT_MODEL, hlr_root("n1", provenance="record_only"))})
        self.assertEqual(result["counted"], [])
        self.assertIn("two-part provenance", result["invalid"][0])

    def test_two_provenance_entries_that_cannot_be_told_apart_are_invalid(self) -> None:
        result = self.scan({"corpus/models/test.corpus.hlr.mps":
                            model(IMPORT_MODEL, hlr_root("n1", provenance="ambiguous"))})
        self.assertEqual(result["counted"], [])
        self.assertIn("two-part provenance", result["invalid"][0])

    def test_a_misplaced_root_is_reported_rather_than_silently_dropped(self) -> None:
        # Both roots exist; the valid one is counted and the misplaced one is named. A
        # gate that reported only the count would show 1 and look correct.
        result = self.scan({
            "corpus/models/test.corpus.hlr.mps": model(IMPORT_MODEL, hlr_root("n1")),
            "languages/testlang/models/testlang.structure.mps":
                model(IMPORT_MODEL, hlr_root("n2")),
        })
        self.assertEqual(len(result["counted"]), 1)
        self.assertEqual(len(result["invalid"]), 1)


class LiveProjectTests(unittest.TestCase):
    """The live project must satisfy the same rule, not just the fixtures."""

    def test_the_corpus_holds_the_whole_population_and_nothing_is_misplaced(self) -> None:
        result = placement.scan(placement.DEFAULT_PROJECT)
        self.assertEqual(result["invalid"], [])
        self.assertEqual(len(result["counted"]), 119)

    def test_a_structure_aspect_declares_the_concept_but_holds_no_instance(self) -> None:
        # ImportedHLR belongs in the realization structure aspect as a ConceptDeclaration.
        # What must never appear there is an instance of it, which check_module_graph
        # would count as a concept. The distinction is the point of the test: a check
        # that merely grepped for the name would fail on the declaration.
        declared = False
        for path in placement.model_files(placement.DEFAULT_PROJECT):
            if not placement.is_structure_aspect(path, placement.DEFAULT_PROJECT):
                continue
            model = exporter.Model(path)
            for node in model.roots:
                self.assertNotEqual(model.concept(node), exporter.IMPORTED_HLR, path.name)
                if model.prop(node, "name") == "ImportedHLR":
                    declared = True
        self.assertTrue(declared, "ImportedHLR is not declared in any structure aspect")


if __name__ == "__main__":
    unittest.main()
