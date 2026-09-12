import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from probe import HERE
from verify import validate

ROOT = HERE.parents[2]
RECORD = ROOT / "observations/P8/run-1.json"


class EvidenceIntegrity(unittest.TestCase):
    def test_static_never_enters_fixture_bodies(self):
        with tempfile.TemporaryDirectory() as temp:
            # Profile all four fixture bodies, including flows with no task calls.
            script = '''
import runpy, sys
from pathlib import Path

def guard(frame, event, arg):
    if event == "call" and Path(frame.f_code.co_filename).name == "fixtures.py" and frame.f_code.co_name in {"linear", "loop", "task_a", "task_b"}:
        raise RuntimeError("static inspection entered a fixture body")
sys.setprofile(guard)
sys.argv.pop(0)
runpy.run_path(sys.argv[0], run_name="__main__")
'''
            result = subprocess.run([sys.executable, "-c", script, str(HERE / "probe.py"),
                                     "--static-only", "--output", temp + "/static.json"],
                                    cwd=HERE, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_corrupt_expectations_fail_normal_and_optimized(self):
        expected = json.loads((HERE / "expected.json").read_text())
        expected["static"]["flow_names"][0] = "wrong"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "expected.json"
            path.write_text(json.dumps(expected))
            for flags in [[], ["-O"]]:
                output = Path(temp) / "must-not-exist.json"
                result = subprocess.run([sys.executable, *flags, str(HERE / "probe.py"),
                                         "--static-only", "--expected", str(path),
                                         "--output", str(output)],
                                        capture_output=True, text=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("static flow_names", result.stderr)
                self.assertFalse(output.exists())

    def test_native_corruption_rejected(self):
        record = json.loads(RECORD.read_text())
        original = json.loads(RECORD.with_suffix(".raw.json").read_text())
        expected = json.loads((HERE / "expected.json").read_text())
        for mutation in ["duplicate", "edge", "order"]:
            raw = copy.deepcopy(original)
            rows = raw["loop-2"]["task_runs"]
            if mutation == "duplicate":
                rows.append(copy.deepcopy(rows[0]))
            elif mutation == "edge":
                rows[3]["task_run"]["task_inputs"]["value"][0]["id"] = rows[0]["task_run"]["id"]
            else:
                rows[0]["states"].reverse()
            label = {"duplicate": "native invocation count", "edge": "native dependencies",
                     "order": "native states"}[mutation]
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, label):
                validate(record, raw, expected)


if __name__ == "__main__":
    unittest.main()
