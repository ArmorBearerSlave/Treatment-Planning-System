"""Fixtures for the model-persistence observation gate.

The control this replaces compared `spec/architecture.yaml` with
`mps/bootstrap/language-skeleton.json` and never looked at a model, so it passed for four
checkpoints on a constraint no model satisfied. A gate that compares two declarations
verifies neither; these fixtures exist to show this one reads the disk.

The live test deliberately couples the gate's verdict to MPS-MAT-004B's recorded status
rather than pinning either one. While the acceptance item is open the gate must fail, and
when someone converts the model and closes the item the gate must pass. Neither can move
without the other, which is what stops the divergence going quiet again.
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))

import check_model_persistence as persistence  # noqa: E402

REF = "r:00000000-0000-4000-0000-000000000001(test.corpus.hlr)"
OTHER = "r:00000000-0000-4000-0000-000000000002(test.other)"

MODEL = '<?xml version="1.0" encoding="UTF-8"?>\n<model ref="{ref}">\n  <persistence version="9" />\n</model>\n'


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


class ObservationTests(unittest.TestCase):
    """What the gate sees, given each on-disk shape MPS can produce."""

    def observe(self, files: dict[str, str]) -> list[dict]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative, text in files.items():
                write(root / relative, text)
            return persistence.observe(root)

    def test_a_single_file_model_is_seen_as_single_file(self) -> None:
        observed = self.observe({"corpus/models/test.corpus.hlr.mps": MODEL.format(ref=REF)})
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]["persistence"], persistence.SINGLE_FILE)
        self.assertEqual(observed[0]["reference"], REF)

    def test_a_folder_with_a_dot_model_marker_is_seen_as_file_per_root(self) -> None:
        observed = self.observe({
            "corpus/models/test.corpus.hlr/.model": MODEL.format(ref=REF),
            "corpus/models/test.corpus.hlr/GOV_001.mps": "<node />\n",
            "corpus/models/test.corpus.hlr/GOV_002.mps": "<node />\n",
        })
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]["persistence"], persistence.FILE_PER_ROOT)
        self.assertEqual(observed[0]["root_files"], 2)

    def test_root_files_inside_a_per_root_folder_are_not_counted_as_models(self) -> None:
        # Each root is a .mps file. Counting them as models would report a converted corpus
        # as 119 models rather than one, and the count would look deliberate.
        observed = self.observe({
            "corpus/models/test.corpus.hlr/.model": MODEL.format(ref=REF),
            "corpus/models/test.corpus.hlr/GOV_001.mps": MODEL.format(ref=OTHER),
        })
        self.assertEqual([e["reference"] for e in observed], [REF])

    def test_generated_output_is_not_authored_persistence(self) -> None:
        observed = self.observe({
            "corpus/models/test.corpus.hlr.mps": MODEL.format(ref=REF),
            "languages/lang/source_gen/x/aspectcps-descriptorclasses.mps":
                MODEL.format(ref=OTHER),
            "languages/lang/classes_gen/x/aspectcps-descriptorclasses.mps":
                MODEL.format(ref=OTHER),
        })
        self.assertEqual([e["reference"] for e in observed], [REF])

    def test_a_file_that_is_not_a_model_is_ignored(self) -> None:
        observed = self.observe({
            "corpus/models/test.corpus.hlr.mps": MODEL.format(ref=REF),
            "corpus/models/broken.mps": "not xml at all",
        })
        self.assertEqual([e["reference"] for e in observed], [REF])


class VerdictTests(unittest.TestCase):
    """The gate enforces where a contract binds, and reports everywhere else."""

    def check(self, files: dict[str, str], declared: str, contracted=(REF,)):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative, text in files.items():
                write(root / relative, text)
            return persistence.check(root, declared, contracted)

    def test_a_contracted_model_in_the_declared_mode_passes(self) -> None:
        _, errors = self.check({
            "corpus/models/test.corpus.hlr/.model": MODEL.format(ref=REF),
            "corpus/models/test.corpus.hlr/GOV_001.mps": "<node />\n",
        }, persistence.FILE_PER_ROOT)
        self.assertEqual(errors, [])

    def test_a_contracted_model_in_the_wrong_mode_fails(self) -> None:
        _, errors = self.check({"corpus/models/test.corpus.hlr.mps": MODEL.format(ref=REF)},
                               persistence.FILE_PER_ROOT)
        self.assertEqual(len(errors), 1)
        self.assertIn("is persisted single-file", errors[0])
        self.assertIn("Convert to File-Per-Root Format", errors[0])

    def test_an_uncontracted_model_in_the_other_mode_is_reported_not_failed(self) -> None:
        # The declaration is a project default; only the MPS-4 contract binds a model. A
        # gate that demanded conversion of every language aspect would assert more than any
        # controlled document does.
        observed, errors = self.check({
            "corpus/models/test.corpus.hlr/.model": MODEL.format(ref=REF),
            "corpus/models/test.corpus.hlr/GOV_001.mps": "<node />\n",
            "languages/lang/models/test.other.mps": MODEL.format(ref=OTHER),
        }, persistence.FILE_PER_ROOT)
        self.assertEqual(errors, [])
        self.assertEqual({e["reference"]: e["persistence"] for e in observed}[OTHER],
                         persistence.SINGLE_FILE)

    def test_a_contracted_model_that_is_absent_fails(self) -> None:
        _, errors = self.check({"languages/lang/models/test.other.mps":
                                MODEL.format(ref=OTHER)}, persistence.FILE_PER_ROOT)
        self.assertEqual(len(errors), 1)
        self.assertIn("was not found on disk", errors[0])


class LiveProjectTests(unittest.TestCase):

    def setUp(self) -> None:
        with io.open(REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml",
                     encoding="utf-8") as handle:
            plan = yaml.safe_load(handle.read())
        self.item = next(i for i in plan["acceptance_items"] if i["id"] == "MPS-MAT-004B")

    def test_the_declared_default_is_file_per_root(self) -> None:
        self.assertEqual(persistence.declared_persistence(), persistence.FILE_PER_ROOT)

    def test_the_gate_agrees_with_the_recorded_status_of_mps_mat_004b(self) -> None:
        _, errors = persistence.check(persistence.DEFAULT_PROJECT,
                                      persistence.declared_persistence())
        if self.item["status"] == "complete":
            self.assertEqual(errors, [],
                             "MPS-MAT-004B is recorded complete but the corpus model is not "
                             "persisted as declared")
        else:
            self.assertNotEqual(errors, [],
                                "MPS-MAT-004B is still open, so the gate must still be "
                                "reporting the divergence that keeps it open")

    def test_every_authored_model_is_observed_rather_than_assumed(self) -> None:
        observed = persistence.observe(persistence.DEFAULT_PROJECT)
        self.assertGreater(len(observed), 40)
        self.assertTrue(any(e["reference"].endswith("(nltps.corpus.hlr)") for e in observed))


if __name__ == "__main__":
    unittest.main()
