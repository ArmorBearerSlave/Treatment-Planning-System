"""Job-folder machinery: freezing, hashing, and refusing unbound results."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from pytps.external.jobs import JobError, JobFolder, read_volume, write_volume
from pytps.external.matlab import MatlabError, quote_for_matlab
from pytps.geometry import Grid


def tiny_grid() -> Grid:
    return Grid((4, 3, 2), (2.0, 2.0, 4.0), (-3.0, 1.0, 0.0))


class VolumeExchangeTests(unittest.TestCase):
    """The raw binary layout MATLAB reads back with one fread."""

    def setUp(self) -> None:
        self.grid = tiny_grid()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_float_round_trip(self) -> None:
        array = np.arange(self.grid.voxel_count, dtype=np.float32).reshape(self.grid.dimensions)
        spec = write_volume(self.root / "v.f32", self.grid, array, "float32")
        self.assertEqual(spec.byte_count, self.grid.voxel_count * 4)
        restored = read_volume(self.root / "v.f32", self.grid, "float32", spec.digest)
        self.assertTrue(np.array_equal(restored, array))

    def test_int16_round_trip(self) -> None:
        array = (np.arange(self.grid.voxel_count, dtype=np.int16) % 7).reshape(self.grid.dimensions)
        spec = write_volume(self.root / "v.i16", self.grid, array, "int16")
        restored = read_volume(self.root / "v.i16", self.grid, "int16", spec.digest)
        self.assertTrue(np.array_equal(restored, array))

    def test_bytes_are_little_endian_and_x_fastest(self) -> None:
        """The layout the MATLAB adapters assume, asserted on the actual bytes."""
        array = np.zeros(self.grid.dimensions, dtype=np.float32)
        array[1, 0, 0] = 1.0  # one step in x
        array[0, 1, 0] = 2.0  # one step in y is nx elements later
        array[0, 0, 1] = 3.0  # one step in z is nx*ny elements later
        write_volume(self.root / "v.f32", self.grid, array, "float32")
        raw = np.frombuffer((self.root / "v.f32").read_bytes(), dtype="<f4")
        nx, ny, _ = self.grid.dimensions
        self.assertEqual(float(raw[1]), 1.0)
        self.assertEqual(float(raw[nx]), 2.0)
        self.assertEqual(float(raw[nx * ny]), 3.0)

    def test_truncated_volume_is_rejected(self) -> None:
        array = np.zeros(self.grid.dimensions, dtype=np.float32)
        write_volume(self.root / "v.f32", self.grid, array, "float32")
        (self.root / "v.f32").write_bytes((self.root / "v.f32").read_bytes()[:-8])
        with self.assertRaises(JobError) as caught:
            read_volume(self.root / "v.f32", self.grid, "float32")
        self.assertIn("grid", str(caught.exception))

    def test_altered_volume_fails_its_digest(self) -> None:
        array = np.ones(self.grid.dimensions, dtype=np.float32)
        spec = write_volume(self.root / "v.f32", self.grid, array, "float32")
        write_volume(self.root / "v.f32", self.grid, array * 2.0, "float32")
        with self.assertRaises(JobError):
            read_volume(self.root / "v.f32", self.grid, "float32", spec.digest)

    def test_unknown_dtype_is_rejected(self) -> None:
        with self.assertRaises(JobError):
            write_volume(self.root / "v.bin", self.grid, np.zeros(self.grid.dimensions), "float64")

    def test_missing_volume_is_reported(self) -> None:
        with self.assertRaises(JobError):
            read_volume(self.root / "absent.f32", self.grid, "float32")


class JobFolderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = tiny_grid()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.job = JobFolder.create(self.root, "matrad")
        self.job.add_json("request.json", {"target": "PTV"})
        self.job.add_volume("ct.f32", self.grid, np.zeros(self.grid.dimensions, np.float32), "float32")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_freeze_records_every_input(self) -> None:
        record = self.job.freeze(tools={"matlab": "/somewhere/matlab"})
        files = {entry["file"] for entry in record["inputs"]}
        self.assertEqual(files, {"request.json", "ct.f32"})
        self.assertTrue(all(len(entry["sha256"]) == 64 for entry in record["inputs"]))
        self.assertFalse(record["clinicalUsePermitted"])

    def test_inputs_are_a_list_so_matlab_can_read_the_file_names(self) -> None:
        """MATLAB's jsondecode rewrites field names like "ct.f32"; a list survives."""
        record = self.job.freeze(tools={})
        self.assertIsInstance(record["inputs"], list)
        self.assertIn("ct.f32", [entry["file"] for entry in record["inputs"]])

    def test_a_frozen_job_refuses_more_inputs(self) -> None:
        self.job.freeze(tools={})
        with self.assertRaises(JobError):
            self.job.add_json("late.json", {})

    def test_editing_a_frozen_input_is_detected(self) -> None:
        self.job.freeze(tools={})
        self.job.check_inputs_unchanged()
        self.job.file("request.json").write_text('{"target": "OTHER"}', encoding="utf-8")
        with self.assertRaises(JobError) as caught:
            self.job.check_inputs_unchanged()
        self.assertIn("request.json", str(caught.exception))

    def test_a_result_must_bind_to_the_frozen_inputs(self) -> None:
        record = self.job.freeze(tools={})
        digests = {entry["file"]: entry["sha256"] for entry in record["inputs"]}
        self.job.file("result.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "jobID": record["jobID"],
                    "requestDigest": "0" * 64,
                    "clinicalReleaseAllowed": False,
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaises(JobError) as caught:
            self.job.load_result("result.json", {"requestDigest": digests["request.json"]})
        self.assertIn("different inputs", str(caught.exception))

    def test_a_result_claiming_clinical_release_is_refused(self) -> None:
        self.job.freeze(tools={})
        self.job.file("result.json").write_text(
            json.dumps({"schemaVersion": 1, "clinicalReleaseAllowed": True}), encoding="utf-8"
        )
        with self.assertRaises(JobError) as caught:
            self.job.load_result("result.json", {})
        self.assertIn("clinical release", str(caught.exception))

    def test_a_missing_result_explains_where_to_look(self) -> None:
        self.job.freeze(tools={})
        with self.assertRaises(JobError) as caught:
            self.job.load_result("result.json", {})
        self.assertIn("matlab.log", str(caught.exception))

    def test_job_folders_are_never_reused(self) -> None:
        existing = self.job.path.name
        with self.assertRaises(JobError):
            JobFolder.create(self.root, "matrad", job_id=existing.split("-", 1)[1])


class MatlabQuotingTests(unittest.TestCase):
    def test_a_plain_path_is_single_quoted(self) -> None:
        self.assertEqual(quote_for_matlab("/tmp/job"), "'/tmp/job'")

    def test_a_path_with_a_quote_is_refused(self) -> None:
        for bad in ("/tmp/it's", "/tmp/two\nlines"):
            with self.assertRaises(MatlabError):
                quote_for_matlab(bad)


class ToolDiscoveryTests(unittest.TestCase):
    def test_a_missing_matlab_says_what_to_set(self) -> None:
        from pytps.external.matlab import find_matlab

        with self.assertRaises(MatlabError) as caught:
            find_matlab("/definitely/not/matlab")
        self.assertIn("not found", str(caught.exception))

    def test_a_directory_without_the_marker_is_not_a_checkout(self) -> None:
        from pytps.external.matlab import find_library

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(MatlabError) as caught:
                find_library("matrad", directory)
            self.assertIn("matRad_rc.m", str(caught.exception))

    def test_unknown_library_kind_is_rejected(self) -> None:
        from pytps.external.matlab import find_library

        with self.assertRaises(MatlabError):
            find_library("eclipse")


if __name__ == "__main__":
    unittest.main()
