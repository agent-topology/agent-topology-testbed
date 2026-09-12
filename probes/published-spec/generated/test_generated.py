"""Deterministic failure controls; synthetic results are not package evidence."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from generate import BASE, permute, valid
from run import classify, encode, shrink


class Controls(unittest.TestCase):
    def pair(self):
        result = dict(status='accepted', validation={'accepted': True}, canonical='{}', structureHash=dict(algorithm='sha256', algorithmVersion='1', value='0'*64), properties=dict(non_mutation=True, idempotence=True, hash_idempotence=True))
        return [result, deepcopy(result)]

    def test_altered_adapter_result_fails_cli_under_optimization(self):
        pair = self.pair()
        pair[1]['structureHash']['value'] = 'f'*64
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'pair.json'; path.write_bytes(encode(pair))
            p = subprocess.run([sys.executable, '-O', str(Path(__file__).with_name('verify.py')), '--pair', str(path)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 1, p.stderr)
            self.assertEqual(json.loads(p.stdout)['differences'], ['structure-hash'])

    def test_canonical_float_difference_is_separate(self):
        pair = self.pair(); pair[0]['canonical'] = '{"x":0.0}'; pair[1]['canonical'] = '{"x":0}'
        self.assertEqual(classify(*pair), ('canonical',))

    def test_one_sided_rejection_retained(self):
        pair = self.pair(); pair[1] = dict(status='rejected', validation={'accepted': False, 'errors': ['synthetic']})
        self.assertEqual(classify(*pair), ('acceptance',))

    def test_both_rejected_is_not_a_pass(self):
        r = dict(status='rejected', validation={'accepted': False})
        self.assertEqual(classify(r, r), ('both-rejected',))

    def test_api_failure_and_incomplete_tuple_are_errors(self):
        for mutation in [lambda r: r.update(status='error'), lambda r: r['structureHash'].pop('algorithmVersion')]:
            pair = self.pair(); mutation(pair[1])
            with self.assertRaises(ValueError): classify(*pair)

    def test_algorithm_transition_not_same_algorithm_hash_drift(self):
        pair = self.pair(); pair[1]['structureHash']['algorithmVersion'] = '2'
        self.assertEqual(classify(*pair), ('algorithm-transition',))

    def test_property_failure_detected(self):
        for name in ['non_mutation', 'idempotence', 'hash_idempotence']:
            pair = self.pair(); pair[0]['properties'][name] = False
            self.assertIn('py:' + name, classify(*pair))

    def test_invalid_input_outside_population(self):
        self.assertTrue(valid(BASE))
        for mutate in [lambda d: d['graphs'][0]['structure'].pop('joins'), lambda d: d['graphs'][0]['structure']['entryNodeIds'].append('missing'), lambda d: d['graphs'].append(deepcopy(d['graphs'][0])), lambda d: d['graphs'][0].update(name=0.5)]:
            d = deepcopy(BASE); mutate(d); self.assertFalse(valid(d))

    def test_permutation_leaves_extension_order_untouched(self):
        d = deepcopy(BASE); d['x-e1'] = ['second', 'first']
        original = deepcopy(d)
        self.assertEqual(permute(d)['x-e1'], d['x-e1'])
        self.assertEqual(d, original)

    def test_shrink_preserves_validity_and_signature(self):
        pair = self.pair()
        class Fake:
            def evaluate(self, d):
                if not valid(d): raise RuntimeError('invalid input reached adapters')
                result = deepcopy(pair)
                if isinstance(d.get('x-e1'), float): result[1]['canonical'] = 'different'
                return result
        d = deepcopy(BASE); d['x-e1'] = 1.0; d['graphs'][0]['name'] = 'removable'
        small, attempts, stop = shrink(d, ('canonical',), Fake())
        self.assertTrue(valid(small)); self.assertNotIn('name', small['graphs'][0])
        self.assertEqual(classify(*Fake().evaluate(small)), ('canonical',))
        self.assertEqual(stop, 'local-fixed-point'); self.assertGreater(attempts, 0)


if __name__ == '__main__': unittest.main()
