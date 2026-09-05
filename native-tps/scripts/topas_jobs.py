#!/usr/bin/env python3
"""Desktop TOPAS bridge. JSON stdin/stdout; fetch streams a tar.gz. No shell jobs."""
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid

ROOT = Path.home() / '.local/share/governed-tps/topas-jobs'
RUNNER = Path('/home/armorbearer/hupci-sim/opentopas/run-topas.sh')
ENGINE = Path('/home/armorbearer/hupci-sim/opentopas/topas-install/bin/topas')
LIMIT = 1024 * 1024 * 1024


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, obj):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(obj, sort_keys=True, indent=2))
    temp.replace(path)


def relative(name):
    p = Path(name)
    if not name or p.is_absolute() or '..' in p.parts or name.startswith('-'):
        raise ValueError('Only relative input/output paths without parent traversal are supported')
    return p


def job_path(identifier):
    return ROOT / str(uuid.UUID(identifier))


def inventory(directory):
    return {str(p.relative_to(directory)): digest(p) for p in sorted(directory.rglob('*')) if p.is_file()}


def prepare(request):
    source = Path(request['source']).resolve(strict=True)
    names = request['files']
    macros = request['macros']
    if not source.is_dir() or not names or not macros or len(names) > 1000:
        raise ValueError('Provide a source folder, input files, and at least one macro')
    if len(set(names)) != len(names) or len(set(macros)) != len(macros):
        raise ValueError('Duplicate input or macro names')
    for name in names:
        p = source / relative(name)
        if not p.is_file() or p.resolve() != source / relative(name):
            raise ValueError('Inputs must be regular files without symlinks: ' + name)
    if any(m not in names or not m.endswith('.txt') for m in macros):
        raise ValueError('Every macro must be an explicitly listed .txt input')
    if sum((source / n).stat().st_size for n in names) > LIMIT:
        raise ValueError('Input snapshot exceeds 1 GiB')
    texts = {n: (source / n).read_text() for n in names if n.endswith('.txt')}
    for name, content in texts.items():
        for line in content.splitlines():
            line = line.split('#', 1)[0].strip()
            if not line or '=' not in line:
                continue
            key, value = [v.strip() for v in line.split('=', 1)]
            for token in re.findall(r'"([^"]*)"', value):
                if token.startswith('/') or '..' in Path(token).parts:
                    raise ValueError('Absolute or parent-relative parameter paths are unsupported: ' + token)
            if key == 'includeFile':
                for ref in value.split():
                    if str(relative(ref.strip('"'))) not in names:
                        raise ValueError('Include is missing from input snapshot: ' + ref)
            if key.endswith('/InputFile'):
                if str(relative(value.strip('"'))) not in names:
                    raise ValueError('InputFile is missing from input snapshot: ' + value)
            if key.endswith('/InputDirectory') and value.strip('"') not in ('.', './'):
                raise ValueError('Use InputDirectory = "./" for this bridge')
            if key.endswith('/OutputFile'):
                output = str(relative(value.strip('"')))
                if any(n == output or n.startswith(output + '.') for n in names):
                    raise ValueError('Output collides with a reviewed input: ' + output)
    identifier = str(uuid.uuid4())
    job = job_path(identifier)
    (job / 'inputs').mkdir(parents=True, mode=0o700)
    for name in names:
        dest = job / 'inputs' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((source / name).read_bytes())
    # Persist the exact bridge so detached work survives app/SSH disconnects.
    script = base64.b64decode(request['worker'])
    (job / 'worker.py').write_bytes(script)
    manifest = dict(schemaVersion=1, id=identifier, created=time.time(), source=str(source),
                    macros=macros, inputs=inventory(job / 'inputs'),
                    runner=str(RUNNER), runnerSHA256=digest(RUNNER),
                    engine=str(ENGINE), engineSHA256=digest(ENGINE),
                    workerSHA256=digest(job / 'worker.py'), clinicalReleaseAllowed=False,
                    limitations=['Runtime libraries and Geant4 datasets are not snapshotted.',
                                 'Transport outputs are raw; calibration and grid validation are separate.'])
    save(job / 'manifest.json', manifest)
    save(job / 'status.json', dict(state='prepared', updated=time.time()))
    return status(identifier)


