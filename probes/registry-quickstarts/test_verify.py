"""Negative controls for Q1's saved-evidence verifier; no framework execution."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import verify

RUN = verify.INPUT / "run-1"


class Controls(unittest.TestCase):
    def test_baseline(self):
        verify.verify_run(RUN)

    def test_duplicate_edge(self):
        doc = verify.read(RUN / "python-cli.json")
        doc["graphs"][0]["structure"]["edges"].append(
            deepcopy(doc["graphs"][0]["structure"]["edges"][0]))
        with self.assertRaisesRegex(ValueError, "multiplicity"):
            verify.check_document(doc)

    def test_missing_greet(self):
        doc = verify.read(RUN / "python-cli.json")
        doc["graphs"][0]["structure"]["nodes"].pop()
        with self.assertRaisesRegex(ValueError, "node identities"):
            verify.check_document(doc)

    def test_only_clock_is_removed(self):
        a = verify.read(RUN / "python-cli.json")
        b = deepcopy(a)
        b["provenance"]["generatedAt"] = "another clock"
        self.assertEqual(verify.semantic(a), verify.semantic(b))
        b["provenance"]["producer"]["version"] = "different"
        self.assertNotEqual(verify.semantic(a), verify.semantic(b))

    def corrupt(self, filename, mutate, error):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "copy"
            shutil.copytree(RUN, out)
            path = out / filename
            value = json.loads(path.read_text())
            mutate(value)
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, error):
                verify.verify_run(out)

    def test_missing_command(self):
        self.corrupt("commands.json", lambda c: c.pop(), "missing/reordered")

    def test_nonzero_command(self):
        self.corrupt("commands.json", lambda c: c[4].update(exit=6), "failed command")

    def test_import_escape(self):
        self.corrupt("python-audit.json",
                     lambda c: c["imports"].update({"agent_topology.spec": "/checkout/spec.py"}),
                     "audit receipt")

    def test_bad_hash_optimized_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "copy"
            shutil.copytree(RUN, out)
            path = out / "python-cli.json"
            doc = json.loads(path.read_text())
            doc["structureHash"]["value"] = "0" * 64
            path.write_text(json.dumps(doc))
            p = subprocess.run([sys.executable, "-O", str(Path(verify.__file__)),
                                str(out), str(RUN)], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("API oracle failed", p.stderr)


if __name__ == "__main__":
    unittest.main()
