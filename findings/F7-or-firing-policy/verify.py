"""Audit existing C1 records and pinned contracts; no framework imports or execution."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFS = {
    "beta2": "cbd2f404a36834fb9ba318500b7832f03ba610da",
    "c1": "3715dd32a0efc3e7bd500d26d038774d6a37f4e6",
    "current_2026_09_12": "eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe",
}


def require(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: {actual!r} != {expected!r}")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit(upstream):
    source = (ROOT / "probes/crewai/flow_probe.py").read_bytes()
    lock = (ROOT / "probes/crewai/requirements.lock").read_bytes()
    # Literal expectations only: do not import the probe or derive them from output.
    constants = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("EXPECTED_"):
                    constants[target.id] = ast.literal_eval(node.value)
    records = {}
    for case in ("and-both", "and-only_a", "or-both", "or-only_a"):
        for mode in ("static", "callable", "execution"):
            pair = []
            for run in (1, 2):
                path = ROOT / f"observations/C1/c1-{case}-{mode}-{run}.json"
                raw = path.read_bytes()
                pair.append(raw)
                record = json.loads(raw)
                for key, value in {
                    "source_sha256": digest(source), "lock_sha256": digest(lock),
                    "framework": "crewai", "version": "1.15.21", "python": "3.11.16",
                    "case_id": f"C1-crewai-flow-probe-{case}", "evidence_class": mode,
                }.items():
                    require(record[key], value, f"{path.name} {key}")
                for section in ("static", "callable", "execution"):
                    if section == mode or (mode == "execution" and section == "callable"):
                        key = case.split("-")[0] if section == "static" else case
                        require(record[section], constants[f"EXPECTED_{section.upper()}"][key], path.name)
                records[str(path.relative_to(ROOT))] = digest(raw)
            require(pair[0], pair[1], f"{case} {mode} byte-identical pair")

    files = [
        "spec/agent-topology.schema.json", "docs/0.1-contract.md",
        "docs/guides/concepts.md", "docs/guides/consuming-documents.md",
        "docs/decisions/0003-canonical-ordering-and-versioned-structure-hash.md",
        "conformance/fixtures/multi-source-join/fixture.json",
        "conformance/fixtures/multi-source-join/expected.json",
    ]
    helper = "packages/python/spec/src/agent_topology/spec/_joins.py"
    extension = "spec/experimental/interpretation-v1.schema.json"
    contracts, contents = {}, {}
    for label, ref in REFS.items():
        contents[label] = {}
        for path in files + ([helper, extension] if label != "beta2" else []):
            raw = subprocess.check_output(["git", "-C", str(upstream), "show", f"{ref}:{path}"])
            contents[label][path] = raw
        schema = json.loads(contents[label][files[0]])
        require(set(schema["$defs"]["join"]["properties"]), {"id", "sources", "target"}, label)
        require(set(schema["$defs"]["edge"]["properties"]), {"id", "source", "target", "kind"}, label)
        if label != "beta2":
            require(b"AND convergence: all its sources" in contents[label][files[3]], True, label)
            require(b"AND convergence semantics" in contents[label][helper], True, label)
            props = json.loads(contents[label][extension])["properties"]["nodes"]["items"]["properties"]
            require(set(props), {"nodeId", "branch", "subgraph", "sentinel", "entry"}, label)
        contracts[label] = {"commit": ref, "sha256": {p: digest(b) for p, b in contents[label].items()}}
    for path in (files[0], files[3], helper):
        require(contents["c1"][path], contents["current_2026_09_12"][path], f"unchanged {path}")
    require(contents["beta2"][files[0]], contents["c1"][files[0]], "unchanged beta.2 schema")
    return {"evidence_class": "saved-record and contract audit; no new framework execution",
            "record_count": len(records), "pair_count": 12, "records_sha256": records,
            "source_sha256": digest(source), "lock_sha256": digest(lock), "contracts": contracts}


if __name__ == "__main__":
    result = audit(Path(sys.argv[1]))
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 3 and sys.argv[2] == "--write":
        (HERE / "evidence/audit.json").write_text(encoded)
    else:
        require(encoded, (HERE / "evidence/audit.json").read_text(), "saved audit")
    print("PASS: 24 records, 12 equal pairs, literal assertions, source/lock hashes, 3 pinned contracts")
