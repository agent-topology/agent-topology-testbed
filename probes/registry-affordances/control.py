"""Save and run the deliberately wrong X1 expectation control."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from setup import save

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    expected = json.loads((ROOT / "expectations.json").read_text())
    expected["cases"]["direct-fanout"]["fact"][2]["value"] = "deliberately-wrong"
    wrong = out / "wrong-expectations.json"
    save(wrong, expected)
    report = out / "comparison.json"
    command = [sys.executable, "-O", str(ROOT / "verify.py"),
               str(args.evidence.resolve()), "--expected", str(wrong), "--report", str(report)]
    result = subprocess.run(command, capture_output=True, text=True)
    save(out / "command.json", {"command": command, "exit": result.returncode,
                                 "stdout": result.stdout, "stderr": result.stderr})
    if result.returncode != 1:
        raise RuntimeError("deliberately wrong expectation did not fail with exit 1")
    errors = json.loads(report.read_text())["errors"]
    if not any("fact router/branch" in error for error in errors):
        raise RuntimeError("control failed for the wrong reason")
    print(json.dumps({"expectedExit": 1, "actualExit": result.returncode, "errors": len(errors)}))


if __name__ == "__main__":
    main()
