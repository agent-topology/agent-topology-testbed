"""Small schema-valid documents; generator dependencies never enter spec envs."""
from copy import deepcopy
import json
from pathlib import Path

from hypothesis import given, seed, settings, Phase, strategies as st
from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
BASE = json.loads((HERE.parents[2] / 'observations/V1/inputs/minimal.json').read_text())
SCHEMA = Draft202012Validator(json.loads((HERE / 'schema.json').read_text()), format_checker=FormatChecker())
# Unicode scalar values only, with the known code-point/UTF-16 boundary included.
TEXT = st.text(alphabet=['a', 'z', 'é', 'e', '\u0301', '\ue000', '\U00010000', '😀', '"', '\\', '\n'], min_size=1, max_size=4)
NUMBER = st.one_of(st.integers(-100, 100), st.sampled_from([0.0, -0.0, 1.0, 0.5, 1e-7, 1e-6, 1e20]))
PAYLOAD = st.recursive(st.one_of(st.none(), st.booleans(), NUMBER, TEXT), lambda child: st.one_of(st.lists(child, max_size=3), st.dictionaries(st.one_of(TEXT, st.sampled_from(['0', '2', '10'])), child, max_size=3)), max_leaves=6)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid(document):
    """Independent schema + reference/ID/completeness oracle, never package filtering."""
    if not SCHEMA.is_valid(document):
        return False
    graphs = document['graphs']
    gids = [g['id'] for g in graphs]
    if len(set(gids)) != len(gids):
        return False
    lookup = {}
    for g in graphs:
        s = g['structure']
        groups = {k: [x['id'] for x in s[k + 's']] for k in ('node', 'edge', 'join')}
        if any(len(v) != len(set(v)) for v in groups.values()):
            return False
        nodes = set(groups['node'])
        if not set(s['entryNodeIds'] + s['exitNodeIds']) <= nodes:
            return False
        if any(e['source'] not in nodes or e['target'] not in nodes for e in s['edges']):
            return False
        if any(not set(j['sources'] + [j['target']]) <= nodes for j in s['joins']):
            return False
        if any(n.get('subgraphId', g['id']) not in gids for n in s['nodes']):
            return False
        lookup[g['id']] = dict(groups, graph=[g['id']])
    gaps = document['completeness']['gaps']
    if document['completeness']['status'] != ('incomplete' if gaps else 'complete'):
        return False
    return all(e['graphId'] in lookup and e['id'] in lookup[e['graphId']][e['kind']] for e in (g['element'] for g in gaps))


@st.composite
def documents(draw):
    d = deepcopy(BASE)
    d['structureHash']['value'] = '0' * 64  # schema-valid placeholder, not a computed oracle
    gids = draw(st.lists(TEXT, min_size=1, max_size=2, unique=True))
    d['graphs'] = []
    for gi, gid in enumerate(gids):
        ids = draw(st.lists(TEXT, max_size=3, unique=True))
        s = dict(nodes=[], edges=[], joins=[], entryNodeIds=[], exitNodeIds=[])
        for nid in ids:
            n = {'id': nid}
            if draw(st.booleans()): n['type'] = draw(TEXT)
            if draw(st.booleans()): n['interrupts'] = draw(st.lists(st.sampled_from(['before', 'after']), unique=True, max_size=2))
            if gi == 0 and len(gids) == 2 and draw(st.booleans()): n['subgraphId'] = gids[1]
            if draw(st.booleans()): n['x-e1'] = draw(PAYLOAD)
            s['nodes'].append(n)
        if ids:
            for ei in range(draw(st.integers(0, 2))):
                s['edges'].append(dict(id=f'e{ei}', source=draw(st.sampled_from(ids)), target=draw(st.sampled_from(ids)), kind=draw(st.sampled_from(['direct', 'conditional']))))
            for key in ('entryNodeIds', 'exitNodeIds'):
                s[key] = draw(st.lists(st.sampled_from(ids), unique=True, max_size=len(ids)))
        if len(ids) >= 2:
            for ji in range(draw(st.integers(0, 2))):
                s['joins'].append(dict(id=f'j{ji}', sources=draw(st.lists(st.sampled_from(ids), min_size=2, max_size=len(ids), unique=True)), target=draw(st.sampled_from(ids))))
        g = dict(id=gid, structure=s)
        if draw(st.booleans()): g['name'] = draw(TEXT)
        d['graphs'].append(g)
    if draw(st.booleans()): d['provenance']['source'] = {'kind': draw(TEXT)}
    if draw(st.booleans()): d['producerLimitations'] = [{'code': draw(TEXT), 'message': draw(TEXT)}]
    if draw(st.booleans()):
        d['completeness'] = dict(status='incomplete', gaps=[dict(code=draw(TEXT), message=draw(TEXT), element=dict(graphId=gids[0], kind='graph', id=gids[0]))])
    if draw(st.booleans()): d['x-e1'] = draw(PAYLOAD)
    require(valid(d), 'generator violated independent validity oracle')
    return d


def population(value):
    result = []
    @seed(value)
    @settings(max_examples=100, database=None, deadline=None, phases=[Phase.generate])
    @given(documents())
    def collect(document):
        result.append(document)
    collect()
    require(len(result) == 100, 'seed did not produce 100 base examples')
    return result


def permute(document):
    """Only contract-defined structural collections; extension lists keep their order."""
    d = deepcopy(document)
    d['graphs'].reverse()
    for g in d['graphs']:
        s = g['structure']
        for key in ('nodes', 'edges', 'joins', 'entryNodeIds', 'exitNodeIds'): s[key].reverse()
        for n in s['nodes']:
            if 'interrupts' in n: n['interrupts'].reverse()
        for j in s['joins']: j['sources'].reverse()
    return d
