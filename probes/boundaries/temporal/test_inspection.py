"""Evidence-integrity checks, all subprocess checks use the pinned interpreter."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import fixtures
from inspect_definitions import extract

ROOT = Path(__file__).resolve().parent


class InspectionTests(unittest.TestCase):
    def test_duplicate_definitions_are_not_erased(self):
        result = extract([fixtures.LinearWorkflow] * 2, [fixtures.activity_a] * 2)
        self.assertEqual(len(result["workflows"]), 2)
        self.assertEqual(len(result["activities"]), 2)

    def test_fixture_bodies_are_never_entered(self):
        forbidden = {fixtures.LinearWorkflow.run.__code__, fixtures.ChoiceWorkflow.run.__code__,
                     fixtures.activity_a.__code__, fixtures.activity_b.__code__}

        def profile(frame, event, arg):
            if event == "call" and frame.f_code in forbidden:
                raise AssertionError("Inspection entered a fixture body")

        previous = sys.getprofile()
        sys.setprofile(profile)
        try:
            extract([fixtures.LinearWorkflow, fixtures.ChoiceWorkflow],
                    [fixtures.activity_a, fixtures.activity_b])
        finally:
            sys.setprofile(previous)
        self.assertEqual(fixtures.BODIES_ENTERED, [])

    def test_corrupt_expectations_fail_without_output_even_optimized(self):
        for flags in ([], ["-O"]):
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                expected = json.loads((ROOT / "expected.json").read_text())
                expected["workflows"][0]["python_name"] = "wrong"
                (root / "bad.json").write_text(json.dumps(expected))
                result = subprocess.run(
                    [sys.executable, *flags, str(ROOT / "inspect_definitions.py"),
                     "--expected", str(root / "bad.json"), "--output", str(root / "output.json")],
                    capture_output=True, text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Observation mismatch", result.stderr)
                self.assertFalse((root / "output.json").exists())


if __name__ == "__main__":
    unittest.main()
