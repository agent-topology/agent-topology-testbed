"""Install beta.3 registry artifacts into fresh, isolated environments."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def clean_environment(home, bootstrap):
    return {
        "HOME": str(home),
        "PATH": os.pathsep.join([str(bootstrap), "/usr/local/bin", "/usr/bin", "/bin"]),
        "LANG": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PIP_CONFIG_FILE": os.devnull,
        "PIP_INDEX_URL": "https://pypi.org/simple",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "npm_config_registry": "https://registry.npmjs.org",
        "npm_config_userconfig": str(home / ".npmrc"),
        "npm_config_globalconfig": str(home / "global-npmrc"),
        "npm_config_cache": str(home / "npm-cache"),
        "npm_config_audit": "false",
        "npm_config_fund": "false",
        "npm_config_update_notifier": "false",
        "npm_config_ignore_scripts": "true",
    }


def command(args, cwd, out, records, env):
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    result = subprocess.run(list(map(str, args)), cwd=cwd, env=env,
                            capture_output=True, text=True, timeout=240)
    records.append({"command": list(map(str, args)), "cwd": str(cwd),
                    "startedAt": started, "seconds": time.monotonic() - clock,
                    "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    save(out / "commands.json", records)
    if result.returncode:
        raise RuntimeError(f"command failed; see {out / 'commands.json'}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--envs", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--resolve", action="store_true")
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    if envs.exists() or out.exists():
        raise ValueError("use fresh environment and evidence directories")
    if envs.is_relative_to(REPO):
        raise ValueError("environments must be outside the checkout")
    envs.mkdir(parents=True); out.mkdir(parents=True)
    home = envs / "home"; home.mkdir()
    bootstrap = envs / "bin"; bootstrap.mkdir()
    Path(bootstrap / "python3.11").symlink_to(Path(sys.executable).resolve())
    node = Path(subprocess.check_output(["which", "node"], text=True).strip()).resolve()
    npm = Path(subprocess.check_output(["which", "npm"], text=True).strip()).resolve()
    Path(bootstrap / "node").symlink_to(node)
    Path(bootstrap / "npm").symlink_to(npm)
    env = clean_environment(home, bootstrap)
    save(out / "environment.json", env)
    records = []
    run = lambda command_, cwd=envs: command(command_, cwd, out, records, env)
    py, js = envs / "python", envs / "typescript"
    run(["python3.11", "-m", "venv", py]); js.mkdir()
    pip = [py / "bin/python", "-I", "-m", "pip", "install", "--only-binary=:all:",
           "--report", out / "pip-report.json"]
    if args.resolve:
        run(pip + ["agent-topology-langgraph==0.1.0b3", "agent-topology-spec==0.1.0b3", "langgraph==1.2.11"])
        save(js / "package.json", {"private": True, "type": "module", "dependencies": {
            "@agent-topology/langgraph": "0.1.0-beta.3",
            "@agent-topology/spec": "0.1.0-beta.3",
            "@langchain/langgraph": "1.4.14"}})
        run(["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund"], js)
    else:
        run(pip + ["--require-hashes", "-r", ROOT / "locks/requirements.txt"])
        for name in ("package.json", "package-lock.json"):
            (js / name).write_bytes((ROOT / "locks" / name).read_bytes())
        run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], js)
    report = json.loads((out / "pip-report.json").read_text())
    lock = json.loads((js / "package-lock.json").read_text())
    artifacts, requirements = [], []
    for item in report["install"]:
        info = item["download_info"]
        if item.get("is_direct") or "dir_info" in info:
            raise ValueError("direct/editable Python installation")
        sha = info["archive_info"]["hashes"]["sha256"]
        data = urllib.request.urlopen(info["url"]).read()
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError("wheel digest mismatch")
        artifacts.append({"ecosystem": "python", "name": item["metadata"]["name"],
                          "version": item["metadata"]["version"], "url": info["url"], "sha256": sha})
        requirements.append(f'{item["metadata"]["name"]}=={item["metadata"]["version"]} --hash=sha256:{sha}')
    for name, item in lock["packages"].items():
        if not name:
            continue
        if item.get("link") or not item.get("resolved", "").startswith("https://registry.npmjs.org/"):
            raise ValueError("linked/non-registry npm installation")
        data = urllib.request.urlopen(item["resolved"]).read()
        algorithm, expected = item["integrity"].split("-", 1)
        if base64.b64encode(hashlib.new(algorithm, data).digest()).decode() != expected:
            raise ValueError("npm integrity mismatch")
        artifacts.append({"ecosystem": "npm", "name": name, "version": item["version"],
                          "url": item["resolved"], "integrity": item["integrity"],
                          "sha256": hashlib.sha256(data).hexdigest()})
    save(out / "artifacts.json", artifacts)
    run([py / "bin/python", "-I", "-m", "pip", "freeze", "--all"])
    run(["node", "--version"]); run(["npm", "--version"])
    if args.resolve:
        (ROOT / "locks").mkdir(exist_ok=True)
        (ROOT / "locks/requirements.txt").write_text("\n".join(sorted(requirements)) + "\n")
        for name in ("package.json", "package-lock.json"):
            (ROOT / "locks" / name).write_bytes((js / name).read_bytes())
    save(out / "provenance.json", {
        "completedAt": datetime.now(timezone.utc).isoformat(), "runtime": sys.version,
        "sourceSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "locks": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "locks").iterdir()}})


if __name__ == "__main__":
    main()
