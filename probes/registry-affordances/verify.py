"""Audit X1 records against literal expectations without importing frameworks."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_VERSIONS = {
    "python": {"agent-topology-langgraph": "0.1.0b3", "agent-topology-spec": "0.1.0b3", "langgraph": "1.2.11"},
    "typescript": {"@agent-topology/langgraph": "0.1.0-beta.3", "@agent-topology/spec": "0.1.0-beta.3", "@langchain/langgraph": "1.4.14"},
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def strip_source(value):
    value = copy.deepcopy(value)
    if isinstance(value, dict):
        value.pop("source", None) if set(value) >= {"kind", "source"} else None
        return {key: strip_source(child) for key, child in value.items()}
    if isinstance(value, list):
        return [strip_source(child) for child in value]
    return value


def normalized(record):
    document = record["document"]
    graph = document["graphs"][0]
    return {"graphId": graph["id"], "structure": graph["structure"],
            "completeness": document["completeness"], "structureHash": document["structureHash"],
            "interpretation": strip_source(graph["x-topology-interpretation"]),
            "derivedJoinEdges": record["derivedJoinEdges"]}


def fact(graph, node_id, key):
    record = next(item for item in graph["x-topology-interpretation"]["nodes"] if item["nodeId"] == node_id)
    return strip_source(record[key])


def check_case(record, expected):
    if record["inputSha256"] != hashlib.sha256(record["case"].encode()).hexdigest():
        raise ValueError("input digest")
    document = record["document"]
    if record["computedHash"] != document["structureHash"]:
        raise ValueError("computed/recorded hash")
    if document["topologyVersion"] != "0.1" or document["structureHash"]["algorithmVersion"] != "1":
        raise ValueError("contract/hash version")
    if len(document["graphs"]) != 1:
        raise ValueError("graph count")
    graph = document["graphs"][0]; structure = graph["structure"]
    if graph["id"] != expected["graphId"]:
        raise ValueError("graph id")
    if sorted(node["id"] for node in structure["nodes"]) != expected["nodes"]:
        raise ValueError("nodes")
    edges = sorted([edge["source"], edge["target"], edge["kind"]] for edge in structure["edges"])
    if edges != sorted(expected["edges"]):
        raise ValueError("edges")
    joins = sorted([join["id"], sorted(join["sources"]), join["target"]] for join in structure["joins"])
    if joins != sorted(expected["joins"]):
        raise ValueError("joins")
    if structure["entryNodeIds"] != expected["entryNodeIds"] or structure["exitNodeIds"] != expected["exitNodeIds"]:
        raise ValueError("entry/exit arrays")
    gaps = [{"code": gap["code"], "element": gap["element"]} for gap in document["completeness"]["gaps"]]
    if gaps != expected["gaps"]:
        raise ValueError("gaps")
    if (document["completeness"]["status"] == "complete") != (not expected["gaps"]):
        raise ValueError("completeness status")
    if record["derivedJoinEdges"] != expected.get("derivedJoinEdges", []):
        raise ValueError("derived join edges")
    for node_id, key, value in ([expected["fact"]] if "fact" in expected else expected.get("facts", [])):
        if fact(graph, node_id, key) != value:
            raise ValueError(f"fact {node_id}/{key}")


def verify(out, expectations_path=None):
    expectations = json.loads((expectations_path or ROOT / "expectations.json").read_text())
    errors, pairs, captures = [], [], {}
    if json.loads((out / "inputs-before-extraction.json").read_text()) != json.loads((ROOT / "expectations.json").read_text()):
        errors.append("pre-extraction expectations drift")
    commands = json.loads((out / "commands.json").read_text())
    for language in ("python", "typescript"):
        for case, expected in expectations["cases"].items():
            for repeat in (1, 2):
                key = f"{language}-{case}-{repeat}"
                try:
                    raw = (out / f"{key}.json").read_text()
                    record = json.loads(raw); check_case(record, expected)
                    identity = record["identity"]
                    if identity["versions"] != EXPECTED_VERSIONS[language]:
                        raise ValueError("package versions")
                    matching = [command for command in commands if command["stdout"] == raw]
                    if len(matching) != 1 or matching[0]["exit"] != 0:
                        raise ValueError("command receipt")
                    for imported in identity["imports"].values():
                        prefix = identity.get("prefix") + "/" if language == "python" else "file://" + matching[0]["cwd"] + "/node_modules/"
                        if not imported.startswith(prefix):
                            raise ValueError("workspace/editable/linked import")
                    captures[key] = record
                except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                    errors.append(f"{key}: {exc}")
            first, second = (captures.get(f"{language}-{case}-{repeat}") for repeat in (1, 2))
            if first and second:
                equal = normalized(first) == normalized(second)
                distinct = first["identity"]["pid"] != second["identity"]["pid"]
                pairs.append({"language": language, "case": case, "kind": "fresh-process", "semanticEqual": equal, "distinctPid": distinct})
                if not equal or not distinct:
                    errors.append(f"{language}-{case}: repeat mismatch")
    for case in expectations["cases"]:
        py, js = captures.get(f"python-{case}-1"), captures.get(f"typescript-{case}-1")
        if py and js:
            equal = normalized(py) == normalized(js)
            pairs.append({"case": case, "kind": "cross-language", "semanticEqual": equal})
            if not equal:
                errors.append(f"{case}: cross-language mismatch")
    for case in ("opaque-child", "ordinary-node"):
        pass
    child, ordinary = captures.get("python-opaque-child-1"), captures.get("python-ordinary-node-1")
    if child and ordinary:
        same_core = child["document"]["graphs"][0]["structure"] == ordinary["document"]["graphs"][0]["structure"]
        same_hash = child["document"]["structureHash"] == ordinary["document"]["structureHash"]
        pairs.append({"kind": "F3-control", "sameCore": same_core, "sameHash": same_hash, "sameExtension": normalized(child)["interpretation"] == normalized(ordinary)["interpretation"]})
        if not same_core or not same_hash or normalized(child)["interpretation"] == normalized(ordinary)["interpretation"]:
            errors.append("F3 core/hash/extension distinction")
    for repeat in (1, 2):
        try:
            cli = json.loads((out / f"python-orphan-router-cli-{repeat}.json").read_text())
            api = captures[f"python-orphan-router-{repeat}"]["document"]
            shell = {"document": cli, "derivedJoinEdges": []}
            if normalized(shell) != normalized({"document": api, "derivedJoinEdges": []}):
                raise ValueError("API/CLI semantic mismatch")
            failure = json.loads((out / f"commonjs-require-{repeat}.json").read_text())
            if failure["exit"] == 0 or expectations["commonjs"]["errorCode"] not in failure["stderr"]:
                raise ValueError("CommonJS failure boundary")
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append(f"repeat-{repeat}: {exc}")
    return {"summary": {"captures": len(captures), "comparisons": len(pairs), "errors": len(errors),
                        "commonjsExpectedFailures": 2, "cliGraphIdChecks": 2},
            "errors": errors, "pairs": pairs,
            "residualUnknowns": expectations["residualUnknowns"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    report = verify(args.out.resolve(), args.expected)
    save(args.report, report)
    print(json.dumps(report["summary"]))
    if report["errors"]:
        raise SystemExit(1)
