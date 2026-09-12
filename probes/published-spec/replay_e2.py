"""E2: replay E1's saved bytes through the four V2 published installations.

The generator is never imported or run. Input hashes and the complete minimized
inventory are checked before the lock-only V2 setup starts.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from run_v2 import VERSIONS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E1 = ROOT / "observations/E1"
OBSERVATION = ROOT / "observations/E2"
EXPECTATIONS = OBSERVATION / "expectations.json"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_inputs():
    expected = json.loads(EXPECTATIONS.read_text())
    sources = expected["input_sources"]
    population_path = ROOT / sources["population_gzip"]
    cases_path = ROOT / sources["cases"]
    compressed = population_path.read_bytes()
    population = gzip.decompress(compressed)
    cases_raw = cases_path.read_bytes()
    require(digest(compressed) == sources["population_gzip_sha256"], "E1 population gzip changed")
    require(digest(population) == sources["population_uncompressed_sha256"], "E1 population bytes changed")
    require(digest(cases_raw) == sources["cases_sha256"], "E1 cases changed")
    lines = population.splitlines(keepends=True)
    cases = json.loads(cases_raw)
    require(len(lines) == len(cases) == sources["population_lines"], "E1 population count changed")
    for raw, case in zip(lines, cases):
        require(raw.endswith(b"\n"), f"E1 input lost newline: {case['case']}")
        require(digest(raw) == case["input_sha256"], f"E1 case digest changed: {case['case']}")

    repeat_population = (E1 / "run-b/inputs.jsonl.gz").read_bytes()
    repeat_cases = (E1 / "run-b/cases.json").read_bytes()
    require(repeat_population == compressed and repeat_cases == cases_raw, "E1 authoritative runs disagree")

    minimized_dir = ROOT / sources["minimized_directory"]
    minimized = []
    for sha in sources["minimized_sha256"]:
        path = minimized_dir / f"{sha}.json"
        raw = path.read_bytes()
        require(digest(raw) == sha, f"E1 minimized input changed: {sha}")
        minimized.append((sha, raw))
    actual = sorted(path.stem for path in minimized_dir.glob("*.json") if not path.name.endswith("-replay.json"))
    require(actual == sources["minimized_sha256"], "E1 minimized inventory changed")

    boundaries = []
    for name, oracle in sorted(expected["boundary_cases"].items()):
        raw = (OBSERVATION / "boundary" / name).read_bytes()
        require(digest(raw) == oracle["sha256"], f"E2 boundary input changed: {name}")
        boundaries.append((Path(name).stem, raw))
    return expected, population, cases, minimized, boundaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    require(not envs.exists() and not out.exists(), "use new environment and output directories")

    expected, population, cases, minimized, boundaries = checked_inputs()
    out.mkdir(parents=True)
    save(out / "inputs-before-install.json", {
        "expectations": expected,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "generator_rerun": False,
        "verified_population_cases": len(cases),
        "verified_minimized_candidates": len(minimized),
        "verified_boundary_cases": len(boundaries),
    })

    clean_env = {key: value for key, value in os.environ.items()
                 if key not in {"PYTHONPATH", "PYTHONHOME", "NODE_PATH", "NODE_OPTIONS"}}
    commands = []

    def run(command, cwd=ROOT, raw=None, allowed=(0,), stdout_path=None):
        started = datetime.now(timezone.utc).isoformat()
        before = time.monotonic()
        process = subprocess.run([str(value) for value in command], cwd=cwd, env=clean_env,
                                 input=raw, capture_output=True)
        record = {
            "command": [str(value) for value in command],
            "cwd": str(cwd),
            "started_at": started,
            "seconds": time.monotonic() - before,
            "exit": process.returncode,
            "stdout_sha256": digest(process.stdout),
            "stderr": process.stderr.decode(),
        }
        if stdout_path is not None:
            stdout_path.parent.mkdir(parents=True, exist_ok=True)
            if stdout_path.suffix == ".gz":
                stdout_path.write_bytes(gzip.compress(process.stdout, mtime=0))
            else:
                stdout_path.write_bytes(process.stdout)
            record["stdout_path"] = str(stdout_path.relative_to(out))
        else:
            record["stdout"] = process.stdout.decode()
        commands.append(record)
        save(out / "commands.json", commands)
        require(process.returncode in allowed, f"command failed: {command}; see {out}/commands.json")
        return process

    # V2 owns the four lock-only isolated installations and validates their
    # artifacts/import identities. Its nine-document calls are retained under setup/.
    run([sys.executable, HERE / "run_v2.py", "--envs", envs, "--out", out / "setup"])

    identities = {}
    for label, version in VERSIONS.items():
        target = envs / label
        if label.startswith("py"):
            command = [target / "bin/python", "-I", HERE / "generated/batch.py"]
            one_shot = [target / "bin/python", "-I", HERE / "adapter.py"]
        else:
            shutil.copyfile(HERE / "generated/batch.mjs", target / "batch.mjs")
            command = ["node", target / "batch.mjs"]
            one_shot = ["node", target / "adapter.mjs"]

        batch_path = out / "population" / f"{label}.jsonl.gz"
        process = run(command, target, population, stdout_path=batch_path)
        rows = process.stdout.splitlines()
        require(len(rows) == len(cases), f"population result count mismatch: {label}")
        first = json.loads(rows[0])
        require(first["identity"]["version"] == version, f"wrong package version: {label}")
        require(str(target) + "/" in first["identity"]["imported_path"], f"import escaped installation: {label}")
        identities[label] = first["identity"]

        for sha, raw in minimized:
            result_path = out / "minimized" / sha / f"{label}.json"
            process = run(one_shot, target, raw, allowed=(0, 2), stdout_path=result_path)
            record = json.loads(process.stdout)
            require(record["identity"]["version"] == version, f"wrong package version: {label}/{sha}")
            require(record["input_sha256"] == sha, f"minimized adapter input mismatch: {label}/{sha}")

        for name, raw in boundaries:
            result_path = out / "boundary" / name / f"{label}.json"
            process = run(one_shot, target, raw, allowed=(0, 2), stdout_path=result_path)
            record = json.loads(process.stdout)
            require(record["identity"]["version"] == version, f"wrong package version: {label}/{name}")
            require(record["input_sha256"] == digest(raw), f"boundary adapter input mismatch: {label}/{name}")

    save(out / "identities.json", identities)
    sources = [HERE / name for name in ("replay_e2.py", "compare_e2.py", "adapter.py", "adapter.mjs")]
    sources += [HERE / "generated/batch.py", HERE / "generated/batch.mjs", EXPECTATIONS]
    save(out / "provenance.json", {
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "callable; installed-package evaluation, no framework execution",
        "generator_rerun": False,
        "sources_sha256": {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in sources},
        "locks_sha256": {str(path.relative_to(ROOT)): digest(path.read_bytes())
                         for path in sorted((HERE / "locks").rglob("*")) if path.is_file()},
        "commands_seconds": sum(command["seconds"] for command in commands),
    })
    run([sys.executable, "-O", HERE / "compare_e2.py", out])
    print(f"PASS E2: 600 saved inputs plus 16 minima and 2 boundaries; {out}")


if __name__ == "__main__":
    main()
