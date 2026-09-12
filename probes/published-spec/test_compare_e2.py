"""Deterministic controls for the E2 saved-evidence comparator."""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from replay_e2 import HERE, OBSERVATION


class E2ComparisonControls(unittest.TestCase):
    def setUp(self):
        source = OBSERVATION / "run-a"
        if not source.exists():
            self.skipTest("saved E2 evidence has not been captured yet")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.records = Path(self.temp.name) / "records"
        self.records.mkdir()
        for name in ("population", "minimized", "boundary"):
            shutil.copytree(source / name, self.records / name)

    def test_saved_replay_passes(self):
        result = subprocess.run(
            [sys.executable, "-O", HERE / "compare_e2.py", self.records],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_altered_adapter_result_fails_nonzero(self):
        path = self.records / "population/py-b3.jsonl.gz"
        rows = gzip.decompress(path.read_bytes()).splitlines()
        record = json.loads(rows[0])
        record["canonical"] += " "
        rows[0] = json.dumps(record, ensure_ascii=False).encode()
        path.write_bytes(gzip.compress(b"\n".join(rows) + b"\n", mtime=0))
        result = subprocess.run(
            [sys.executable, "-O", HERE / "compare_e2.py", self.records],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("beta.3 canonical mismatch", result.stdout)


if __name__ == "__main__":
    unittest.main()
