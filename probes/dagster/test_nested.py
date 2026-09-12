"""Failure-path checks for P4; run with the isolated Dagster Python."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("nested.py").resolve()
WORKER = """
import runpy
import sys
namespace = runpy.run_path(sys.argv[1])['main'].__globals__
mutation, output = sys.argv[2:]
mode = 'static'
original = namespace['extract_static']
def damaged(parent):
    facts = original(parent)
    if mutation == 'identity':
        facts['invocations'] = [row for row in facts['invocations'] if row[0] != 'right.seed']
    elif mutation == 'edge':
        facts['dependencies']['right'] = []
    elif mutation == 'mapping':
        facts['input_mappings']['right'][0][1] = 'left.seed'
    return facts
namespace['extract_static'] = damaged
if mutation == 'input':
    namespace['INPUT_VALUES']['right_seed'] = 1
    mode = 'execution'
elif mutation == 'version':
    namespace['importlib'].metadata.version = lambda name: 'unsupported'
elif mutation == 'static_only':
    from dagster import GraphDefinition
    def forbidden(*args, **kwargs):
        raise RuntimeError('Static mode attempted execution')
    GraphDefinition.to_job = forbidden
    GraphDefinition.execute_in_process = forbidden
sys.argv = ['nested.py', '--mode', mode, '--output', output]
namespace['main']()
"""


class NestedEvidenceChecks(unittest.TestCase):
    def run_worker(self, mutation, succeeds=False):
        with tempfile.TemporaryDirectory(prefix="p4-check-") as directory:
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
                self.assertIn("AssertionError: Observation mismatch", result.stderr)
                self.assertFalse(output.exists())

    def test_loss_or_corruption_fails_under_optimization(self):
        for mutation in ("identity", "edge", "mapping", "input", "version"):
            with self.subTest(mutation=mutation):
                self.run_worker(mutation)

    def test_static_mode_does_not_execute(self):
        self.run_worker("static_only", succeeds=True)


if __name__ == "__main__":
    unittest.main()
