"""Audit saved E1 bytes and repeat results; --pair reports differences with exit 1."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from generate import require, valid
from run import classify, digest, encode


def audit(path):
    inputs = (path / 'evaluated-inputs.jsonl.gz').read_bytes()
    raw_inputs = gzip.decompress(inputs).splitlines(keepends=True)
    records = [list(map(json.loads, gzip.decompress((path / f'batch-{i}.jsonl.gz').read_bytes()).splitlines())) for i in range(2)]
    require(len(raw_inputs) == len(records[0]) == len(records[1]), 'batch count mismatch')
    by_hash = {}
    for raw, a, b in zip(raw_inputs, *records):
        sha = digest(raw)
        require(valid(json.loads(raw)), 'saved evaluated input invalid')
        require(a['input_sha256'] == b['input_sha256'] == sha, 'saved input digest mismatch')
        classify(a, b)  # rejects API failures independently of summary
        by_hash[sha] = [a, b]
    cases = json.loads((path / 'cases.json').read_text())
    require(len(cases) == 600, 'incomplete population')
    counts = Counter()
    population = gzip.decompress((path / 'inputs.jsonl.gz').read_bytes()).splitlines(keepends=True)
    require(len(population) == len(cases), 'saved population count mismatch')
    for case, raw in zip(cases, population):
        require(digest(raw) == case['input_sha256'], 'case input changed')
        signature = classify(*by_hash[case['input_sha256']])
        require(list(signature) == case['mismatch'], 'case classification changed')
        counts.update(signature)
    summary = json.loads((path / 'summary.json').read_text())
    require(dict(counts) == summary['mismatches'], 'summary mismatch')
    for failure in json.loads((path / 'failures.json').read_text()):
        sha = failure['minimized_sha256']
        raw = (path / 'minimized' / (sha + '.json')).read_bytes()
        require(digest(raw) == sha and valid(json.loads(raw)), 'minimized candidate changed/invalid')
        require(list(classify(*by_hash[sha])) == failure['signature'], 'shrink lost distinguishing mismatch')
        replay = json.loads((path / 'minimized' / (sha + '-replay.json')).read_text())
        require(all(c['exit'] in (0, 2) for c in replay), 'replay failure')
        results = [json.loads(c['stdout']) for c in replay]
        require(all(r['input_sha256'] == sha for r in results), 'replay input changed')
        require(list(classify(*results)) == failure['signature'], 'fresh replay lost mismatch')
    # Exact observations apart from installation location and executable; identities
    # are retained raw and versions/runtimes must still agree across installations.
    semantic = {}
    for sha, pair in by_hash.items():
        for r in pair:
            r['identity'] = {k: v for k, v in r['identity'].items() if k not in ('imported_path', 'executable')}
        semantic[sha] = pair
    return cases, semantic


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('runs', nargs='*', type=Path)
    p.add_argument('--pair', type=Path)
    args = p.parse_args()
    if args.pair:
        differences = classify(*json.loads(args.pair.read_text()))
        print(json.dumps({'differences': differences}))
        return int(bool(differences))
    require(len(args.runs) == 2, 'supply two saved runs')
    a, b = map(audit, args.runs)
    require(a == b, 'fixed-seed repeat differs')
    print('PASS: 300 base inputs, 600 comparisons, all shrink evaluations and fresh replays reproduce')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
