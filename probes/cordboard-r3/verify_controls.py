"""Retain focused tests, hash recomputation, and nonzero failure controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    python = str(args.python.absolute())
    worker = str(HERE / 'worker.py')
    jobs = [
        ('unit-tests', [sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE),
                        '-p', 'test_*.py', '-v'], 0, 'Ran 9 tests'),
        ('hashes', [python, '-I', '-c',
            'import json,sys; from pathlib import Path; from agent_topology.spec import compute_structure_hash; '
            'files=sorted(Path(sys.argv[1]).glob("*.stdout.json")); assert len(files)==8; '
            'docs=[json.loads(p.read_text())["document"] for p in files]; '
            'assert all(compute_structure_hash(d)==d["structureHash"] for d in docs); '
            'print("8 hashes recomputed and equal")',
            str(ROOT / 'observations/cordboard-r3/run')], 0, '8 hashes'),
        ('invalid-recipe', [python, '-I', '-c',
            'import runpy,sys; w=runpy.run_path(sys.argv[1]); '
            'w["extract"]({"routing":"invalid","interrupt_before":[]})', worker],
            1, 'unknown routing recipe'),
        ('invalid-producer-document', [python, '-I', '-c',
            'import runpy,sys; w=runpy.run_path(sys.argv[1]); '
            'w["producer"].describe=lambda *a,**k: {}; '
            'w["extract"]({"routing":"direct","interrupt_before":[]})', worker],
            1, 'invalid producer document'),
    ]
    receipt = {'sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(HERE.iterdir()) if p.is_file()}, 'checks': []}
    for name, command, expected_code, marker in jobs:
        result = subprocess.run(command, capture_output=True, cwd=ROOT)
        (out / f'{name}.stdout.txt').write_bytes(result.stdout)
        (out / f'{name}.stderr.txt').write_bytes(result.stderr)
        passed = (result.returncode == expected_code and
                  marker in (result.stdout + result.stderr).decode())
        receipt['checks'].append({'name': name, 'argv': command, 'exit_code': result.returncode,
                                  'expected_exit_code': expected_code, 'marker': marker, 'passed': passed})
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        if not passed:
            raise SystemExit(f'{name} failed; see retained output')
    print('9 tests, 8 hash recomputations and 2 failure controls passed')


if __name__ == '__main__':
    main()
