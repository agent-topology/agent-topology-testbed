"""Audit saved D1 evidence without installing or executing frameworks."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from run import cases
from setup import save


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def core(value):
    if isinstance(value, dict):
        return {k: core(v) for k, v in value.items() if not k.startswith("x-")}
    if isinstance(value, list): return [core(v) for v in value]
    return value


def projection(document):
    # All non-extension structural properties remain visible; no identity/repr scrubbing.
    graphs = []
    for graph in document["graphs"]:
        structure = core(copy.deepcopy(graph["structure"]))
        for node in structure["nodes"]:
            if "interrupts" in node: node["interrupts"].sort()
        for join in structure["joins"]: join["sources"].sort()
        for key in ("nodes", "edges", "joins"): structure[key].sort(key=encode)
        for key in ("entryNodeIds", "exitNodeIds"): structure[key].sort()
        graphs.append({"id": graph["id"], "structure": structure})
    return {"graphs": sorted(graphs, key=encode)}


def differences(a, b, path=""):
    if type(a) is not type(b): return [path]
    if isinstance(a, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            child = f"{path}/{key}"
            result += [child] if key not in a or key not in b else differences(a[key], b[key], child)
        return result
    if isinstance(a, list):
        if len(a) != len(b): return [path]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differences(x, y, f"{path}/{i}")]
    return [] if a == b else [path]


def compare(a, b):
    pa, pb = projection(a), projection(b)
    structural = pa != pb
    hashed = a["structureHash"] != b["structureHash"]
    return {"structureEqual": not structural, "hashEqual": not hashed,
            "classification": ("extraction-drift" if structural else "hash-computation-drift" if hashed else "stable"),
            "structuralDifferences": differences(pa, pb), "rawDifferences": differences(a, b)}


def check_oracle(document, shape, variant):
    # Literal graph expectations independent of the builder and cases generator.
    nodes = ["__end__", "__start__", "a", "b"] + (["c"] if shape == "join" else [])
    edges = {"linear": [["__start__", "a"], ["a", "b"], ["b", "__end__"]],
             "fanout": [["__start__", "a"], ["__start__", "b"], ["a", "__end__"], ["b", "__end__"]],
             "join": [["__start__", "a"], ["__start__", "b"], ["c", "__end__"]]}[shape]
    joins = [[["a", "b"], "c"]] if shape == "join" else []
    if variant == "independent": joins = []; edges += [["a", "c"], ["b", "c"]]
    if variant == "edge-change": edges += [["a", "b" if shape == "fanout" else "__end__"]]
    if variant == "node-change":
        nodes = ["renamed" if n == "a" else n for n in nodes]
        edges = [["renamed" if n == "a" else n for n in edge] for edge in edges]
        joins = [[["b", "renamed"], "c"]] if shape == "join" else []
    graphs = document["graphs"]
    if len(graphs) != 1 or graphs[0]["id"] != "main": raise ValueError("graph identity")
    s = graphs[0]["structure"]
    if sorted(n["id"] for n in s["nodes"]) != sorted(nodes): raise ValueError("node identity/multiplicity")
    if sorted([e["source"], e["target"]] for e in s["edges"]) != sorted(edges): raise ValueError("edge connectivity/multiplicity")
    if sorted([sorted(j["sources"]), j["target"]] for j in s["joins"]) != sorted(joins): raise ValueError("join connectivity/multiplicity")
    if any(e["kind"] != "direct" for e in s["edges"]): raise ValueError("edge kind")
    for key in ("nodes", "edges", "joins"):
        if len({x["id"] for x in s[key]}) != len(s[key]): raise ValueError("duplicate identity")
    if s["entryNodeIds"] != ["__start__"] or s["exitNodeIds"] != ["__end__"]: raise ValueError("entry/exit")
    if document["completeness"] != {"status": "complete", "gaps": []}: raise ValueError("completeness")
    if document["topologyVersion"] != "0.1": raise ValueError("format")


def verify(out):
    expected = cases()
    saved = json.loads((out / "cases.json").read_text())
    errors, pairs, captures, identities = [], [], {}, {}
    if saved != expected: errors.append("case inventory/content differs")
    commands = json.loads((out / "commands.json").read_text())
    if len(commands) != len(expected)*4 or any(c["exit"] != 0 for c in commands): errors.append("missing/failed command")
    for language in ("python", "typescript"):
        extension = "py" if language == "python" else "mts"
        base_source = (out / "workers" / f"{language}-base.{extension}").read_text()
        comment_source = (out / "workers" / f"{language}-comment.{extension}").read_text()
        if comment_source != base_source.replace("D1_UNRELATED_COMMENT", "D1_UNRELATED_COMMENT changed without executable edits"):
            errors.append(f"{language}: source-comment transformation")
        for name, case in expected.items():
            for repeat in (1, 2):
                key = f"{language}-{name}-{repeat}"
                try:
                    raw = (out / f"{key}.json").read_text()
                    record = json.loads(raw)
                    input_path = out / "inputs" / f"{name}.json"
                    if record["inputSha256"] != hashlib.sha256(input_path.read_bytes()).hexdigest(): raise ValueError("input digest")
                    if json.loads(input_path.read_text()) != case["recipe"]: raise ValueError("input content")
                    matching = [c for c in commands if c["stdout"] == raw]
                    if len(matching) != 1: raise ValueError("command/output receipt")
                    identity = record["identity"]
                    identities[key] = identity
                    versions = ({"agent-topology-langgraph": "0.1.0b2", "agent-topology-spec": "0.1.0b2", "langgraph": "1.2.11"}
                                if language == "python" else {"@agent-topology/langgraph": "0.1.0-beta.2", "@agent-topology/spec": "0.1.0-beta.2", "@langchain/langgraph": "1.4.14"})
                    if identity["versions"] != versions: raise ValueError("package identity")
                    for path in identity["imports"].values():
                        if language == "python" and not path.startswith(identity["prefix"] + "/"): raise ValueError("nonisolated import")
                        if language == "typescript" and not path.startswith("file://" + matching[0]["cwd"] + "/node_modules/"): raise ValueError("nonisolated import")
                    docs = record["describes"]
                    if len(docs) != 2: raise ValueError("describe count")
                    for item in docs:
                        document = item["document"]
                        check_oracle(document, case["shape"], case["variant"])
                        oracle = {"algorithm": "sha256", "algorithmVersion": "1",
                                  "value": hashlib.sha256(encode(projection(document))).hexdigest()}
                        if item["computedHash"] != oracle or document["structureHash"] != oracle: raise ValueError("hash computation/oracle")
                        if json.loads(item["canonical"]) != document: raise ValueError("canonical/document mismatch")
                    captures[key] = docs[0]["document"]
                    pair = compare(docs[0]["document"], docs[1]["document"])
                    pairs.append(dict(language=language, case=name, repeat=repeat, kind="same-compiled", **pair))
                    if not pair["structureEqual"] or not pair["hashEqual"]: errors.append(key + ": repeat drift")
                except (OSError, ValueError, KeyError, TypeError) as exc: errors.append(f"{key}: {exc}")
            a, b = (captures.get(f"{language}-{name}-{i}") for i in (1, 2))
            if a is not None and b is not None:
                first, second = (identities[f"{language}-{name}-{i}"] for i in (1, 2))
                if first["pid"] == second["pid"] or first["runtime"] != second["runtime"]:
                    errors.append(f"{language}-{name}: process/runtime identity")
                pair = compare(a, b)
                pairs.append(dict(language=language, case=name, kind="fresh-process", **pair))
                if not pair["structureEqual"] or not pair["hashEqual"]: errors.append(f"{language}-{name}: process drift")
            if case["variant"] == "base": continue
            for repeat in (1, 2):
                base = captures.get(f'{language}-{case["shape"]}-base-{repeat}')
                changed = captures.get(f"{language}-{name}-{repeat}")
                if base is None or changed is None: continue
                pair = compare(base, changed)
                control = case["variant"] in ("node-change", "edge-change", "independent")
                if control and not pair["structureEqual"] and not pair["hashEqual"]: pair["classification"] = "expected-structural-change"
                pairs.append(dict(language=language, case=name, repeat=repeat, kind="transformation", positiveControl=control, **pair))
                if pair["structureEqual"] == control or pair["hashEqual"] == control: errors.append(f"{language}-{name}-{repeat}: transformation expectation")
    return {"summary": {"captures": len(captures), "describes": len(captures)*2,
                         "comparisons": len(pairs), "errors": len(errors)}, "errors": errors, "pairs": pairs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.out.resolve())
    save(args.report, report)
    print(json.dumps(report["summary"]))
    if report["errors"]: raise SystemExit(1)
