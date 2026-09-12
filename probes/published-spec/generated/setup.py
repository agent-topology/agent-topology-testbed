"""Install only generator and published beta.2 V1 environments from frozen locks."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--envs', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    if envs.exists() or out.exists(): raise ValueError('use fresh paths')
    envs.mkdir(parents=True); out.mkdir(parents=True)
    records = []
    def run(cmd, cwd=envs):
        start = time.monotonic()
        result = subprocess.run(list(map(str, cmd)), cwd=cwd, capture_output=True, text=True)
        records.append(dict(command=list(map(str, cmd)), cwd=str(cwd), started_at=datetime.now(timezone.utc).isoformat(), seconds=time.monotonic()-start, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
        (out / 'commands.json').write_text(json.dumps(records, indent=2)+'\n')
        if result.returncode: raise RuntimeError(result.stderr)
    for label in ('generator', 'py-b2', 'js-b2'):
        target = envs / label
        if label != 'js-b2':
            run([sys.executable, '-m', 'venv', target])
            lock = HERE / 'requirements.lock' if label == 'generator' else HERE.parent / 'locks/py-b2/requirements.lock'
            run([target / 'bin/python', '-I', '-m', 'pip', '--isolated', 'install', '--index-url', 'https://pypi.org/simple', '--only-binary=:all:', '--require-hashes', '-r', lock, '--report', out / f'{label}-install.json'])
            run([target / 'bin/python', '-I', '-m', 'pip', 'freeze', '--all'])
        else:
            target.mkdir()
            for name in ('package.json', 'package-lock.json'):
                shutil.copyfile(HERE.parent / 'locks/js-b2' / name, target / name)
            run(['npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund', '--registry=https://registry.npmjs.org'], target)
            run(['npm', 'ls', '--all', '--json'], target)
            shutil.copyfile(HERE.parent / 'adapter.mjs', target / 'adapter.mjs')
    artifacts = []
    for label in ('generator', 'py-b2'):
        for item in json.loads((out / f'{label}-install.json').read_text())['install']:
            info = item['download_info']
            raw = urllib.request.urlopen(info['url'], timeout=30).read()
            sha = hashlib.sha256(raw).hexdigest()
            if sha != info['archive_info']['hashes']['sha256']: raise ValueError('artifact mismatch')
            artifacts.append(dict(environment=label, package=item['metadata']['name'], version=item['metadata']['version'], url=info['url'], sha256=sha))
    for name, item in json.loads((envs / 'js-b2/package-lock.json').read_text())['packages'].items():
        if not name: continue
        raw = urllib.request.urlopen(item['resolved'], timeout=30).read()
        import base64
        algorithm, expected = item['integrity'].split('-', 1)
        if base64.b64encode(hashlib.new(algorithm, raw).digest()).decode() != expected: raise ValueError('npm artifact mismatch')
        artifacts.append(dict(environment='js-b2', package=name, version=item['version'], url=item['resolved'], integrity=item['integrity'], sha256=hashlib.sha256(raw).hexdigest()))
    (out / 'artifacts.json').write_text(json.dumps(artifacts, indent=2)+'\n')
    print('PASS: isolated locked generator and V1 beta.2 installations')


if __name__ == '__main__':
    main()
