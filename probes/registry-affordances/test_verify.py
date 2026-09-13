"""Deterministic saved-evidence and negative-control checks for X1."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from verify import verify

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT.parents[1] / "observations/X1/run"


class VerifyTests(unittest.TestCase):
    def test_saved_evidence(self):
        self.assertEqual(verify(EVIDENCE)["errors"], [])

    def test_deliberately_wrong_expectation_fails_nonzero(self):
        expected = json.loads((ROOT / "expectations.json").read_text())
        expected["cases"]["direct-fanout"]["fact"][2]["value"] = "wrong"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.json"
            report = Path(directory) / "report.json"
            path.write_text(json.dumps(expected))
            result = subprocess.run([sys.executable, "-O", str(ROOT / "verify.py"),
                                     str(EVIDENCE), "--expected", str(path), "--report", str(report)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(any("fact router/branch" in error for error in json.loads(report.read_text())["errors"]))

    def test_missing_capture_and_workspace_import_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            copy_to = Path(directory) / "run"
            import shutil
            shutil.copytree(EVIDENCE, copy_to)
            (copy_to / "typescript-sentinels-2.json").unlink()
            path = copy_to / "python-sentinels-1.json"
            before = path.read_text()
            record = json.loads(path.read_text())
            record["identity"]["imports"]["spec"] = str(ROOT / "fake.py")
            after = json.dumps(record)
            path.write_text(after)
            commands = json.loads((copy_to / "commands.json").read_text())
            for command in commands:
                if command["stdout"] == before:
                    command["stdout"] = after
            (copy_to / "commands.json").write_text(json.dumps(commands))
            errors = verify(copy_to)["errors"]
            self.assertTrue(any("workspace/editable/linked import" in error for error in errors))
            self.assertTrue(any("typescript-sentinels-2" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
