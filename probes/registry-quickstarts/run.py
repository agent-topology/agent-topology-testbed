#!/usr/bin/env python3
"""Execute frozen Q1 documentation in a new directory, preserving raw evidence."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
INPUT = HERE.parents[1] / "observations/Q1"


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    require(not envs.exists() and not out.exists(), "use two new directories")
    require(not envs.is_relative_to(HERE.parents[1]), "environments must be outside checkout")
    inputs = json.loads((INPUT / "inputs.json").read_text())
    refs = json.loads((INPUT / "source-references.json").read_text())
    for item in refs["files"]:
        require(digest(INPUT / "source" / item["path"]) == item["sha256"], "source drift")
    for item in inputs["blocks"]:
        require(digest(INPUT / item["path"]) == item["sha256"], "snippet drift")
    envs.mkdir(parents=True)
    out.mkdir(parents=True)
    save(out / "inputs-before-install.json", inputs)
    home = envs / "home"
    home.mkdir()
    bootstrap = envs / "bin"
    bootstrap.mkdir()
    (bootstrap / "python").symlink_to(sys.executable)
    node = Path(shutil.which("node")).resolve()
    npm = Path(shutil.which("npm")).absolute()
    env = {
        "HOME": str(home), "PATH": os.pathsep.join(dict.fromkeys(
            [str(bootstrap), str(node.parent), str(npm.parent), "/usr/bin", "/bin"])),
        "LANG": "C.UTF-8", "PYTHONNOUSERSITE": "1",
        "PIP_CONFIG_FILE": os.devnull, "PIP_INDEX_URL": "https://pypi.org/simple",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_ONLY_BINARY": ":all:",
        "npm_config_registry": "https://registry.npmjs.org",
        "npm_config_userconfig": str(home / ".npmrc"),
        "npm_config_globalconfig": str(home / "global-npmrc"),
        "npm_config_cache": str(home / "npm-cache"),
        "npm_config_audit": "false", "npm_config_fund": "false",
        "npm_config_update_notifier": "false", "npm_config_ignore_scripts": "true",
    }
    save(out / "environment.json", env)
    commands = []

    def run(argv, cwd, label, extra=None):
        start = time.monotonic()
        p = subprocess.run([str(x) for x in argv], cwd=cwd,
                           env=env | (extra or {}), capture_output=True, text=True)
        commands.append(dict(label=label, command=[str(x) for x in argv], cwd=str(cwd),
                             exit=p.returncode, stdout=p.stdout, stderr=p.stderr,
                             seconds=time.monotonic()-start,
                             completedAt=datetime.now(timezone.utc).isoformat()))
        save(out / "commands.json", commands)
        require(p.returncode == 0, f"{label} failed; raw failure saved in {out}/commands.json")
        return p.stdout

    def block(name):
        item = next(x for x in inputs["blocks"] if x["id"] == name)
        return (INPUT / item["path"]).read_text()

    def shell(source, cwd, label, python=False, extra=None):
        prefix = "source .venv/bin/activate\n" if python else ""
        return run(["/bin/bash", "--noprofile", "--norc", "-exc",
                    prefix + source], cwd, label, extra)

    def capture(cwd, label):
        shutil.copyfile(cwd / "topology.json", out / f"{label}.json")

    py, js = envs / "python", envs / "typescript"
    py.mkdir()
    js.mkdir()
    run(["python", "--version"], py, "python-runtime")
    run(["node", "--version"], js, "node-runtime")
    run(["npm", "--version"], js, "npm-runtime")
    shell(block("python-1"), py, "python-install",
          extra={"PIP_REPORT": str(out / "pip-report.json")})
    (py / "graph.py").write_text(block("python-2"))
    shell(block("python-3"), py, "python-export-inspect", python=True)
    capture(py, "python-cli")
    shell("python graph.py > topology.json\n", py, "python-inline-api", python=True)
    capture(py, "python-api")
    shell(block("python-4"), py, "python-strict", python=True)
    capture(py, "python-strict")
    for name in ("graph.py",):
        shutil.copyfile(py / name, out / name)
    shutil.copyfile(HERE / "audit.py", py / "audit.py")
    audit = run([py / ".venv/bin/python", "-I", py / "audit.py",
                 out / "python-cli.json", out / "python-api.json", out / "python-strict.json"],
                py, "python-audit")
    (out / "python-audit.json").write_text(audit)
    run([py / ".venv/bin/python", "-I", "-m", "pip", "freeze", "--all"], py, "python-freeze")
    run([py / ".venv/bin/python", "-I", "-m", "pip", "check"], py, "python-dependencies")

    shell(block("typescript-1"), js, "typescript-install")
    for file, source, command, label in [
        ("graph.mjs", "typescript-2", "typescript-3", "typescript-esm"),
        ("graph.cjs", "typescript-4", "typescript-5", "typescript-commonjs"),
    ]:
        (js / file).write_text(block(source))
        shell(block(command), js, label)
        capture(js, label)
        shutil.copyfile(js / file, out / file)
    # The final block is retained as classified before setup; no invented compiler command.
    (out / "node-count.ts").write_text(block("typescript-6"))
    shutil.copyfile(HERE / "audit.mjs", js / "audit.mjs")
    audit = run(["node", js / "audit.mjs", out / "typescript-esm.json",
                 out / "typescript-commonjs.json"], js, "typescript-audit")
    (out / "typescript-audit.json").write_text(audit)
    run(["npm", "ls", "--all", "--json"], js, "typescript-dependencies")
    for name in ("package.json", "package-lock.json"):
        shutil.copyfile(js / name, out / name)

    report = json.loads((out / "pip-report.json").read_text())
    artifacts, requirements = [], []
    for item in report["install"]:
        info = item["download_info"]
        require(not item.get("is_direct") and "dir_info" not in info, "non-registry Python install")
        require(info["url"].startswith("https://files.pythonhosted.org/"), "non-PyPI artifact")
        sha = info["archive_info"]["hashes"]["sha256"]
        raw = urlopen(info["url"]).read()
        require(hashlib.sha256(raw).hexdigest() == sha, "wheel identity mismatch")
        artifacts.append(dict(ecosystem="python", name=item["metadata"]["name"],
                              version=item["metadata"]["version"], url=info["url"], sha256=sha))
        requirements.append(f'{item["metadata"]["name"]}=={item["metadata"]["version"]} --hash=sha256:{sha}')
    (out / "requirements.lock").write_text("\n".join(sorted(requirements)) + "\n")
    lock = json.loads((out / "package-lock.json").read_text())
    for name, item in lock["packages"].items():
        if not name:
            continue
        require(not item.get("link"), "local npm link")
        require(item["resolved"].startswith("https://registry.npmjs.org/"), "non-registry npm artifact")
        require((js / name).resolve().is_relative_to(js / "node_modules"), "npm path escape")
        raw = urlopen(item["resolved"]).read()
        algorithm, expected = item["integrity"].split("-", 1)
        require(base64.b64encode(hashlib.new(algorithm, raw).digest()).decode() == expected,
                "npm artifact identity mismatch")
        artifacts.append(dict(ecosystem="npm", name=name, version=item["version"],
                              url=item["resolved"], integrity=item["integrity"],
                              sha256=hashlib.sha256(raw).hexdigest()))
    save(out / "artifacts.json", artifacts)
    save(out / "provenance.json", {
        "documentationCommit": refs["commit"], "platform": platform.platform(),
        "runtime": sys.version, "envs": str(envs),
        "completedAt": datetime.now(timezone.utc).isoformat(),
        "commandSeconds": sum(c["seconds"] for c in commands),
        "sources": {p.name: digest(p) for p in sorted(HERE.glob("*")) if p.is_file()},
        "inputsSha256": digest(INPUT / "inputs.json"),
        "locks": {name: digest(out / name) for name in ("requirements.lock", "package-lock.json")},
    })
    print(f"PASS: complete executable quickstarts; evidence at {out}")


if __name__ == "__main__":
    main()
