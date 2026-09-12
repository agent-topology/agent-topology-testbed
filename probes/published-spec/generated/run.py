"""Bounded E1 generation, persistent V1-environment calls, shrinking and fresh replay."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from generate import HERE, population, permute, require, valid

SEEDS = [39, 20260912, 103]
LIMIT = 300  # locally valid shrink evaluations per failing base/variant


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_bytes(encode(value))


def classify(a, b):
    require(a['status'] in ('accepted', 'rejected') and b['status'] in ('accepted', 'rejected'), 'adapter API/setup error')
    result = []
    for r in (a, b):
        require(r['validation']['accepted'] == (r['status'] == 'accepted'), 'inconsistent validation/status')
    if a['validation']['accepted'] != b['validation']['accepted']: result.append('acceptance')
    if a['status'] == b['status'] == 'rejected': result.append('both-rejected')
    if a['status'] == b['status'] == 'accepted':
        if a['canonical'].encode() != b['canonical'].encode(): result.append('canonical')
        ha, hb = a['structureHash'], b['structureHash']
        for h in (ha, hb): require(set(h) == {'algorithm', 'algorithmVersion', 'value'}, 'incomplete hash tuple')
        if (ha['algorithm'], ha['algorithmVersion']) != (hb['algorithm'], hb['algorithmVersion']): result.append('algorithm-transition')
        elif ha != hb: result.append('structure-hash')
    for label, r in [('py', a), ('js', b)]:
        for key, passed in r.get('properties', {}).items():
            if not passed: result.append(label + ':' + key)
    return tuple(result)


class Runners:
    def __init__(self, envs, out):
        self.out, self.envs = out, envs
        self.clean = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME', 'NODE_PATH', 'NODE_OPTIONS'}}
        shutil.copyfile(HERE / 'batch.mjs', envs / 'js-b2/batch.mjs')
        self.commands = [[str(envs / 'py-b2/bin/python'), '-I', str(HERE / 'batch.py')], ['node', str(envs / 'js-b2/batch.mjs')]]
        self.started = time.monotonic()
        self.processes = [subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.clean) for cmd in self.commands]
        self.logs = [[], []]
        self.cache = {}

    def evaluate(self, d):
        raw = encode(d)
        if raw in self.cache: return self.cache[raw]
        require(valid(d), 'invalid input cannot enter language comparison')
        records = []
        for i, p in enumerate(self.processes):
            p.stdin.write(raw); p.stdin.flush()
            line = p.stdout.readline()
            require(bool(line), 'batch runner ended unexpectedly')
            self.logs[i].append(line)
            r = json.loads(line)
            require(r['input_sha256'] == digest(raw), 'adapters did not receive identical bytes')
            label, version = [('py-b2', '0.1.0b2'), ('js-b2', '0.1.0-beta.2')][i]
            require(r['identity']['version'] == version, 'wrong published package')
            require(str(self.envs / label) + '/' in r['identity']['imported_path'], 'import escaped isolation')
            require(r['status'] != 'error', str(r.get('error')))
            records.append(r)
        self.cache[raw] = records
        return records

    def close(self):
        commands = []
        (self.out / 'evaluated-inputs.jsonl.gz').write_bytes(gzip.compress(b''.join(self.cache), mtime=0))
        for i, p in enumerate(self.processes):
            p.stdin.close()
            stderr = p.stderr.read().decode()
            code = p.wait(timeout=30)
            (self.out / f'batch-{i}.jsonl.gz').write_bytes(gzip.compress(b''.join(self.logs[i]), mtime=0))
            commands.append(dict(command=self.commands[i], exit=code, stderr=stderr, records=len(self.logs[i])))
        save(self.out / 'batch-commands.json', dict(commands=commands, seconds=time.monotonic()-self.started))
        require(all(c['exit'] == 0 for c in commands), 'batch process failure')


def reductions(value):
    """Deterministic tree deletion/simplification; validity checked before adapters."""
    if isinstance(value, dict):
        for item in value.values(): yield item
        for key in value:
            yield {k: v for k, v in value.items() if k != key}
        for key, item in value.items():
            for smaller in reductions(item): yield dict(value, **{key: smaller})
    elif isinstance(value, list):
        for item in value: yield item
        for i in range(len(value)): yield value[:i] + value[i+1:]
        for i, item in enumerate(value):
            for smaller in reductions(item): yield value[:i] + [smaller] + value[i+1:]
    elif isinstance(value, str):
        for s in ['', 'a']:
            if len(s) < len(value): yield s
    elif isinstance(value, (float, int)) and not isinstance(value, bool):
        for n in [0, 0.0]:
            if (len(encode(n)), encode(n)) < (len(encode(value)), encode(value)): yield n


def shrink(document, signature, runners):
    current = document
    attempts = 0
    while attempts < LIMIT:
        changed = False
        for candidate in reductions(current):
            if not valid(candidate): continue
            attempts += 1
            if classify(*runners.evaluate(candidate)) == signature:
                current = candidate
                changed = True
                break
            if attempts >= LIMIT: break
        if not changed: return current, attempts, 'local-fixed-point'
    return current, attempts, 'limit-reached'


def fresh_replay(envs, document, out):
    raw = encode(document)
    records, commands = [], []
    for cmd in ([str(envs / 'py-b2/bin/python'), '-I', str(HERE.parent / 'adapter.py')], ['node', str(envs / 'js-b2/adapter.mjs')]):
        t = time.monotonic()
        p = subprocess.run(cmd, input=raw, capture_output=True, timeout=30,
                           env={k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME', 'NODE_PATH', 'NODE_OPTIONS'}})
        commands.append(dict(command=cmd, exit=p.returncode, seconds=time.monotonic()-t, stdout=p.stdout.decode(), stderr=p.stderr.decode()))
        require(p.returncode in (0, 2), 'fresh V1 runner failed')
        r = json.loads(p.stdout)
        require(r['input_sha256'] == digest(raw), 'fresh input mismatch')
        require(p.returncode == (0 if r['status'] == 'accepted' else 2), 'fresh status/exit mismatch')
        records.append(r)
    save(out, commands)
    return classify(*records)


def leaves(value):
    if isinstance(value, dict):
        for item in value.values(): yield from leaves(item)
    elif isinstance(value, list):
        for item in value: yield from leaves(item)
    else: yield value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--envs', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out, envs = args.out.resolve(), args.envs.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'minimized').mkdir()
    started = time.monotonic()
    runners = Runners(envs, out)
    cases, failures, minima, counts = [], [], {}, Counter()
    population_bytes = []
    coverage = Counter()
    try:
        for value in SEEDS:
            for index, document in enumerate(population(value)):
                base_records = None
                for variant, d in [('base', document), ('permuted', permute(document))]:
                    case = f'{value}-{index:03d}-{variant}'
                    raw = encode(d)
                    population_bytes.append(raw)
                    records = runners.evaluate(d)
                    signature = classify(*records)
                    if variant == 'base': base_records = records
                    else:
                        for language, (a, b) in enumerate(zip(base_records, records)):
                            if a['status'] == b['status'] == 'accepted':
                                require(a['canonical'] == b['canonical'] and a['structureHash'] == b['structureHash'], f'ordering violation: {case}/{language}')
                    cases.append(dict(case=case, seed=value, index=index, variant=variant, input_sha256=digest(raw), mismatch=signature))
                    counts.update(signature)
                    if signature:
                        # Every failing input is reduced; content-addressed output deduplicates equal minima.
                        small, attempts, stop = shrink(d, signature, runners)
                        sha = digest(encode(small))
                        (out / 'minimized' / (sha + '.json')).write_bytes(encode(small))
                        minima[sha] = (small, signature)
                        failures.append(dict(case=case, signature=signature, minimized_sha256=sha, attempts=attempts, stop=stop))
                text = encode(document).decode()
                for name, present in {
                    'bmp': any(0x80 <= ord(c) <= 0xffff for c in text),
                    'supplementary': any(ord(c) > 0xffff for c in text),
                    'combining': '\u0301' in text, 'quote': '\\"' in text, 'backslash': '\\\\' in text,
                    'extension': 'x-e1' in text,
                    'float': any(isinstance(x, float) for x in leaves(document)),
                    'integer': any(type(x) is int for x in leaves(document)),
                    'optional-present': any('name' in g for g in document['graphs']),
                    'optional-absent': any('name' not in g for g in document['graphs']),
                    'nontrivial-permutation': encode(permute(document)) != encode(document),
                }.items(): coverage[name] += int(present)
        for sha, (small, signature) in minima.items():
            require(fresh_replay(envs, small, out / 'minimized' / (sha + '-replay.json')) == signature, 'fresh V1 replay lost mismatch')
    finally:
        runners.close()
        (out / 'inputs.jsonl.gz').write_bytes(gzip.compress(b''.join(population_bytes), mtime=0))
        save(out / 'cases.json', cases)
        save(out / 'failures.json', failures)
    require(all(coverage.values()) and len(coverage) == 11, 'required dimension not exercised')
    save(out / 'summary.json', dict(seeds=SEEDS, base_examples=300, comparisons=len(cases), mismatches=dict(counts), minimized_candidates=len(minima), coverage=dict(coverage), shrink_limit=LIMIT, shrink_stop_counts=dict(Counter(f['stop'] for f in failures)), duration_seconds=time.monotonic()-started, finished_at=datetime.now(timezone.utc).isoformat(), generator_versions={n: importlib.metadata.version(n) for n in ['hypothesis', 'jsonschema']}, source_sha256={p.name: digest(p.read_bytes()) for p in sorted(HERE.iterdir()) if p.is_file()}, disposition='differences retained' if failures else 'bounded non-finding'))
    print((out / 'summary.json').read_text())


if __name__ == '__main__':
    main()
