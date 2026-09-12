"""C1-crewai-flow-probe: router label selection versus listener cardinality,
and AND/OR convergence semantics, over six cases.

No LLM calls, no crew, no tools: every flow method is a fixed, hardcoded
Python function. Answers two separate questions, kept in separate record
sections so one is never presented as evidence for another:

  static   - what the Flow class declares: method names, trigger edges, and
             each listener's condition_type ("AND"/"OR"), read via the public,
             no-kickoff classmethod Flow.flow_definition() and the exported
             crewai.flow.build_flow_structure() projection. True regardless
             of which label a router selects at runtime.
  callable - the router method invoked directly on a freshly constructed,
             not-kicked-off Flow instance. This is direct evaluation of user
             code; it is not engine evidence and never touches the listener-
             dispatch/trigger-accounting machinery.
  execution - flow.kickoff() with the router's return value hardcoded per
             case, and each listener method appending its own name to
             self.state["log"]. This is the only section that shows how many
             times a listener actually ran and in what order.

Two experiments, six cases:

  router-route_a / router-route_b
    One router with two fixed possible labels ("route_a"/"route_b",
    declared via emit=[...] so both are statically enumerable). Two listener
    methods (listener_one, listener_two) are BOTH wired to the same label
    "route_a". Selecting "route_a" fires both listeners from one selection;
    selecting "route_b" fires neither. One label does not imply one listener,
    and listener count is a runtime fact, not a static one.

  and-both / and-only_a / or-both / or-only_a
    A deterministic a-then-b chain: a() is the start method; route(), a
    router on a(), selects "go_b" (case "both") or "skip_b" (case "only_a");
    b() only exists behind the "go_b" label, so case "only_a" never runs b()
    at all -- not merely a no-op body. Two Flow variants share this same
    chain and differ only in the paired join's condition: and_(a, b) versus
    or_(a, b). No timing sleeps; ordering is a causal consequence of the
    chain, not a race.

    pip install "crewai==1.15.21"
    python flow_probe.py --case and-both --mode execution --output out.json
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
from pathlib import Path
from typing import Literal

REQUIRED_PYTHON = "3.11.16"
REQUIRED_CREWAI = "1.15.21"

CASES = (
    "router-route_a", "router-route_b",
    "and-both", "and-only_a",
    "or-both", "or-only_a",
)

# Static structure is identical for both cases of a given experiment: the
# declared graph and every condition_type do not depend on which label a
# router selects at runtime. Recorded once per experiment, read with
# build_flow_structure() (crewai.flow.__all__, exported; no kickoff) which
# projects the lower-level, non-underscore-but-not-exported
# Flow.flow_definition() classmethod. Both are read from the class alone.
EXPECTED_STATIC = {
    "router": {
        "start_methods": ["begin"],
        "router_methods": ["route"],
        "nodes": {
            "begin": {"class_name": "RouterCardinalityFlow", "type": "start"},
            "route": {
                "class_name": "RouterCardinalityFlow", "type": "router",
                "is_router": True, "condition_type": "OR",
                "trigger_condition_type": "OR", "trigger_methods": ["begin"],
                "router_events": ["route_a", "route_b"],
            },
            "listener_one": {
                "class_name": "RouterCardinalityFlow", "type": "listen",
                "condition_type": "OR", "trigger_condition_type": "OR",
                "trigger_methods": ["route_a"],
            },
            "listener_two": {
                "class_name": "RouterCardinalityFlow", "type": "listen",
                "condition_type": "OR", "trigger_condition_type": "OR",
                "trigger_methods": ["route_a"],
            },
        },
        "edges": [
            ["begin", "route", "OR", False, None],
            ["route", "listener_one", None, True, "route_a"],
            ["route", "listener_two", None, True, "route_a"],
        ],
    },
    "and": {
        "start_methods": ["a"],
        "router_methods": ["route"],
        "nodes": {
            "a": {"class_name": "ConvergenceFlow", "type": "start"},
            "route": {
                "class_name": "ConvergenceFlow", "type": "router",
                "is_router": True, "condition_type": "OR",
                "trigger_condition_type": "OR", "trigger_methods": ["a"],
                "router_events": ["go_b", "skip_b"],
            },
            "b": {
                "class_name": "ConvergenceFlow", "type": "listen",
                "condition_type": "OR", "trigger_condition_type": "OR",
                "trigger_methods": ["go_b"],
            },
            "join": {
                "class_name": "ConvergenceFlow", "type": "listen",
                "condition_type": "AND", "trigger_condition_type": "AND",
                "trigger_methods": ["a", "b"],
                "trigger_condition": {"type": "AND", "conditions": ["a", "b"]},
            },
        },
        "edges": [
            ["a", "join", "AND", False, None],
            ["a", "route", "OR", False, None],
            ["b", "join", "AND", False, None],
            ["route", "b", None, True, "go_b"],
        ],
    },
    "or": {
        "start_methods": ["a"],
        "router_methods": ["route"],
        "nodes": {
            "a": {"class_name": "ConvergenceFlow", "type": "start"},
            "route": {
                "class_name": "ConvergenceFlow", "type": "router",
                "is_router": True, "condition_type": "OR",
                "trigger_condition_type": "OR", "trigger_methods": ["a"],
                "router_events": ["go_b", "skip_b"],
            },
            "b": {
                "class_name": "ConvergenceFlow", "type": "listen",
                "condition_type": "OR", "trigger_condition_type": "OR",
                "trigger_methods": ["go_b"],
            },
            "join": {
                "class_name": "ConvergenceFlow", "type": "listen",
                "condition_type": "OR", "trigger_condition_type": "OR",
                "trigger_methods": ["a", "b"],
                "trigger_condition": {"type": "OR", "conditions": ["a", "b"]},
            },
        },
        "edges": [
            ["a", "join", "OR", False, None],
            ["a", "route", "OR", False, None],
            ["b", "join", "OR", False, None],
            ["route", "b", None, True, "go_b"],
        ],
    },
}

# The router's hardcoded return value and its raw callable result -- direct
# invocation of user code on a freshly constructed, not-kicked-off instance.
# Never touches Flow's listener-dispatch/trigger-accounting machinery.
EXPECTED_CALLABLE = {
    "router-route_a": {"callback_result": "route_a"},
    "router-route_b": {"callback_result": "route_b"},
    "and-both": {"callback_result": "go_b"},
    "and-only_a": {"callback_result": "skip_b"},
    "or-both": {"callback_result": "go_b"},
    "or-only_a": {"callback_result": "skip_b"},
}

# kickoff() results. "log" is the ordered sequence of method invocations
# (each method appends its own name to self.state["log"]); a name appearing
# twice is two separate invocations, not one. join_count is only meaningful
# for the and-*/or-* cases.
EXPECTED_EXECUTION = {
    "router-route_a": {"log": ["begin", "route", "listener_one", "listener_two"]},
    "router-route_b": {"log": ["begin", "route"]},
    "and-both": {"log": ["a", "route", "b", "join"], "join_count": 1},
    "and-only_a": {"log": ["a", "route"], "join_count": 0},
    "or-both": {"log": ["a", "route", "join", "b"], "join_count": 1},
    "or-only_a": {"log": ["a", "route", "join"], "join_count": 1},
}


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"observation mismatch: {actual!r} != {expected!r}")


def build_router_cardinality_flow(selected_label):
    from crewai.flow.flow import Flow, listen, router, start

    def begin(self):
        self.state["log"] = self.state.get("log", []) + ["begin"]
        return "begin-out"

    def route(self) -> Literal["route_a", "route_b"]:
        self.state["log"] = self.state.get("log", []) + ["route"]
        return selected_label

    def listener_one(self):
        self.state["log"] = self.state.get("log", []) + ["listener_one"]

    def listener_two(self):
        self.state["log"] = self.state.get("log", []) + ["listener_two"]

    namespace = {
        "begin": start()(begin),
        "route": router(begin, emit=["route_a", "route_b"])(route),
        "listener_one": listen("route_a")(listener_one),
        "listener_two": listen("route_a")(listener_two),
    }
    return type("RouterCardinalityFlow", (Flow,), namespace)


def build_convergence_flow(join_kind, case):
    from crewai.flow.flow import Flow, and_, or_, listen, router, start

    def a(self):
        self.state["log"] = self.state.get("log", []) + ["a"]
        return "a-out"

    def route(self) -> Literal["go_b", "skip_b"]:
        self.state["log"] = self.state.get("log", []) + ["route"]
        return "go_b" if case == "both" else "skip_b"

    def b(self):
        self.state["log"] = self.state.get("log", []) + ["b"]
        return "b-out"

    def join(self):
        self.state["log"] = self.state.get("log", []) + ["join"]
        self.state["join_count"] = self.state.get("join_count", 0) + 1

    namespace = {
        "a": start()(a),
        "route": router(a, emit=["go_b", "skip_b"])(route),
        "b": listen("go_b")(b),
    }
    cls = type("ConvergenceFlow", (Flow,), namespace)
    condition = and_(cls.a, cls.b) if join_kind == "and" else or_(cls.a, cls.b)
    cls.join = listen(condition)(join)
    return cls


def build_flow_class(case):
    if case.startswith("router-"):
        label = case.split("-", 1)[1]
        return build_router_cardinality_flow(label), "router"
    join_kind, subcase = case.split("-", 1)
    return build_convergence_flow(join_kind, subcase), join_kind


def normalize_structure(structure):
    nodes = {name: dict(sorted(meta.items())) for name, meta in structure["nodes"].items()}
    edges = sorted(
        (
            edge.get("source"), edge.get("target"), edge.get("condition_type"),
            edge.get("is_router_event"), edge.get("router_event"),
        )
        for edge in structure["edges"]
    )
    return {
        "start_methods": sorted(structure["start_methods"]),
        "router_methods": sorted(structure["router_methods"]),
        "nodes": nodes,
        "edges": [list(edge) for edge in edges],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--mode", choices=("static", "callable", "execution"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    source = Path(__file__).resolve()

    require_equal(platform.python_version(), REQUIRED_PYTHON)
    require_equal(importlib.metadata.version("crewai"), REQUIRED_CREWAI)

    # No LLM calls, no crew, no tools are constructed anywhere in this probe.
    # crewai_core.telemetry.CoreTelemetry._is_telemetry_disabled() (read from
    # installed source) checks exactly these three flags before ever building
    # an OTLP span exporter; any one of them is sufficient, all three are set
    # here for an explicit, redundant guard against a network telemetry call.
    os.environ["OTEL_SDK_DISABLED"] = "true"
    os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
    os.environ["CREWAI_DISABLE_TRACKING"] = "true"
    # CREWAI_TRACING_ENABLED governs Crew.kickoff()'s tracing gate, not a bare
    # Flow's -- Flow.kickoff() consults only a context variable that nothing
    # sets outside of Crew.kickoff() (verified empirically; see
    # observations/C1/README.md). Set anyway: harmless, and correct if a
    # future crewai version wires Flow through the same gate.
    os.environ["CREWAI_TRACING_ENABLED"] = "false"

    record = {
        "case_id": f"C1-crewai-flow-probe-{args.case}",
        "python": platform.python_version(),
        "framework": "crewai",
        "version": REQUIRED_CREWAI,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
        "evidence_class": args.mode,
    }

    # A fixed (not per-process-random) name: crewai.flow.Flow.kickoff() checks
    # only a context variable set by Crew.kickoff(), never CREWAI_TRACING_ENABLED
    # directly, for its first-run consent bookkeeping (verified empirically:
    # see observations/C1/README.md). A random name would make every one of
    # this probe's invocations look like a first run and write that bookkeeping
    # file over and over, outside this repository, under the real user's
    # application-support directory; a fixed name confines that one-time write
    # (if any) to a single, clearly-named, easy-to-find-and-delete subdirectory
    # there instead of one new directory per invocation.
    os.environ["CREWAI_STORAGE_DIR"] = "c1-crewai-probe"
    flow_cls, shape = build_flow_class(args.case)

    if args.mode == "static":
        from crewai.flow.visualization import build_flow_structure
        observed_static = normalize_structure(build_flow_structure(flow_cls))
        require_equal(observed_static, EXPECTED_STATIC[shape])
        record["static"] = observed_static

    if args.mode in ("callable", "execution"):
        # Direct invocation of user code on a freshly constructed,
        # not-kicked-off instance. This never touches Flow's
        # listener-dispatch/trigger-accounting machinery; it is not
        # engine evidence of which listeners the engine will run.
        callable_instance = flow_cls()
        callback_result = callable_instance.route()
        observed_callable = {"callback_result": callback_result}
        require_equal(observed_callable, EXPECTED_CALLABLE[args.case])
        record["callable"] = observed_callable

    if args.mode == "execution":
        execution_instance = flow_cls()
        execution_instance.kickoff()
        state = dict(execution_instance.state)
        state.pop("id", None)  # generated run ID; excluded per evidence conventions
        observed_execution = {"log": state.get("log", [])}
        if "join_count" in EXPECTED_EXECUTION[args.case]:
            observed_execution["join_count"] = state.get("join_count", 0)
        require_equal(observed_execution, EXPECTED_EXECUTION[args.case])
        record["execution"] = observed_execution

    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
