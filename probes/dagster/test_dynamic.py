"""Failure-path checks for P6; run with the isolated Dagster Python."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("dynamic.py").resolve()
WORKER = """
import runpy
import sys
namespace = runpy.run_path(sys.argv[1])['main'].__globals__
mutation, output = sys.argv[2:]
case = '2'
mode = 'static'
original = namespace['extract_static']
def damaged(built):
    facts = original(built)
    if mutation == 'dependency_kind':
        facts['dependencies'][1][4] = 'direct'
    elif mutation == 'is_dynamic':
        facts['output_is_dynamic']['dynamic_source']['result'] = False
    return facts
namespace['extract_static'] = damaged
if mutation == 'mapping_keys':
    namespace['CASE_KEYS']['2'] = ['k0', 'k0']
    mode = 'execution'
elif mutation == 'cardinality':
    namespace['CASE_KEYS']['2'] = ['k0']
    mode = 'execution'
elif mutation == 'version':
    namespace['importlib'].metadata.version = lambda name: 'unsupported'
elif mutation == 'static_only':
    from dagster import JobDefinition
    def forbidden(*args, **kwargs):
        raise RuntimeError('Static mode attempted execution')
    JobDefinition.execute_in_process = forbidden
sys.argv = ['dynamic.py', '--case', case, '--mode', mode, '--output', output]
namespace['main']()
"""


# Each mutation's expected failure signature. `mapping_keys` fails inside the
# framework itself (a duplicate mapping key is a framework-enforced
# invariant, raised before our own assertions ever run), not via
# `require_equal`; every other mutation reaches our own assertion.
EXPECTED_FAILURE_TEXT = {
    "dependency_kind": "AssertionError: observation mismatch",
    "is_dynamic": "AssertionError: observation mismatch",
    "mapping_keys": "DagsterInvariantViolationError",
    "cardinality": "AssertionError: observation mismatch",
    "version": "AssertionError: observation mismatch",
}


class DynamicEvidenceChecks(unittest.TestCase):
    def run_worker(self, mutation, succeeds=False):
        with tempfile.TemporaryDirectory(prefix="p6-check-") as directory:
            output = Path(directory) / "observation.json"
            result = subprocess.run(
                [sys.executable, "-O", "-c", WORKER, str(SOURCE), mutation, str(output)],
                capture_output=True, text=True, timeout=60,
            )
            if succeeds:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(output.is_file())
            else:
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(EXPECTED_FAILURE_TEXT[mutation], result.stderr)
                self.assertFalse(output.exists())

    def test_loss_or_corruption_fails_under_optimization(self):
        for mutation in ("dependency_kind", "is_dynamic", "mapping_keys", "cardinality", "version"):
            with self.subTest(mutation=mutation):
                self.run_worker(mutation)

    def test_static_mode_does_not_execute(self):
        self.run_worker("static_only", succeeds=True)


if __name__ == "__main__":
    unittest.main()
