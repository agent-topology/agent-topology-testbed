"""K1: isolated registry installs and fresh-process public calls against six
compatibility-boundary documents plus one direct hash-computation-boundary call.

Reuses V1's isolated-installation pattern and locked dependencies (published-spec/locks/)
so this probe does not maintain a second, potentially drifting pin of the same four
packages. Reuses V1's minimal accepted document as the base for every mutation.
Output and environment directories must be new to prevent stale evidence reuse.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mutate import DOCUMENT_CASES, HASH_BOUNDARY_CASE, HASH_BOUNDARY_REQUESTED_VERSION  # noqa: E402

HERE = Path(__file__).resolve().parent
PUBLISHED_SPEC = HERE.parent / "published-spec"
K1 = HERE.parents[1] / "observations/K1"
VERSIONS = {"py-b1": "0.1.0b1", "py-b2": "0.1.0b2", "js-b1": "0.1.0-beta.1", "js-b2": "0.1.0-beta.2"}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def case_bytes(name):
    return (json.dumps(DOCUMENT_CASES[name](), indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    require(not envs.exists() and not out.exists(), "use new environment and output directories")
    envs.mkdir(parents=True)
    out.mkdir(parents=True)

    manifest = json.loads((K1 / "cases.json").read_text())
    for name in DOCUMENT_CASES:
        raw = case_bytes(name)
        require(digest(raw) == manifest["cases"][name]["sha256"], f"case document changed: {name}")
        require(raw == (K1 / "cases" / f"{name}.json").read_bytes(), f"committed case document drifted: {name}")
    save(out / "cases-before-install.json", manifest)

    clean_env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME", "NODE_PATH", "NODE_OPTIONS"}}
    commands = []

    def run(command, cwd=envs, raw=None, allowed=(0,)):
        started = datetime.now(timezone.utc).isoformat()
        before = time.monotonic()
        p = subprocess.run([str(x) for x in command], cwd=cwd, env=clean_env, input=raw, capture_output=True)
        commands.append({"command": [str(x) for x in command], "cwd": str(cwd), "started_at": started,
                         "seconds": time.monotonic() - before, "exit": p.returncode,
                         "stdout": p.stdout.decode(), "stderr": p.stderr.decode()})
        save(out / "commands.json", commands)
        require(p.returncode in allowed, f"command failed: {command}; see {out}/commands.json")
        return p

    artifacts = []
    identities = {}
    for label, version in VERSIONS.items():
        target = envs / label
        lockdir = PUBLISHED_SPEC / "locks" / label
        if label.startswith("py"):
            run([sys.executable, "-m", "venv", target])
            python = target / "bin/python"
            install = [python, "-I", "-m", "pip", "--isolated", "install", "--index-url", "https://pypi.org/simple",
                       "--only-binary=:all:", "--report", out / f"{label}-install.json",
                       "--require-hashes", "-r", lockdir / "requirements.lock"]
            run(install)
            report = json.loads((out / f"{label}-install.json").read_text())
            run([python, "-I", "-m", "pip", "freeze", "--all"])
            for p in report["install"]:
                info = p["download_info"]
                raw = urllib.request.urlopen(info["url"]).read()
                sha = digest(raw)
                require(sha == info["archive_info"]["hashes"]["sha256"], "Python artifact digest mismatch")
                artifacts.append({"installation": label, "package": p["metadata"]["name"], "version": p["metadata"]["version"], "url": info["url"], "sha256": sha})
            shutil.copyfile(PUBLISHED_SPEC / "adapter.py", target / "adapter.py")
            shutil.copyfile(HERE / "hash_adapter.py", target / "hash_adapter.py")
            adapter_command = [python, "-I", target / "adapter.py"]
            hash_command = [python, "-I", target / "hash_adapter.py", HASH_BOUNDARY_REQUESTED_VERSION]
        else:
            target.mkdir()
            for name in ("package.json", "package-lock.json"):
                shutil.copyfile(lockdir / name, target / name)
            run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund", "--registry=https://registry.npmjs.org"], target)
            run(["npm", "ls", "--all", "--json"], target)
            lock = json.loads((target / "package-lock.json").read_text())
            for name, p in lock["packages"].items():
                if not name:
                    continue
                raw = urllib.request.urlopen(p["resolved"]).read()
                import base64
                algorithm, expected = p["integrity"].split("-", 1)
                require(base64.b64encode(hashlib.new(algorithm, raw).digest()).decode() == expected, "npm integrity mismatch")
                artifacts.append({"installation": label, "package": name, "version": p["version"], "url": p["resolved"], "integrity": p["integrity"], "sha256": digest(raw)})
            shutil.copyfile(PUBLISHED_SPEC / "adapter.mjs", target / "adapter.mjs")
            shutil.copyfile(HERE / "hash_adapter.mjs", target / "hash_adapter.mjs")
            adapter_command = ["node", target / "adapter.mjs"]
            hash_command = ["node", target / "hash_adapter.mjs", HASH_BOUNDARY_REQUESTED_VERSION]
        save(out / "artifacts.json", artifacts)

        for name in DOCUMENT_CASES:
            raw = case_bytes(name)
            for repeat in (1, 2):
                p = run(adapter_command, target, raw, allowed=(0, 2, 3))
                record = json.loads(p.stdout)
                require(record["identity"]["version"] == version, f"wrong package version: {label}")
                require(str(target) + "/" in record["identity"]["imported_path"], f"import escaped installation: {label}")
                require(record["input_sha256"] == digest(raw), "adapter input mismatch")
                require(p.returncode == {"accepted": 0, "rejected": 2, "error": 3}[record["status"]], "adapter exit/status mismatch")
                identities[label] = record["identity"]
                save(out / f"{label}-{name}-{repeat}.json", record)

        base_raw = case_bytes("baseline")
        for repeat in (1, 2):
            p = run(hash_command, target, base_raw, allowed=(0, 3))
            record = json.loads(p.stdout)
            require(record["identity"]["version"] == version, f"wrong package version: {label}")
            require(str(target) + "/" in record["identity"]["imported_path"], f"import escaped installation: {label}")
            require(record["input_sha256"] == digest(base_raw), "hash adapter input mismatch")
            require(record["requested_algorithm_version"] == HASH_BOUNDARY_REQUESTED_VERSION, "wrong requested algorithm version")
            require(p.returncode == {"computed": 0, "error": 3}[record["status"]], "hash adapter exit/status mismatch")
            save(out / f"{label}-{HASH_BOUNDARY_CASE}-{repeat}.json", record)

    save(out / "identities.json", identities)
    save(out / "provenance.json", {"finished_at": datetime.now(timezone.utc).isoformat(),
         "evidence_class": "callable; retrospective installed-package evaluation, no framework execution",
         "sources_sha256": {p.name: digest(p.read_bytes()) for p in (
             HERE / "run.py", HERE / "mutate.py", HERE / "hash_adapter.py", HERE / "hash_adapter.mjs", HERE / "compare.py",
             PUBLISHED_SPEC / "adapter.py", PUBLISHED_SPEC / "adapter.mjs")},
         "locks_sha256": {str(p.relative_to(PUBLISHED_SPEC)): digest(p.read_bytes()) for p in sorted((PUBLISHED_SPEC / "locks").rglob("*")) if p.is_file()},
         "commands_seconds": sum(c["seconds"] for c in commands)})
    run([sys.executable, "-O", HERE / "compare.py", out])
    print(f"PASS K1: four isolated installs, {4 * (2 * len(DOCUMENT_CASES) + 2)} fresh-process calls; {out}")


if __name__ == "__main__":
    main()
