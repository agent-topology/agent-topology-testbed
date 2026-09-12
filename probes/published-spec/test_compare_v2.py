"""Deterministic controls for the V2 comparison classifications."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from compare_v2 import compare
from run_v2 import EXPECTATIONS, HERE, INPUTS, save


class V2ComparisonControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "records"
        shutil.copytree(INPUTS.parent / "V2" / "run", self.out)
        self.manifest = json.loads((INPUTS / "inputs.json").read_text())
        self.expectations = json.loads(EXPECTATIONS.read_text())

    def mutate(self, label, change):
        for repeat in (1, 2):
            path = self.out / f"{label}-minimal-{repeat}.json"
            record = json.loads(path.read_text())
            change(record)
            save(path, record)

    def test_corrupted_expected_value_exits_one(self):
        expected = deepcopy(self.expectations)
        expected["inputs"]["minimal.json"]["expected_full_canonical_bytes"] = "different"
        path = self.out / "corrupted-expectations.json"
        save(path, expected)
        result = subprocess.run([sys.executable, "-O", HERE / "compare_v2.py", self.out, "--expected", path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads((self.out / "comparison.json").read_text())
        self.assertEqual(len(report["expectation_mismatches"]), 3)

    def test_algorithm_transition_is_separate(self):
        self.mutate("py-b3", lambda record: record["structureHash"].update(algorithmVersion="2", value="0" * 64))
        report = compare(self.out, self.manifest, self.expectations)
        self.assertGreater(len(report["algorithm_transitions"]), 0)
        self.assertEqual(report["hash_disagreements"], [])

    def test_same_algorithm_hash_disagreement_is_structural(self):
        self.mutate("py-b3", lambda record: record["structureHash"].update(value="0" * 64))
        report = compare(self.out, self.manifest, self.expectations)
        self.assertGreater(len(report["hash_disagreements"]), 0)
        self.assertEqual(report["algorithm_transitions"], [])

    def test_canonical_difference_is_separate(self):
        self.mutate("py-b3", lambda record: record.update(canonical=record["canonical"] + "\n"))
        report = compare(self.out, self.manifest, self.expectations)
        self.assertEqual(len(report["canonical_differences"]), 2)
        self.assertEqual(report["hash_disagreements"], [])

    def test_rejection_is_excluded(self):
        self.mutate("py-b3", lambda record: record.update(status="rejected", validation={"accepted": False, "errors": ["synthetic rejection"]}))
        report = compare(self.out, self.manifest, self.expectations)
        self.assertEqual(len(report["rejected"]), 1)
        self.assertEqual(sum(row["validation"] == "excluded-rejected" for row in report["comparisons"]), 2)

    def test_missing_repeat_fails(self):
        (self.out / "py-b3-minimal-2.json").unlink()
        with self.assertRaises(FileNotFoundError):
            compare(self.out, self.manifest, self.expectations)

    def test_adapter_error_is_not_rejection(self):
        self.mutate("py-b3", lambda record: record.update(status="error"))
        with self.assertRaisesRegex(ValueError, "adapter error"):
            compare(self.out, self.manifest, self.expectations)

    def test_wrong_identity_fails(self):
        self.mutate("py-b3", lambda record: record["identity"].update(version="local"))
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            compare(self.out, self.manifest, self.expectations)


if __name__ == "__main__":
    unittest.main()
