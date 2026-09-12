"""One static extraction, followed by separately labeled callback evaluation."""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import sys
from typing import TypedDict

import agent_topology.langgraph as producer
import agent_topology.spec as spec
import langgraph.graph as framework

# -I isolates site imports. Only the checked-in local ADR model is added here,
# after importing the measured packages; their import paths are retained below.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import evaluate


def extract(case):
    phase = "extract"
    calls = {"node": 0, "router_during_extraction": 0, "router_direct": 0}

    def body(state):
        calls["node"] += 1
        raise RuntimeError("R3_NODE_BODY_EXECUTED")

    def route(state):
        if phase == "extract":
            calls["router_during_extraction"] += 1
            raise RuntimeError("R3_ROUTER_EXECUTED_DURING_EXTRACTION")
        calls["router_direct"] += 1
        return "a" if case["routing"] == "single" else ["a", "b"]

    state = TypedDict("State", {"value": str})
    graph = framework.StateGraph(state)
    for node in ("router", "a", "b"):
        graph.add_node(node, body)
    graph.add_edge(framework.START, "router")
    if case["routing"] == "direct":
        graph.add_edge("router", "a")
        graph.add_edge("router", "b")
    elif case["routing"] in ("single", "list"):
        graph.add_conditional_edges("router", route, {"a": "a", "b": "b"})
    else:
        raise ValueError("unknown routing recipe")
    graph.add_edge("a", framework.END)
    graph.add_edge("b", framework.END)
    compiled = graph.compile(name="r3-minimal", interrupt_before=case["interrupt_before"])
    document = producer.describe(compiled, depth=0)
    errors = spec.validate_document(document)
    if errors:
        raise ValueError(f"invalid producer document: {errors}")
    before = json.dumps(document, sort_keys=True)
    verdicts = {"default": evaluate(document),
                "override": evaluate(document, allow_parallel_interrupt=True)}
    if json.dumps(document, sort_keys=True) != before:
        raise ValueError("ADR model mutated the document")
    phase = "direct-call"
    callback = ({"evaluated": False} if case["routing"] == "direct" else
                {"evaluated": True, "input": {"value": "unused"},
                 "result": route({"value": "unused"})})
    return {"document": document, "core_validation_errors": errors,
            "adr_model": verdicts, "callable": callback, "calls": calls}


if __name__ == "__main__":
    raw = Path(sys.argv[1]).read_bytes()
    record = extract(json.loads(raw))
    record.update({"input_sha256": hashlib.sha256(raw).hexdigest(),
                   "evidence_classes": ["static producer extraction", "callable ADR model",
                                        "direct router callable evaluation; no framework execution"],
                   "identity": {"python": platform.python_version(), "executable": sys.executable,
                                "prefix": sys.prefix,
                                "versions": {p: metadata.version(p) for p in
                                             ("agent-topology-langgraph", "agent-topology-spec", "langgraph")},
                                "imports": {"producer": producer.__file__, "spec": spec.__file__,
                                            "framework": framework.__file__}}})
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
