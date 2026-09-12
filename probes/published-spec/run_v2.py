"""V2: compare isolated published beta.2 and beta.3 spec packages.

Initial --resolve-b3 writes only beta.3 locks. Normal reproduction consumes all
four locks. Output and environment directories must be new.
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
ROOT = HERE.parents[1]
INPUTS = ROOT / "observations/V1"
OBSERVATION = ROOT / "observations/V2"
EXPECTATIONS = OBSERVATION / "expectations.json"
VERSIONS = {
    "py-b2": "0.1.0b2",
    "py-b3": "0.1.0b3",
    "js-b2": "0.1.0-beta.2",
    "js-b3": "0.1.0-beta.3",
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_inputs():
    manifest = json.loads((INPUTS / "inputs.json").read_text())
    expectations = json.loads(EXPECTATIONS.read_text())
    require(expectations["input_manifest"] == "observations/V1/inputs.json", "wrong V2 input manifest")
    require(set(expectations["inputs"]) == set(manifest["inputs"]), "V2 expectation inventory mismatch")
    for name, item in manifest["inputs"].items():
        raw = (INPUTS / "inputs" / name).read_bytes()
        expected = expectations["inputs"][name]
        require(digest(raw) == item["sha256"] == expected["sha256"], f"input changed: {name}")
        require(expected["expected_structure_hash_tuple"] == "equal", f"unexpected hash expectation: {name}")
        require(expected["expected_full_canonical_bytes"] in {"equal", "different"}, f"invalid canonical expectation: {name}")
    return manifest, expectations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resolve-b3", action="store_true", help="Resolve and write only py-b3/js-b3 locks")
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    require(not envs.exists() and not out.exists(), "use new environment and output directories")
    manifest, expectations = checked_inputs()
    envs.mkdir(parents=True)
    out.mkdir(parents=True)
    save(out / "inputs-before-install.json", {"manifest": manifest, "expectations": expectations})
    clean_env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME", "NODE_PATH", "NODE_OPTIONS"}}
    commands = []

    def run(command, cwd=envs, raw=None, allowed=(0,)):
        started = datetime.now(timezone.utc).isoformat()
        before = time.monotonic()
        process = subprocess.run([str(x) for x in command], cwd=cwd, env=clean_env, input=raw, capture_output=True)
        commands.append({"command": [str(x) for x in command], "cwd": str(cwd), "started_at": started,
                         "seconds": time.monotonic() - before, "exit": process.returncode,
                         "stdout": process.stdout.decode(), "stderr": process.stderr.decode()})
        save(out / "commands.json", commands)
        require(process.returncode in allowed, f"command failed: {command}; see {out}/commands.json")
        return process

    artifacts = []
    identities = {}
    for label, version in VERSIONS.items():
        target = envs / label
        lockdir = HERE / "locks" / label
        resolve = args.resolve_b3 and label.endswith("b3")
        require(lockdir.exists() or resolve, f"missing lock: {lockdir}")
        if resolve:
            lockdir.mkdir()
        if label.startswith("py"):
            run([sys.executable, "-m", "venv", target])
            python = target / "bin/python"
            install = [python, "-I", "-m", "pip", "--isolated", "install", "--index-url", "https://pypi.org/simple",
                       "--only-binary=:all:", "--report", out / f"{label}-install.json"]
            install += [f"agent-topology-spec=={version}"] if resolve else ["--require-hashes", "-r", lockdir / "requirements.lock"]
            run(install)
            report = json.loads((out / f"{label}-install.json").read_text())
            if resolve:
                (lockdir / "requirements.lock").write_text("".join(
                    f'{item["metadata"]["name"]}=={item["metadata"]["version"]} --hash=sha256:{item["download_info"]["archive_info"]["hashes"]["sha256"]}\n'
                    for item in sorted(report["install"], key=lambda item: item["metadata"]["name"])))
            run([python, "-I", "-m", "pip", "freeze", "--all"])
            for item in report["install"]:
                info = item["download_info"]
                raw = urllib.request.urlopen(info["url"]).read()
                sha = digest(raw)
                require(sha == info["archive_info"]["hashes"]["sha256"], "Python artifact digest mismatch")
                artifacts.append({"installation": label, "package": item["metadata"]["name"], "version": item["metadata"]["version"],
                                  "url": info["url"], "sha256": sha})
            command = [python, "-I", HERE / "adapter.py"]
        else:
            target.mkdir()
            if resolve:
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
            for name, item in lock["packages"].items():
                if not name:
                    continue
                raw = urllib.request.urlopen(item["resolved"]).read()
                algorithm, expected = item["integrity"].split("-", 1)
                require(base64.b64encode(hashlib.new(algorithm, raw).digest()).decode() == expected, "npm integrity mismatch")
                artifacts.append({"installation": label, "package": name, "version": item["version"], "url": item["resolved"],
                                  "integrity": item["integrity"], "sha256": digest(raw)})
            shutil.copyfile(HERE / "adapter.mjs", target / "adapter.mjs")
            command = ["node", target / "adapter.mjs"]
        save(out / "artifacts.json", artifacts)
        for name in manifest["inputs"]:
            for repeat in (1, 2):
                process = run(command, target, (INPUTS / "inputs" / name).read_bytes(), allowed=(0, 2))
                record = json.loads(process.stdout)
                require(record["identity"]["version"] == version, f"wrong package version: {label}")
                require(str(target) + "/" in record["identity"]["imported_path"], f"import escaped installation: {label}")
                require(record["input_sha256"] == manifest["inputs"][name]["sha256"], "adapter input mismatch")
                require(process.returncode == (0 if record["status"] == "accepted" else 2), "adapter exit/status mismatch")
                identities[label] = record["identity"]
                save(out / f'{label}-{Path(name).stem}-{repeat}.json', record)
    save(out / "identities.json", identities)
    save(out / "provenance.json", {"finished_at": datetime.now(timezone.utc).isoformat(),
         "evidence_class": "callable; installed-package evaluation, no framework execution",
         "sources_sha256": {path.name: digest(path.read_bytes()) for path in (HERE / "run_v2.py", HERE / "adapter.py", HERE / "adapter.mjs", HERE / "compare_v2.py")},
         "locks_sha256": {str(path.relative_to(HERE)): digest(path.read_bytes()) for path in sorted((HERE / "locks").rglob("*")) if path.is_file()},
         "commands_seconds": sum(command["seconds"] for command in commands)})
    run([sys.executable, "-O", HERE / "compare_v2.py", out])
    print(f"PASS V2: four isolated installs, 72 fresh-process calls; {out}")


if __name__ == "__main__":
    main()
