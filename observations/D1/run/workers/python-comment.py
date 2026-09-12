"""D1: compiled definitions only; every node body fails if called."""
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import sys
from typing import TypedDict

import agent_topology.langgraph as producer
import agent_topology.spec as spec
import langgraph.graph as framework


def fail():
    raise RuntimeError("D1_NODE_BODY_EXECUTED")


def named_step(state):
    return fail()


def build(recipe):
    state = TypedDict("State", {"value": str})
    graph = framework.StateGraph(state)
    for node in recipe["nodes"]:
        body = named_step if recipe["callable"] == "named" else lambda state: fail()
        graph.add_node(node, body, metadata=recipe["metadata"])
    for source, target in recipe["edges"]:
        graph.add_edge(source, target)
    for sources, target in recipe["joins"]:
        graph.add_edge(sources, target)
    return graph.compile(name="d1")


if __name__ == "__main__":
    raw = Path(sys.argv[1]).read_bytes()
    recipe = json.loads(raw)
    compiled = build(recipe)
    # D1_UNRELATED_COMMENT changed without executable edits
    documents = []
    for _ in range(2):
        document = producer.describe(compiled)
        errors = spec.validate_document(document)
        if errors:
            raise RuntimeError(str(errors))
        documents.append({"document": document, "canonical": spec.canonical_json(document),
                          "computedHash": spec.compute_structure_hash(document)})
    print(json.dumps({"inputSha256": hashlib.sha256(raw).hexdigest(),
                      "identity": {"runtime": sys.version, "executable": sys.executable,
                                   "pid": os.getpid(), "prefix": sys.prefix,
                                   "versions": {n: metadata.version(n) for n in
                                                ("agent-topology-langgraph", "agent-topology-spec", "langgraph")},
                                   "imports": {"producer": producer.__file__, "spec": spec.__file__,
                                               "framework": framework.__file__}},
                      "describes": documents}, ensure_ascii=False))
