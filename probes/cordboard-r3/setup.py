"""Install the unchanged D1 Python lock into a fresh, isolated environment."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    env, out = args.env.resolve(), args.out.resolve()
    if env.exists() or out.exists():
        parser.error('environment and output must both be fresh paths')
    out.mkdir(parents=True)
    lock = ROOT / 'probes/published-producer/locks/requirements.txt'
    commands = [
        [sys.executable, '-m', 'venv', str(env)],
        [str(env / 'bin/python'), '-I', '-m', 'pip', '--isolated', 'install',
         '--index-url', 'https://pypi.org/simple', '--require-hashes',
         '--only-binary=:all:', '-r', str(lock), '--report', str(out / 'install.json')],
    ]
    receipt = {'lock': str(lock.relative_to(ROOT)),
               'lock_sha256': hashlib.sha256(lock.read_bytes()).hexdigest(), 'commands': []}
    for i, command in enumerate(commands):
        result = subprocess.run(command, capture_output=True)
        (out / f'{i}.stdout.txt').write_bytes(result.stdout)
        (out / f'{i}.stderr.txt').write_bytes(result.stderr)
        receipt['commands'].append({'argv': command, 'exit_code': result.returncode})
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
