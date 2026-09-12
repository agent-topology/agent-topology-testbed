"""Bounded rule controls and corruption checks for the saved observation."""
import copy
import json
from pathlib import Path
import unittest

from model import evaluate
from verify import check_record, normalized, verify

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / 'observations/cordboard-r3/run'
CASES = json.loads((HERE / 'cases.json').read_text())


class ProbeTests(unittest.TestCase):
    def record(self, name='direct-interrupt'):
        return json.loads((RUN / f'{name}-1.stdout.json').read_text())

    def test_four_authored_cases_and_overrides(self):
        for name, case in CASES.items():
            with self.subTest(name=name):
                record = self.record(name)
                check_record(record, case)
                for override in (False, True):
                    result = evaluate(record['document'], allow_parallel_interrupt=override)
                    self.assertIs(result['matched'], case['expected_match'])
                    self.assertEqual(result['decision'], 'reject' if case['expected_match']
                                     and not override else 'not-rejected')

    def test_no_mutation(self):
        document = self.record()['document']
        before = copy.deepcopy(document)
        evaluate(document)
        self.assertEqual(document, before)

    def test_override_requires_boolean(self):
        with self.assertRaises(ValueError):
            evaluate(self.record()['document'], allow_parallel_interrupt='false')

    def test_interrupt_on_descendant_does_not_match_action_four(self):
        document = self.record()['document']
        for node in document['graphs'][0]['structure']['nodes']:
            node.pop('interrupts', None)
            if node['id'] == '__end__':
                node['interrupts'] = ['before']
        self.assertFalse(evaluate(document)['matched'])

    def test_missing_static_interrupt_is_not_a_success(self):
        record = self.record()
        for node in record['document']['graphs'][0]['structure']['nodes']:
            node.pop('interrupts', None)
        with self.assertRaisesRegex(ValueError, 'static interrupts'):
            check_record(record, CASES['direct-interrupt'])

    def test_recorded_validation_failure_is_not_a_success(self):
        record = self.record()
        record['core_validation_errors'] = ['synthetic invalid document']
        with self.assertRaisesRegex(ValueError, 'core validation'):
            check_record(record, CASES['direct-interrupt'])

    def test_corrupt_evidence_is_not_a_success(self):
        record = self.record()
        record['adr_model']['default']['matches'][0]['source'] = 'a'
        with self.assertRaisesRegex(ValueError, 'evidence locators'):
            check_record(record, CASES['direct-interrupt'])

    def test_repeat_normalizes_only_timestamp(self):
        record = self.record()
        other = copy.deepcopy(record)
        other['document']['provenance']['generatedAt'] = 'other'
        self.assertEqual(normalized(record), normalized(other))
        other['document']['provenance']['producer']['version'] = 'other'
        self.assertNotEqual(normalized(record), normalized(other))

    def test_complete_capture(self):
        self.assertEqual(verify(RUN)['records_checked'], 8)


if __name__ == '__main__':
    unittest.main()
