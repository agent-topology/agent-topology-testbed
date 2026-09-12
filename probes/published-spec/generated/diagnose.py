"""Explain canonical differences without changing the differential oracle."""
import argparse
from collections import Counter
from decimal import Decimal
import gzip
import json
from pathlib import Path
import re

TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?')


def numeric_form(text):
    def replace(match):
        token = match.group()
        if token.startswith('"'): return token
        value = Decimal(token)
        return '0' if value == 0 else str(value.normalize())
    return TOKEN.sub(replace, text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    records = [dict((r['input_sha256'], r) for r in map(json.loads, gzip.decompress((args.run / f'batch-{i}.jsonl.gz').read_bytes()).splitlines())) for i in range(2)]
    counts = Counter()
    for case in json.loads((args.run / 'cases.json').read_text()):
        if 'canonical' not in case['mismatch']: continue
        a, b = [r[case['input_sha256']]['canonical'] for r in records]
        counts['canonical-differences'] += 1
        if numeric_form(a) == numeric_form(b): counts['numeric-spelling-only'] += 1
        else: counts['other-difference'] += 1
    print(json.dumps(dict(counts)))
    if counts['other-difference']: raise SystemExit(1)


if __name__ == '__main__': main()
