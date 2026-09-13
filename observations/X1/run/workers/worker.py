"""X1 Python builder: minimum compiled definitions; every user body fails."""
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import sys
from typing import TypedDict

import agent_topology.langgraph as producer
import agent_topology.spec as spec
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    value: str


def forbidden(_state):
    raise RuntimeError("X1_USER_BODY_EXECUTED")


def chain(runnable=forbidden):
    graph = StateGraph(State)
    graph.add_node("child", runnable)
    graph.add_edge(START, "child")
    graph.add_edge("child", END)
    return graph.compile()


def build(case):
    if case in {"opaque-child", "ordinary-node"}:
        return chain(chain() if case == "opaque-child" else forbidden)
    graph = StateGraph(State)
    if case in {"direct-fanout", "conditional-router"}:
        for name in ("router", "a", "b"):
            graph.add_node(name, forbidden)
        graph.add_edge(START, "router")
        if case == "direct-fanout":
            graph.add_edge("router", "a")
            graph.add_edge("router", "b")
        else:
            graph.add_conditional_edges("router", forbidden, ["a", "b"])
        graph.add_edge("a", END)
        graph.add_edge("b", END)
    elif case == "orphan-router":
        graph.add_node("router", forbidden)
        graph.add_node("target", forbidden)
        graph.add_edge(START, "router")
        graph.add_conditional_edges("router", forbidden)
        graph.add_edge("target", END)
    elif case in {"multi-source-join", "independent-edges"}:
        for name in ("a", "b", "joined"):
            graph.add_node(name, forbidden)
        graph.add_edge(START, "a")
        graph.add_edge(START, "b")
        if case == "multi-source-join":
            graph.add_edge(["a", "b"], "joined")
        else:
            graph.add_edge("a", "joined")
            graph.add_edge("b", "joined")
        graph.add_edge("joined", END)
    elif case == "sentinels":
        graph.add_edge(START, END)
    else:
        raise ValueError(case)
    return graph.compile()


def observe(case):
    graph_id = "custom-router" if case == "orphan-router" else "main"
    document = producer.describe(build(case), graph_id=graph_id)
    errors = spec.validate_document(document)
    if errors:
        raise RuntimeError(str(errors))
    canonical = spec.canonical_json(document)
    if json.loads(canonical) != document:
        raise RuntimeError("canonical round trip")
    computed = spec.compute_structure_hash(document)
    if computed != document["structureHash"]:
        raise RuntimeError("structure hash")
    structure = document["graphs"][0]["structure"]
    return {
        "case": case,
        "inputSha256": hashlib.sha256(case.encode()).hexdigest(),
        "identity": {
            "runtime": sys.version,
            "executable": sys.executable,
            "pid": os.getpid(),
            "prefix": sys.prefix,
            "versions": {name: metadata.version(name) for name in (
                "agent-topology-langgraph", "agent-topology-spec", "langgraph")},
            "imports": {"producer": producer.__file__, "spec": spec.__file__},
        },
        "document": document,
        "computedHash": computed,
        "derivedJoinEdges": spec.derived_join_edges(structure),
    }


if __name__ == "__main__":
    print(json.dumps(observe(sys.argv[1]), ensure_ascii=False))
