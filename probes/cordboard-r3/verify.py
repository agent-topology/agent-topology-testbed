"""Check captured records against predeclared recipes, never the model as oracle."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_record(record, case):
    require(record['core_validation_errors'] == [], 'core validation failed')
    direct = case['routing'] == 'direct'
    expected = case['expected_match']
    document = record['document']
    require(len(document['graphs']) == 1, 'graph count')
    graph = document['graphs'][0]
    require(graph['id'] == 'main' and graph['name'] == 'r3-minimal', 'graph identity')
    structure = graph['structure']
    nodes = {node['id']: node for node in structure['nodes']}
    require(len(structure['nodes']) == 5 and set(nodes) ==
            {'__start__', '__end__', 'router', 'a', 'b'}, 'node set')
    for name, node in nodes.items():
        require(node.get('interrupts', []) ==
                (['before'] if name in case['interrupt_before'] else []), 'static interrupts')
    edges = structure['edges']
    triples = {(e['source'], e['target'], e['kind']) for e in edges}
    kind = 'direct' if direct else 'conditional'
    require(len(edges) == 5 and triples == {
        ('__start__', 'router', 'direct'), ('router', 'a', kind),
        ('router', 'b', kind), ('a', '__end__', 'direct'),
        ('b', '__end__', 'direct')}, 'edge declarations')
    require(structure['joins'] == [] and structure['entryNodeIds'] == ['__start__']
            and structure['exitNodeIds'] == ['__end__'], 'structural boundaries')
    require(document['completeness'] == {'status': 'complete', 'gaps': []}, 'completeness')
    require(record['calls'] == {'node': 0, 'router_during_extraction': 0,
                                'router_direct': 0 if direct else 1}, 'execution boundary')
    require(record['callable'] == ({'evaluated': False} if direct else
            {'evaluated': True, 'input': {'value': 'unused'},
             'result': case['expected_callable_result']}), 'callable result')
    for mode, override in [('default', False), ('override', True)]:
        verdict = record['adr_model'][mode]
        require(verdict['rule'] == 'R3' and verdict['matched'] is expected, 'rule match')
        require(verdict['decision'] == ('reject' if expected and not override else 'not-rejected'),
                'rule decision')
        require(verdict['override_requested'] is override and
                verdict['override_applied'] is (override and expected), 'override')
        if expected:
            # IDs are locators, checked against the already-verified literal topology.
            outgoing = sorted((e for e in edges if e['source'] == 'router'), key=lambda e: e['id'])
            require(verdict['matches'] == [{
                'graphId': 'main', 'source': 'router',
                'directEdgeIds': [e['id'] for e in outgoing],
                'interruptedTargets': [{'edgeId': e['id'], 'nodeId': e['target'],
                                        'interrupts': ['before']} for e in outgoing]}], 'evidence locators')
        else:
            require(verdict['matches'] == [], 'unexpected evidence')


def normalized(record):
    result = copy.deepcopy(record)
    del result['document']['provenance']['generatedAt']
    return result


def verify(out):
    cases = json.loads((HERE / 'cases.json').read_text())
    manifest = json.loads((out / 'manifest.json').read_text())
    require([r['id'] for r in manifest['runs']] ==
            [f'{name}-{i}' for name in cases for i in (1, 2)], 'run inventory')
    require(all(r['exit_code'] == 0 for r in manifest['runs']), 'worker failure')
    for name, digest in manifest['sources'].items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, 'source drift')
    records = {}
    for name, case in cases.items():
        raw = (out / f'{name}.input.json').read_bytes()
        require(json.loads(raw) == case, 'input drift')
        for i in (1, 2):
            record = json.loads((out / f'{name}-{i}.stdout.json').read_text())
            require(record['input_sha256'] == hashlib.sha256(raw).hexdigest(), 'input digest')
            check_record(record, case)
            identity = record['identity']
            require(identity['versions'] == {'agent-topology-langgraph': '0.1.0b2',
                    'agent-topology-spec': '0.1.0b2', 'langgraph': '1.2.11'}, 'package identity')
            require(all(Path(p).is_relative_to(Path(identity['prefix']))
                        for p in identity['imports'].values()), 'nonisolated import')
            records[f'{name}-{i}'] = record
        require(normalized(records[f'{name}-1']) == normalized(records[f'{name}-2']), 'repeat drift')
    single, multiple = (records[f'{name}-1']['document']
                        for name in ('conditional-single', 'conditional-list'))
    require(single['graphs'] == multiple['graphs'], 'conditional graph difference')
    require(single['structureHash'] == multiple['structureHash'], 'conditional hash difference')
    return {'records_checked': 8, 'repeated_pairs_equal': 4,
            'repeat_exclusion': '/document/provenance/generatedAt',
            'conditional_graphs_equal': True, 'conditional_hashes_equal': True,
            'conditional_hash': single['structureHash'],
            'decisions': {name: records[f'{name}-1']['adr_model']['default']['decision'] for name in cases},
            'disposition': 'supports F1; no execution, safety or resume conclusion'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    result = verify(args.out)
    (args.out / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
