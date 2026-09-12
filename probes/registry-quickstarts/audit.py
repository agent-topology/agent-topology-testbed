"""Separate installed-package observation; does not import or modify graph.py."""
import importlib
import importlib.metadata as metadata
import json
from pathlib import Path
import sys

from agent_topology.spec import canonical_json, compute_structure_hash, validate_document


def require(value, message):
    if not value:
        raise ValueError(message)


prefix = Path(sys.prefix).resolve()
versions = {name: metadata.version(name) for name in
            ("agent-topology-spec", "agent-topology-langgraph", "langgraph")}
require(versions["agent-topology-spec"] == versions["agent-topology-langgraph"] == "0.1.0b2",
        "wrong published topology versions")
imports = {}
for name in ("agent_topology.spec", "agent_topology.langgraph", "langgraph.graph"):
    path = Path(importlib.import_module(name).__file__).resolve()
    require(path.is_relative_to(prefix), "import escaped venv")
    imports[name] = str(path)
for dist in metadata.distributions():
    require(Path(dist.locate_file("")).resolve().is_relative_to(prefix), "distribution escaped venv")
    require(dist.read_text("direct_url.json") is None, "direct/editable distribution")
checks = []
for filename in sys.argv[1:]:
    raw = Path(filename).read_text()
    doc = json.loads(raw)
    require(validate_document(doc) == [], "invalid topology")
    require(compute_structure_hash(doc) == doc["structureHash"], "hash mismatch")
    require(canonical_json(doc) + "\n" == raw, "noncanonical serialization")
    checks.append({"file": Path(filename).name, "valid": True, "hash": doc["structureHash"],
                   "canonical": True})
print(json.dumps({"runtime": sys.version, "prefix": str(prefix), "imports": imports,
                  "versions": versions, "sysPath": sys.path, "checks": checks}, indent=2))
