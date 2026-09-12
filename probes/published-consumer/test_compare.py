"""Controls for K1's evidence classification, using copies of the saved observations."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from compare import compare
from mutate import HASH_BOUNDARY_CASE
from run import HERE, K1, save


class ComparisonControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "records"
        shutil.copytree(K1 / "run", self.out)
        self.manifest = json.loads((K1 / "cases.json").read_text())

    def mutate(self, key, change):
        for n in (1, 2):
            p = self.out / f"{key}-{n}.json"
            record = json.loads(p.read_text())
            change(record)
            save(p, record)

    def test_corrupted_expected_hash_exits_one(self):
        expected = deepcopy(self.manifest)
        expected["cases"]["baseline"]["expected"]["structureHash"]["value"] = "0" * 64
        path = self.out / "corrupted-expected.json"
        save(path, expected)
        result = subprocess.run([sys.executable, "-O", HERE / "compare.py", self.out, "--expected", path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads((self.out / "comparison.json").read_text())
        self.assertEqual(len(report["mismatches"]), 4)
        for row in report["mismatches"]:
            self.assertEqual(row["case"], "baseline")

    def test_flipping_a_rejection_to_accepted_is_caught(self):
        self.mutate("py-b1-unsupported-topology-version", lambda r: r.update(status="accepted", validation={"accepted": True, "errors": []}, canonical="{}", structureHash={"algorithm": "sha256", "algorithmVersion": "1", "value": "0" * 64}))
        report = compare(self.out, self.manifest)
        self.assertEqual(len(report["mismatches"]), 1)
        self.assertEqual(report["mismatches"][0]["case"], "unsupported-topology-version")
        self.assertEqual(report["mismatches"][0]["installation"], "py-b1")

    def test_hash_drift_on_an_accepted_case_is_caught(self):
        self.mutate("js-b2-unknown-permitted-extension", lambda r: r["structureHash"].update(value="1" * 64))
        report = compare(self.out, self.manifest)
        self.assertEqual(len(report["mismatches"]), 1)
        self.assertEqual(report["mismatches"][0]["case"], "unknown-permitted-extension")
        self.assertEqual(report["mismatches"][0]["installation"], "js-b2")

    def test_hash_boundary_error_type_drift_is_caught(self):
        self.mutate(f"py-b2-{HASH_BOUNDARY_CASE}", lambda r: r["error"].update(type="RangeError"))
        report = compare(self.out, self.manifest)
        self.assertEqual(len(report["mismatches"]), 1)
        self.assertEqual(report["mismatches"][0]["case"], HASH_BOUNDARY_CASE)
        self.assertEqual(report["mismatches"][0]["installation"], "py-b2")

    def test_hash_boundary_recovering_instead_of_erroring_is_caught(self):
        self.mutate(f"js-b1-{HASH_BOUNDARY_CASE}", lambda r: r.update(status="computed", structureHash={"algorithm": "sha256", "algorithmVersion": "2", "value": "0" * 64}))
        report = compare(self.out, self.manifest)
        self.assertEqual(len(report["mismatches"]), 1)
        self.assertEqual(report["mismatches"][0]["case"], HASH_BOUNDARY_CASE)
        self.assertEqual(report["mismatches"][0]["installation"], "js-b1")

    def test_missing_repeat_fails(self):
        (self.out / "py-b1-baseline-2.json").unlink()
        with self.assertRaises(FileNotFoundError):
            compare(self.out, self.manifest)

    def test_fresh_process_disagreement_fails(self):
        p = self.out / "py-b2-malformed-extension-key-1.json"
        record = json.loads(p.read_text())
        record["validation"]["errors"] = record["validation"]["errors"] + ["synthetic, repeat 1 only"]
        save(p, record)
        with self.assertRaisesRegex(ValueError, "fresh-process disagreement"):
            compare(self.out, self.manifest)

    def test_wrong_identity_fails(self):
        self.mutate("py-b1-baseline", lambda r: r["identity"].update(version="local"))
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            compare(self.out, self.manifest)

    def test_the_real_saved_records_have_no_mismatches(self):
        report = compare(self.out, self.manifest)
        self.assertEqual(report["mismatches"], [])
        self.assertEqual(report["summary"]["rows"], 28)


if __name__ == "__main__":
    unittest.main()
