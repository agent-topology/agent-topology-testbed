"""Corrupt saved evidence; no framework installs or extraction reruns."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from verify import compare, projection, verify

EVIDENCE = Path(__file__).resolve().parents[2] / "observations/D1/run"


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((EVIDENCE / "python-linear-base-1.json").read_text())["describes"][0]["document"]

    def test_saved_evidence(self):
        self.assertEqual(verify(EVIDENCE)["errors"], [])

    def test_hash_only_drift(self):
        changed = copy.deepcopy(self.document)
        changed["structureHash"]["value"] = "0"*64
        self.assertEqual(compare(self.document, changed)["classification"], "hash-computation-drift")

    def test_process_repr_is_not_normalized(self):
        changed = copy.deepcopy(self.document)
        changed["graphs"][0]["structure"]["nodes"][2]["id"] = "<step at 0x1234>"
        self.assertEqual(compare(self.document, changed)["classification"], "extraction-drift")

    def test_duplicates_are_not_deduplicated(self):
        changed = copy.deepcopy(self.document)
        structure = changed["graphs"][0]["structure"]
        structure["edges"].append(copy.deepcopy(structure["edges"][0]))
        self.assertNotEqual(projection(self.document), projection(changed))

    def test_metadata_remains_visible_outside_projection(self):
        changed = copy.deepcopy(self.document)
        changed["graphs"][0]["x-example"] = "new metadata"
        result = compare(self.document, changed)
        self.assertEqual(result["classification"], "stable")
        self.assertIn("/graphs/0/x-example", result["rawDifferences"])

    def test_corruption_fails_cli_under_optimization(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "evidence"
            shutil.copytree(EVIDENCE, out)
            path = out / "python-linear-base-1.json"
            before = path.read_text()
            record = json.loads(before)
            record["describes"][0]["computedHash"]["value"] = "0"*64
            after = json.dumps(record)
            path.write_text(after)
            # Keep the receipt internally consistent to exercise the hash oracle.
            commands = json.loads((out / "commands.json").read_text())
            for command in commands:
                if command["stdout"] == before: command["stdout"] = after
            (out / "commands.json").write_text(json.dumps(commands))
            report = Path(directory) / "report.json"
            result = subprocess.run([sys.executable, "-O", str(Path(__file__).with_name("verify.py")),
                                     str(out), "--report", str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertTrue(any("hash computation/oracle" in e for e in json.loads(report.read_text())["errors"]))

    def test_missing_capture_and_wrong_version_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "evidence"
            shutil.copytree(EVIDENCE, out)
            (out / "typescript-join-independent-2.json").unlink()
            path = out / "python-linear-base-1.json"
            before = path.read_text()
            record = json.loads(before)
            record["identity"]["versions"]["langgraph"] = "0.0.0"
            after = json.dumps(record)
            path.write_text(after)
            commands = json.loads((out / "commands.json").read_text())
            for command in commands:
                if command["stdout"] == before: command["stdout"] = after
            (out / "commands.json").write_text(json.dumps(commands))
            errors = verify(out)["errors"]
            self.assertGreaterEqual(len(errors), 2)
            self.assertTrue(any("package identity" in e for e in errors))

    def test_positive_control_cannot_reuse_base(self):
        # A constant producer/hasher output must fail the independent topology oracle.
        from verify import check_oracle
        for variant in ("node-change", "edge-change"):
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                check_oracle(self.document, "linear", variant)


if __name__ == "__main__":
    unittest.main()
