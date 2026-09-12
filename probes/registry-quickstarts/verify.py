#!/usr/bin/env python3
"""Audit saved Q1 receipts and compare full documents except generatedAt."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
INPUT = HERE.parents[1] / "observations/Q1"
FILES = ("python-cli", "python-api", "python-strict", "typescript-esm", "typescript-commonjs")
LABELS = ["python-runtime", "node-runtime", "npm-runtime", "python-install",
          "python-export-inspect", "python-inline-api", "python-strict", "python-audit",
          "python-freeze", "python-dependencies", "typescript-install", "typescript-esm",
          "typescript-commonjs", "typescript-audit", "typescript-dependencies"]


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic(document):
    result = deepcopy(document)
    del result["provenance"]["generatedAt"]
    return result


def check_document(doc):
    expected = read(INPUT / "inputs.json")["expected"]
    require(doc["topologyVersion"] == "0.1", "topology version")
    require(len(doc["graphs"]) == 1, "graph count")
    graph = doc["graphs"][0]
    require(graph["id"] == expected["graphId"], "graph ID")
    structure = graph["structure"]
    require(sorted(n["id"] for n in structure["nodes"]) == expected["nodes"], "node identities")
    require(sorted([e["source"], e["target"]] for e in structure["edges"]) ==
            expected["edges"], "edge endpoints or multiplicity")
    require(all(e["kind"] == "direct" for e in structure["edges"]), "edge kinds")
    for field in ("joins", "entryNodeIds", "exitNodeIds"):
        require(structure[field] == expected[field], field)
    require(doc["completeness"] == expected["completeness"], "completeness")
    require([x["code"] for x in doc["producerLimitations"]] == [expected["limitation"]],
            "producer limitations")
    require(doc["structureHash"]["algorithm"] == "sha256" and
            doc["structureHash"]["algorithmVersion"] == "1" and
            re.fullmatch("[0-9a-f]{64}", doc["structureHash"]["value"]), "hash tuple")


def verify_run(out):
    inputs = read(INPUT / "inputs.json")
    refs = read(INPUT / "source-references.json")
    require(refs["commit"] == inputs["documentationCommit"], "source commit")
    for item in refs["files"]:
        require(sha(INPUT / "source" / item["path"]) == item["sha256"], "source snapshot drift")
    require(read(out / "inputs-before-install.json") == inputs, "pre-install inventory")
    for language in ("python", "typescript"):
        source = (INPUT / f"source/docs/getting-started/{language}.md").read_text()
        blocks = re.findall(r"```\w+\n(.*?)\n```", source, re.S)
        inventory = [x for x in inputs["blocks"] if x["id"].startswith(language + "-")]
        require(len(blocks) == len(inventory), "complete block coverage")
        for block, item in zip(blocks, inventory):
            require((INPUT / item["path"]).read_text() == block + "\n", "modified snippet")
            require(sha(INPUT / item["path"]) == item["sha256"], "block hash")
    provenance = read(out / "provenance.json")
    require(provenance["documentationCommit"] == inputs["documentationCommit"], "doc commit")
    require(provenance["inputsSha256"] == sha(INPUT / "inputs.json"), "input manifest drift")
    for name, digest in provenance["sources"].items():
        require(sha(HERE / name) == digest, f"runner source drift: {name}")
    for name, digest in provenance["locks"].items():
        require(sha(out / name) == digest, "lock drift")
    commands = read(out / "commands.json")
    require([c["label"] for c in commands] == LABELS, "missing/reordered command")
    require(all(c["exit"] == 0 for c in commands), "failed command")
    receipts = {c["label"]: c for c in commands}
    for label, block_id, activate in [
        ("python-install", "python-1", False),
        ("python-export-inspect", "python-3", True),
        ("python-strict", "python-4", True),
        ("typescript-install", "typescript-1", False),
        ("typescript-esm", "typescript-3", False),
        ("typescript-commonjs", "typescript-5", False),
    ]:
        item = next(x for x in inputs["blocks"] if x["id"] == block_id)
        prefix = "source .venv/bin/activate\n" if activate else ""
        require(receipts[label]["command"] == ["/bin/bash", "--noprofile", "--norc", "-exc",
                prefix + (INPUT / item["path"]).read_text()], "changed execution block")
    for filename, block_id in [("graph.py", "python-2"), ("graph.mjs", "typescript-2"),
                               ("graph.cjs", "typescript-4"), ("node-count.ts", "typescript-6")]:
        item = next(x for x in inputs["blocks"] if x["id"] == block_id)
        require(sha(out / filename) == item["sha256"], "executed source differs")
    env = read(out / "environment.json")
    require(not any(k in env for k in ("PYTHONPATH", "PYTHONHOME", "NODE_PATH", "NODE_OPTIONS",
                                      "VIRTUAL_ENV")), "ambient path leak")
    require(env["PYTHONNOUSERSITE"] == "1", "user site enabled")
    require(env["PIP_INDEX_URL"] == "https://pypi.org/simple" and
            env["npm_config_registry"] == "https://registry.npmjs.org", "registry drift")
    require(not Path(provenance["envs"]).is_relative_to(HERE.parents[1]), "environment in repository")
    docs = {}
    for filename in FILES:
        doc = read(out / f"{filename}.json")
        check_document(doc)
        docs[filename] = semantic(doc)
    for language, expected_names in [("python", FILES[:3]), ("typescript", FILES[3:])]:
        audit = read(out / f"{language}-audit.json")
        require(json.loads(receipts[f"{language}-audit"]["stdout"]) == audit, "audit receipt")
        require([c["file"] for c in audit["checks"]] ==
                [name + ".json" for name in expected_names], "audit coverage")
        for check, name in zip(audit["checks"], expected_names):
            require(check["valid"] and check["canonical"] and
                    check["hash"] == docs[name]["structureHash"], "API oracle failed")
        prefix = str(Path(provenance["envs"]) / language /
                     (".venv" if language == "python" else "node_modules")) + "/"
        require(all(p.startswith(prefix) for p in audit["imports"].values()), "import escape")
        require(all(docs[name] == docs[expected_names[0]] for name in expected_names),
                "semantic drift across entry points")
    report = read(out / "pip-report.json")
    artifacts = read(out / "artifacts.json")
    py_artifacts = [a for a in artifacts if a["ecosystem"] == "python"]
    require(len(py_artifacts) == len(report["install"]), "Python artifact coverage")
    for item in report["install"]:
        info = item["download_info"]
        require(not item.get("is_direct") and "dir_info" not in info, "direct install")
        require(any(a["name"] == item["metadata"]["name"] and
                    a["version"] == item["metadata"]["version"] and
                    a["sha256"] == info["archive_info"]["hashes"]["sha256"] and
                    a["url"] == info["url"] for a in py_artifacts), "Python identity receipt")
    lock = read(out / "package-lock.json")
    js_artifacts = [a for a in artifacts if a["ecosystem"] == "npm"]
    require(len(js_artifacts) == len(lock["packages"]) - 1, "npm artifact coverage")
    for name, item in lock["packages"].items():
        if name:
            require(not item.get("link") and any(a["name"] == name and
                    a["version"] == item["version"] and a["url"] == item["resolved"] and
                    a["integrity"] == item["integrity"] for a in js_artifacts), "npm identity receipt")
    require(all(a["url"].startswith("https://files.pythonhosted.org/" if
                a["ecosystem"] == "python" else "https://registry.npmjs.org/") for a in artifacts),
            "non-registry artifact")
    return docs, artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    require(args.first.resolve() != args.second.resolve(), "need two runs")
    first, second = (verify_run(p) for p in (args.first, args.second))
    require(read(args.first / "provenance.json")["envs"] !=
            read(args.second / "provenance.json")["envs"], "reused environment")
    require(first == second, "semantic documents or artifact identities changed")
    result = {"status": "pass", "runs": 2, "documents": 10,
              "comparison": "full documents; only provenance.generatedAt removed",
              "artifactIdentitiesEqual": True,
              "entryPoints": list(FILES), "illustrativeBlock": "typescript-6 (not executed)"}
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
