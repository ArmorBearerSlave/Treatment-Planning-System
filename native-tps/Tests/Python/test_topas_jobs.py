import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/topas_jobs.py'
spec = importlib.util.spec_from_file_location('topas_jobs', SCRIPT)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class TopasJobsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        bridge.ROOT = self.root / 'jobs'
        bridge.RUNNER = self.root / 'runner'
        bridge.ENGINE = self.root / 'engine'
        bridge.RUNNER.write_text('runner')
        bridge.ENGINE.write_text('engine')
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'field.txt').write_text('includeFile = materials.txt\ns:Ge/P/InputDirectory = "./"\ns:Ge/P/InputFile = "ct.bin"\ns:Sc/D/OutputFile = "dose"\n')
        (self.source / 'materials.txt').write_text('# materials\n')
        (self.source / 'ct.bin').write_bytes(b'volume')
        self.request = dict(source=str(self.source), files=['field.txt', 'materials.txt', 'ct.bin'], macros=['field.txt'], worker=base64.b64encode(SCRIPT.read_bytes()).decode())

    def tearDown(self):
        self.temp.cleanup()

    def test_snapshot_isolated_and_hashed(self):
        result = bridge.prepare(self.request)
        (self.source / 'ct.bin').write_bytes(b'changed')
        self.assertEqual((bridge.job_path(result['id']) / 'inputs/ct.bin').read_bytes(), b'volume')
        self.assertEqual(result['state'], 'prepared')
        self.assertFalse(result['clinicalReleaseAllowed'])

    def test_missing_include_and_traversal_rejected(self):
        with self.assertRaises(ValueError): bridge.prepare(dict(self.request, files=['field.txt', 'ct.bin']))
        with self.assertRaises(ValueError): bridge.prepare(dict(self.request, files=['../runner']))
        with self.assertRaises(ValueError): bridge.job_path('../../etc')

    def test_symlink_and_output_collision_rejected(self):
        (self.source / 'link').symlink_to(bridge.ENGINE)
        with self.assertRaises(ValueError): bridge.prepare(dict(self.request, files=self.request['files'] + ['link']))
        (self.source / 'dose.bin').write_bytes(b'old')
        with self.assertRaises(ValueError): bridge.prepare(dict(self.request, files=self.request['files'] + ['dose.bin']))

    def test_tamper_and_duplicate_submit_rejected(self):
        result = bridge.prepare(self.request)
        request = dict(id=result['id'], manifestSHA256=result['manifestSHA256'])
        with self.assertRaises(ValueError): bridge.submit(dict(request, manifestSHA256='wrong'))
        with patch.object(bridge.subprocess, 'Popen') as launch:
            bridge.submit(request)
            with self.assertRaises(ValueError): bridge.submit(request)
            self.assertEqual(launch.call_count, 1)
        result = bridge.prepare(self.request)
        (bridge.job_path(result['id']) / 'inputs/ct.bin').write_bytes(b'tampered')
        with self.assertRaises(ValueError): bridge.submit(dict(id=result['id'], manifestSHA256=result['manifestSHA256']))

    def test_worker_success_failure_and_outputs(self):
        result = bridge.prepare(self.request)
        def run(*args, **kwargs):
            (kwargs['cwd'] / 'dose.bin').write_bytes(b'scored')
            return 0
        with patch.object(bridge.subprocess, 'call', side_effect=run): bridge.worker(result['id'])
        done = bridge.status(result['id'])
        self.assertEqual(done['state'], 'completed')
        self.assertEqual(list(done['outputs']), ['dose.bin'])
        failed = bridge.prepare(self.request)
        with patch.object(bridge.subprocess, 'call', return_value=7): bridge.worker(failed['id'])
        self.assertEqual(bridge.status(failed['id'])['state'], 'failed')

    def test_stale_worker_detected(self):
        result = bridge.prepare(self.request)
        bridge.save(bridge.job_path(result['id']) / 'status.json', dict(state='running', updated=0))
        self.assertEqual(bridge.status(result['id'])['state'], 'interrupted')


if __name__ == '__main__': unittest.main()
