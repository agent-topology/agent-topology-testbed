"""Retrospective V1: isolated registry installs and fresh-process public calls.

Initial --resolve writes locks; normal reproduction only consumes those locks.
Output and environment directories must be new to prevent stale evidence reuse.
"""
import argparse
import base64
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

HERE = Path(__file__).resolve().parent
INPUTS = HERE.parents[1] / "observations/V1"
VERSIONS = {"py-b1": "0.1.0b1", "py-b2": "0.1.0b2", "js-b1": "0.1.0-beta.1", "js-b2": "0.1.0-beta.2"}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resolve", action="store_true")
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    require(not envs.exists() and not out.exists(), "use new environment and output directories")
    envs.mkdir(parents=True)
    out.mkdir(parents=True)
    manifest = json.loads((INPUTS / "inputs.json").read_text())
    for name, item in manifest["inputs"].items():
        require(digest((INPUTS / "inputs" / name).read_bytes()) == item["sha256"], f"input changed: {name}")
    save(out / "inputs-before-install.json", manifest)
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
        lockdir = HERE / "locks" / label
        lockdir.mkdir(exist_ok=True)
        if label.startswith("py"):
            run([sys.executable, "-m", "venv", target])
            python = target / "bin/python"
            install = [python, "-I", "-m", "pip", "--isolated", "install", "--index-url", "https://pypi.org/simple", "--only-binary=:all:", "--report", out / f"{label}-install.json"]
            if args.resolve:
                install += [f"agent-topology-spec=={version}"]
            else:
                install += ["--require-hashes", "-r", lockdir / "requirements.lock"]
            run(install)
            report = json.loads((out / f"{label}-install.json").read_text())
            if args.resolve:
                (lockdir / "requirements.lock").write_text("".join(
                    f'{p["metadata"]["name"]}=={p["metadata"]["version"]} --hash=sha256:{p["download_info"]["archive_info"]["hashes"]["sha256"]}\n'
                    for p in sorted(report["install"], key=lambda p: p["metadata"]["name"])))
            run([python, "-I", "-m", "pip", "freeze", "--all"])
            for p in report["install"]:
                info = p["download_info"]
                raw = urllib.request.urlopen(info["url"]).read()
                sha = digest(raw)
                require(sha == info["archive_info"]["hashes"]["sha256"], "Python artifact digest mismatch")
                artifacts.append({"installation": label, "package": p["metadata"]["name"], "version": p["metadata"]["version"], "url": info["url"], "sha256": sha})
            command = [python, "-I", HERE / "adapter.py"]
        else:
            target.mkdir()
            if args.resolve:
                save(target / "package.json", {"private": True, "type": "module", "dependencies": {"@agent-topology/spec": version}})
                run(["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund", "--registry=https://registry.npmjs.org"], target)
                for name in ("package.json", "package-lock.json"):
                    shutil.copyfile(target / name, lockdir / name)
            else:
                for name in ("package.json", "package-lock.json"):
                    shutil.copyfile(lockdir / name, target / name)
                run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund", "--registry=https://registry.npmjs.org"], target)
            run(["npm", "ls", "--all", "--json"], target)
            lock = json.loads((target / "package-lock.json").read_text())
            for name, p in lock["packages"].items():
                if not name:
                    continue
                raw = urllib.request.urlopen(p["resolved"]).read()
                algorithm, expected = p["integrity"].split("-", 1)
                require(base64.b64encode(hashlib.new(algorithm, raw).digest()).decode() == expected, "npm integrity mismatch")
                artifacts.append({"installation": label, "package": name, "version": p["version"], "url": p["resolved"], "integrity": p["integrity"], "sha256": digest(raw)})
            shutil.copyfile(HERE / "adapter.mjs", target / "adapter.mjs")
            command = ["node", target / "adapter.mjs"]
        save(out / "artifacts.json", artifacts)
        for name in manifest["inputs"]:
            for repeat in (1, 2):
                p = run(command, target, (INPUTS / "inputs" / name).read_bytes(), allowed=(0, 2))
                record = json.loads(p.stdout)
                require(record["identity"]["version"] == version, f"wrong package version: {label}")
                require(str(target) + "/" in record["identity"]["imported_path"], f"import escaped installation: {label}")
                require(record["input_sha256"] == manifest["inputs"][name]["sha256"], "adapter input mismatch")
                require(p.returncode == (0 if record["status"] == "accepted" else 2), "adapter exit/status mismatch")
                identities[label] = record["identity"]
                save(out / f'{label}-{Path(name).stem}-{repeat}.json', record)
    save(out / "identities.json", identities)
    save(out / "provenance.json", {"finished_at": datetime.now(timezone.utc).isoformat(),
         "evidence_class": "callable; retrospective installed-package evaluation, no framework execution",
         "sources_sha256": {p.name: digest(p.read_bytes()) for p in (HERE / "run.py", HERE / "adapter.py", HERE / "adapter.mjs", HERE / "compare.py")},
         "locks_sha256": {str(p.relative_to(HERE)): digest(p.read_bytes()) for p in sorted((HERE / "locks").rglob("*")) if p.is_file()},
         "commands_seconds": sum(c["seconds"] for c in commands)})
    run([sys.executable, "-O", HERE / "compare.py", out])
    print(f"PASS V1: four isolated installs, 72 fresh-process calls; {out}")


if __name__ == "__main__":
    main()
