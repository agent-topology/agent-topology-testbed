"""Failure-path and determinism checks for S1; standard library only, no
separate environment or install needed."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("asl_probe.py").resolve()
FIXTURES_DIR = Path(__file__).with_name("fixtures")

POSITIVE_FIXTURES = ("choice", "parallel", "map")
NEGATIVE_FIXTURES = {
    "invalid_missing_target": "ASLReferenceError",
    "invalid_cross_boundary": "ASLReferenceError",
}

# A worker that loads asl_probe.py's live namespace via runpy and corrupts one
# EXPECTED_FACTS entry before calling main(), so require_equal's comparison is
# checked against a genuine mismatch rather than a vacuously passing probe.
WORKER = """
import runpy
import sys
namespace = runpy.run_path(sys.argv[1])['main'].__globals__
mutation, output = sys.argv[2:]
fixture = 'choice'
if mutation == 'choice_order':
    namespace['EXPECTED_FACTS']['choice'][0]['choice_rules']['CheckStatus']['ordered_targets'] = ['Rejected', 'Approved']
elif mutation == 'branch_identity':
    fixture = 'parallel'
    namespace['EXPECTED_FACTS']['parallel'][1]['scope_id'] = 'root/RunBoth/branch1'
elif mutation == 'max_concurrency':
    fixture = 'map'
    namespace['EXPECTED_FACTS']['map'][0]['map_config']['ProcessItems']['max_concurrency'] = 5
elif mutation == 'unknown_state_type':
    original_load_fixture = namespace['load_fixture']
    def patched(path):
        doc = original_load_fixture(path)
        doc['States']['CheckStatus']['Type'] = 'Bogus'
        return doc
    namespace['load_fixture'] = patched
sys.argv = ['asl_probe.py', '--fixture', fixture, '--output', output]
namespace['main']()
"""

EXPECTED_FAILURE_TEXT = {
    "choice_order": "AssertionError: observation mismatch",
    "branch_identity": "AssertionError: observation mismatch",
    "max_concurrency": "AssertionError: observation mismatch",
    "unknown_state_type": "ASLStructureError",
}


class ASLProbeChecks(unittest.TestCase):
    def run_probe(self, fixture, directory):
        output = Path(directory) / f"{fixture}.json"
        result = subprocess.run(
            [sys.executable, "-O", str(SOURCE), "--fixture", fixture, "--output", str(output)],
            capture_output=True, text=True, timeout=30,
        )
        return result, output

    def test_positive_fixtures_succeed_and_are_deterministic(self):
        for fixture in POSITIVE_FIXTURES:
            with self.subTest(fixture=fixture):
                with tempfile.TemporaryDirectory(prefix="s1-check-") as directory:
                    result1, output1 = self.run_probe(fixture, directory)
                    self.assertEqual(result1.returncode, 0, result1.stderr)
                    result2, output2 = self.run_probe(fixture, directory)
                    self.assertEqual(result2.returncode, 0, result2.stderr)
                    self.assertEqual(output1.read_text(), output2.read_text())

    def test_negative_fixtures_fail_under_optimization(self):
        for fixture, expected_exception in NEGATIVE_FIXTURES.items():
            with self.subTest(fixture=fixture):
                with tempfile.TemporaryDirectory(prefix="s1-check-") as directory:
                    result, output = self.run_probe(fixture, directory)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(expected_exception, result.stderr)
                    self.assertFalse(output.exists())

    def test_corrupted_expected_facts_fail(self):
        for mutation in ("choice_order", "branch_identity", "max_concurrency", "unknown_state_type"):
            with self.subTest(mutation=mutation):
                with tempfile.TemporaryDirectory(prefix="s1-check-") as directory:
                    output = Path(directory) / "observation.json"
                    result = subprocess.run(
                        [sys.executable, "-O", "-c", WORKER, str(SOURCE), mutation, str(output)],
                        capture_output=True, text=True, timeout=30,
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(EXPECTED_FAILURE_TEXT[mutation], result.stderr)
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
