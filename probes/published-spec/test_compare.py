"""Controls for evidence classification, using copies of the saved observations."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from compare import compare
from run import HERE, INPUTS, save


class ComparisonControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "records"
        shutil.copytree(INPUTS / "run", self.out)
        self.manifest = json.loads((INPUTS / "inputs.json").read_text())

    def mutate(self, change):
        for n in (1, 2):
            p = self.out / f"py-b1-minimal-{n}.json"
            record = json.loads(p.read_text())
            change(record)
            save(p, record)

    def test_corrupted_expected_hash_exits_one(self):
        expected = deepcopy(self.manifest)
        expected["inputs"]["minimal.json"]["expected_hash"]["value"] = "0" * 64
        path = self.out / "corrupted-expected.json"
        save(path, expected)
        result = subprocess.run([sys.executable, "-O", HERE / "compare.py", self.out, "--expected", path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads((self.out / "comparison.json").read_text())
        self.assertEqual(len(report["hash_disagreements"]), 4)
        self.assertEqual(report["algorithm_transitions"], [])

    def test_algorithm_transition_is_not_hash_drift(self):
        self.mutate(lambda r: r["structureHash"].update(algorithmVersion="2", value="0" * 64))
        report = compare(self.out, self.manifest)
        self.assertEqual(len(report["algorithm_transitions"]), 3)
        self.assertEqual(report["hash_disagreements"], [])

    def test_canonical_difference_is_not_hash_drift(self):
        self.mutate(lambda r: r.update(canonical=r["canonical"] + "\n"))
        report = compare(self.out, self.manifest)
        self.assertEqual(len(report["canonical_differences"]), 2)
        self.assertEqual(report["hash_disagreements"], [])

    def test_rejected_input_is_excluded(self):
        self.mutate(lambda r: r.update(status="rejected", validation={"accepted": False, "errors": ["synthetic rejection"]}))
        report = compare(self.out, self.manifest)
        self.assertEqual(len(report["rejected"]), 1)
        self.assertEqual(sum(p["status"] == "excluded-rejected" for p in report["comparisons"]), 2)
        self.assertEqual(report["hash_disagreements"], [])

    def test_missing_repeat_fails(self):
        (self.out / "py-b1-minimal-2.json").unlink()
        with self.assertRaises(FileNotFoundError):
            compare(self.out, self.manifest)

    def test_adapter_error_is_not_rejection(self):
        self.mutate(lambda r: r.update(status="error"))
        with self.assertRaisesRegex(ValueError, "adapter error"):
            compare(self.out, self.manifest)

    def test_wrong_identity_fails(self):
        self.mutate(lambda r: r["identity"].update(version="local"))
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            compare(self.out, self.manifest)


if __name__ == "__main__":
    unittest.main()
