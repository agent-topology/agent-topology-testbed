"""Install registry packages in fresh isolated environments, retaining receipts."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parent


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def command(args, cwd, out, records):
    start = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    result = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, text=True, timeout=240)
    records.append(dict(command=list(map(str, args)), cwd=str(cwd), startedAt=start,
                        seconds=time.monotonic()-clock, exit=result.returncode,
                        stdout=result.stdout, stderr=result.stderr))
    save(out / "commands.json", records)
    if result.returncode:
        raise RuntimeError(f"command failed; see {out / 'commands.json'}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--envs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resolve", action="store_true", help="Establish locks once; reproduction omits this")
    args = parser.parse_args()
    envs, out = args.envs.resolve(), args.out.resolve()
    if envs.exists() or out.exists():
        raise ValueError("use fresh environment and evidence directories")
    envs.mkdir(parents=True); out.mkdir(parents=True)
    records = []
    run = lambda cmd, cwd=envs: command(cmd, cwd, out, records)
    py, js = envs / "python", envs / "typescript"
    run([sys.executable, "-m", "venv", py]); js.mkdir()
    pip = [py / "bin/python", "-I", "-m", "pip", "install", "--only-binary=:all:",
           "--report", out / "pip-report.json"]
    if args.resolve:
        run(pip + ["agent-topology-langgraph==0.1.0b2", "agent-topology-spec==0.1.0b2", "langgraph==1.2.11"])
        save(js / "package.json", {"private": True, "type": "module", "dependencies": {
            "@agent-topology/langgraph": "0.1.0-beta.2", "@agent-topology/spec": "0.1.0-beta.2",
            "@langchain/langgraph": "1.4.14"}})
        run(["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund"], js)
    else:
        run(pip + ["--require-hashes", "-r", ROOT / "locks/requirements.txt"])
        for name in ("package.json", "package-lock.json"):
            (js / name).write_bytes((ROOT / "locks" / name).read_bytes())
        run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], js)
    report = json.loads((out / "pip-report.json").read_text())
    lock = json.loads((js / "package-lock.json").read_text())
    artifacts = []
    requirements = []
    for item in report["install"]:
        info = item["download_info"]
        sha = info["archive_info"]["hashes"]["sha256"]
        data = urllib.request.urlopen(info["url"]).read()
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError("wheel digest mismatch")
        artifacts.append(dict(ecosystem="python", name=item["metadata"]["name"],
                              version=item["metadata"]["version"], url=info["url"], sha256=sha))
        requirements.append(f'{item["metadata"]["name"]}=={item["metadata"]["version"]} --hash=sha256:{sha}')
    import base64
    for name, item in lock["packages"].items():
        if not name:
            continue
        data = urllib.request.urlopen(item["resolved"]).read()
        algorithm, expected = item["integrity"].split("-", 1)
        if base64.b64encode(hashlib.new(algorithm, data).digest()).decode() != expected:
            raise ValueError("npm integrity mismatch")
        artifacts.append(dict(ecosystem="npm", name=name, version=item["version"],
                              url=item["resolved"], integrity=item["integrity"],
                              sha256=hashlib.sha256(data).hexdigest()))
    save(out / "artifacts.json", artifacts)
    run([py / "bin/python", "-I", "-m", "pip", "freeze", "--all"])
    run(["node", "--version"]); run(["npm", "--version"])
    if args.resolve:
        (ROOT / "locks/requirements.txt").write_text("\n".join(sorted(requirements)) + "\n")
        for name in ("package.json", "package-lock.json"):
            (ROOT / "locks" / name).write_bytes((js / name).read_bytes())
    save(out / "provenance.json", {"completedAt": datetime.now(timezone.utc).isoformat(),
         "platform": sys.platform, "runtime": sys.version,
         "sourceSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "locks": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "locks").iterdir()}})


if __name__ == "__main__":
    main()