def status(identifier):
    job = job_path(identifier)
    result = json.loads((job / 'manifest.json').read_text())
    result['manifestSHA256'] = digest(job / 'manifest.json')
    result.update(json.loads((job / 'status.json').read_text()))
    # A held worker lock distinguishes live jobs from stale state after a reboot/crash.
    if result['state'] in ('running', 'queued') and time.time() - result['updated'] > 15:
        with (job / 'worker.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                result['state'] = 'interrupted'
            except BlockingIOError:
                pass
    log = job / 'transport.log'
    if log.exists():
        with log.open('rb') as f:
            f.seek(max(0, log.stat().st_size - 24000))
            result['log'] = f.read().decode(errors='replace')
    result['parameters'] = {n: (job / 'inputs' / n).read_text() for n in result['inputs'] if n.endswith('.txt')}
    if (job / 'outputs.json').exists():
        result['outputs'] = json.loads((job / 'outputs.json').read_text())
    return result


def submit(request):
    job = job_path(request['id'])
    with (job / 'submit.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if json.loads((job / 'status.json').read_text())['state'] != 'prepared':
            raise ValueError('This job has already been submitted; prepare a new job to rerun')
        if digest(job / 'manifest.json') != request['manifestSHA256']:
            raise ValueError('The reviewed manifest changed')
        manifest = json.loads((job / 'manifest.json').read_text())
        if inventory(job / 'inputs') != manifest['inputs']:
            raise ValueError('Reviewed input files changed')
        for path, key in [(RUNNER, 'runnerSHA256'), (ENGINE, 'engineSHA256'), (job / 'worker.py', 'workerSHA256')]:
            if digest(path) != manifest[key]:
                raise ValueError('Runner, engine, or worker changed since preparation')
        save(job / 'status.json', dict(state='queued', updated=time.time()))
        with (job / 'transport.log').open('ab') as log:
            try:
                subprocess.Popen([sys.executable, str(job / 'worker.py'), '--worker', request['id']],
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                 start_new_session=True, close_fds=True)
            except Exception:
                save(job / 'status.json', dict(state='failed', updated=time.time()))
                raise
    return status(request['id'])


def worker(identifier):
    import shutil
    job = job_path(identifier)
    with (job / 'worker.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            manifest = json.loads((job / 'manifest.json').read_text())
            if inventory(job / 'inputs') != manifest['inputs']:
                raise ValueError('Inputs changed before worker started')
            if digest(RUNNER) != manifest['runnerSHA256'] or digest(ENGINE) != manifest['engineSHA256']:
                raise ValueError('Engine or runner changed before worker started')
            shutil.copytree(job / 'inputs', job / 'work')
            for macro in manifest['macros']:
                save(job / 'status.json', dict(state='running', macro=macro, updated=time.time()))
                code = subprocess.call([str(RUNNER), macro], cwd=job / 'work', stdin=subprocess.DEVNULL)
                if code:
                    raise RuntimeError(f'{macro} exited with code {code}')
            outputs = {n: h for n, h in inventory(job / 'work').items() if n not in manifest['inputs']}
            save(job / 'outputs.json', outputs)
            save(job / 'status.json', dict(state='completed', updated=time.time()))
        except Exception as error:
            save(job / 'status.json', dict(state='failed', error=str(error), updated=time.time()))


def fetch(identifier):
    job = job_path(identifier)
    if status(identifier)['state'] not in ('completed', 'failed', 'interrupted'):
        raise ValueError('Wait for a terminal job state before retrieving results')
    # Regular files only; never follow output symlinks out of the job.
    files = [p for p in job.rglob('*') if p.is_file() and not p.is_symlink()]
    if sum(p.stat().st_size for p in files) > 512 * 1024 * 1024:
        raise ValueError('Result exceeds 512 MiB; transfer the job folder separately')
    with tarfile.open(fileobj=sys.stdout.buffer, mode='w|gz') as archive:
        for p in files:
            archive.add(p, arcname=str(p.relative_to(job)), recursive=False)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        worker(sys.argv[2]); return
    request = json.loads(sys.stdin.buffer.read(2 * 1024 * 1024))
    action = request['action']
    if action == 'probe':
        result = dict(runner=str(RUNNER), runnerAvailable=os.access(RUNNER, os.X_OK),
                      engineAvailable=os.access(ENGINE, os.X_OK), jobRoot=str(ROOT),
                      engineSHA256=digest(ENGINE), engineVersion='See transport log; no version inferred')
    elif action == 'prepare': result = prepare(request)
    elif action == 'submit': result = submit(request)
    elif action == 'status': result = status(request['id'])
    elif action == 'fetch': fetch(request['id']); return
    else: raise ValueError('Unknown action')
    print(json.dumps(result))


if __name__ == '__main__':
    try: main()
    except Exception as error:
        print(json.dumps(dict(error=str(error))), file=sys.stderr)
        sys.exit(1)
