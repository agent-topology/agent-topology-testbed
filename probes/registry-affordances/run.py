"""Run every X1 case twice in fresh language processes and retain raw receipts."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from setup import ROOT, REPO, save


def command(args, cwd, out, records, expected=0):
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    result = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, text=True, timeout=120)
    record = {"command": list(map(str, args)), "cwd": str(cwd), "startedAt": started,
              "seconds": time.monotonic() - clock, "exit": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr}
    records.append(record); save(out / "commands.json", records)
    if (expected == 0 and result.returncode != 0) or (expected == "nonzero" and result.returncode == 0):
        raise RuntimeError(f"unexpected exit; see {out / 'commands.json'}")
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--envs", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    if not envs.exists() or out.exists():
        raise ValueError("use an existing isolated environment and a new output directory")
    if envs.is_relative_to(REPO):
        raise ValueError("environments must be outside the checkout")
    out.mkdir(parents=True)
    expectations = json.loads((ROOT / "expectations.json").read_text())
    save(out / "inputs-before-extraction.json", expectations)
    workers = out / "workers"; workers.mkdir()
    for name in ("worker.py", "worker.mts", "cli_fixture.py", "require-spec.cjs"):
        shutil.copyfile(ROOT / name, workers / name)
    records = []
    py, js = envs / "python", envs / "typescript"
    # Node resolves packages relative to the importing module, so execute its
    # copied workers inside the isolated installation as well as retaining the
    # exact source copies with the evidence.
    shutil.copyfile(ROOT / "worker.mts", js / "worker.mts")
    shutil.copyfile(ROOT / "require-spec.cjs", js / "require-spec.cjs")
    for language, worker, executable in (
        ("python", workers / "worker.py", py / "bin/python"),
        ("typescript", js / "worker.mts", shutil.which("node"))):
        for case in expectations["cases"]:
            for repeat in (1, 2):
                args_ = [executable, "-I", worker, case] if language == "python" else [executable, "--experimental-strip-types", worker, case]
                receipt = command(args_, py if language == "python" else js, out, records)
                (out / f"{language}-{case}-{repeat}.json").write_text(receipt["stdout"])
    for repeat in (1, 2):
        target = f"{workers / 'cli_fixture.py'}:graph"
        cli_out = out / f"python-orphan-router-cli-{repeat}.json"
        command([py / "bin/agt", "describe", target, "--out", cli_out,
                 "--graph-id", "custom-router"], py, out, records)
        receipt = command([shutil.which("node"), js / "require-spec.cjs"], js, out, records, "nonzero")
        save(out / f"commonjs-require-{repeat}.json", receipt)
    sources = [ROOT / name for name in ("expectations.json", "worker.py", "worker.mts", "cli_fixture.py", "require-spec.cjs", "run.py", "setup.py", "verify.py")]
    save(out / "provenance.json", {"completedAt": datetime.now(timezone.utc).isoformat(),
         "sources": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}})
    from verify import verify
    report = verify(out)
    save(out / "comparison.json", report)
    print(json.dumps(report["summary"]))
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
