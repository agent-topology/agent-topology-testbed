"""Capture four predeclared recipes, twice, in separate isolated processes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        parser.error('output must be a fresh path; failed evidence is retained')
    out.mkdir(parents=True)
    cases = json.loads((HERE / 'cases.json').read_text())
    manifest = {'sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(HERE.iterdir()) if p.is_file()}, 'runs': []}
    # Save authored expectations and input bytes before any extraction.
    for name, case in cases.items():
        (out / f'{name}.input.json').write_text(json.dumps(case, indent=2) + '\n')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    failed = False
    for name in cases:
        for repeat in (1, 2):
            stem = f'{name}-{repeat}'
            command = [str(args.python.absolute()), '-I', str(HERE / 'worker.py'),
                       str(out / f'{name}.input.json')]
            result = subprocess.run(command, capture_output=True)
            (out / f'{stem}.stdout.json').write_bytes(result.stdout)
            (out / f'{stem}.stderr.txt').write_bytes(result.stderr)
            manifest['runs'].append({'id': stem, 'argv': command, 'exit_code': result.returncode})
            failed |= result.returncode != 0
            (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if failed:
        raise SystemExit('extraction failed; inspect retained stderr and exit codes')


if __name__ == '__main__':
    main()
