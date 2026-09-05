from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = (root / 'scripts/topas_jobs.py').read_text()
(root / 'Sources/GovernedTPS/TopasBridgeSource.swift').write_text(
    '// Generated from scripts/topas_jobs.py; do not edit by hand.\n'
    'extension TopasBridge {\n    static let source = ####"""\n' + source + '\n"""####\n}\n')
