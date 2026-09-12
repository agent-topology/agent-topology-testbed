"""P4: inspect two nested invocations, then observe one two-input consumer."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import tempfile
from pathlib import Path


# Literal predictions, independent of graph construction and extraction.
INPUT_VALUES = {"left_seed": 1, "right_seed": 2}
EXPECTED_STATIC = {
    "graph_name": "p4_nested",
    "invocations": [
        ["consume", "consume", "op"],
        ["left", "child", "graph"],
        ["left.finish", "finish", "op"],
        ["left.seed", "seed", "op"],
        ["right", "child", "graph"],
        ["right.finish", "finish", "op"],
        ["right.seed", "seed", "op"],
    ],
    "membership": {
        "p4_nested": ["consume", "left", "right"],
        "left": ["left.finish", "left.seed"],
        "right": ["right.finish", "right.seed"],
    },
    "dependencies": {
        "p4_nested": [["left", "result", "consume", "left"],
                      ["right", "result", "consume", "right"]],
        "left": [["left.seed", "result", "left.finish", "value"]],
        "right": [["right.seed", "result", "right.finish", "value"]],
    },
    "input_mappings": {
        "p4_nested": [["left_seed", "left", "value", None],
                      ["right_seed", "right", "value", None]],
        "left": [["value", "left.seed", "value", None]],
        "right": [["value", "right.seed", "value", None]],
    },
    "output_mappings": {
        "p4_nested": [["result", "consume", "result", False]],
        "left": [["result", "left.finish", "result", False]],
        "right": [["result", "right.finish", "result", False]],
    },
    "same_child_definition": True,
}
EXPECTED_EXECUTION = {
    "success": True,
    "step_success_keys": ["consume", "left.finish", "left.seed", "right.finish", "right.seed"],
    "step_skipped_keys": [],
    "step_failure_keys": [],
    "outputs": {
        "consume": {"left": 20, "right": 30, "sum": 50},
        "left": 20, "left.finish": 20, "left.seed": 2,
        "right": 30, "right.finish": 30, "right.seed": 3,
    },
    "graph_output": {"left": 20, "right": 30, "sum": 50},
}
API_COVERAGE = {
    "invocations_membership_and_definition_reuse": {
        "status": "source_visible_only",
        "attempted_method": "GraphDefinition.nodes; Node.name; Node.definition; GraphDefinition.name",
        "limitation": "nodes and Node accessors are non-underscore source-visible APIs, not documented public enumeration APIs or a promised compatibility surface.",
    },
    "parent_and_internal_dependencies": {
        "status": "source_visible_only",
        "attempted_method": "GraphDefinition.dependencies; NodeInvocation.name/alias; DependencyDefinition.node/output",
        "limitation": "dependencies is a non-underscore property, not a documented public getter. Documented-public-only dependency readback remains unsupported by this attempt.",
    },
    "boundary_input_output_mappings": {
        "status": "observed_public",
        "attempted_method": "GraphDefinition.input_mappings/output_mappings; InputMapping and OutputMapping fields",
        "limitation": "Mapping endpoints are local names. Qualified paths are assembled from their observed invocation scope; discovering that scope uses source-visible nodes.",
    },
    "consumer_inputs_results_and_scoped_outputs": {
        "status": "observed_public_in_execution_mode",
        "attempted_method": "execute_in_process; ExecuteInProcessResult.output_for_node/output_value; all_events",
        "limitation": "One successful required-input case, in-process only; no universal barrier, failure/skip policy, or concurrency conclusion.",
    },
}


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"Observation mismatch:\nactual={actual!r}\nexpected={expected!r}")


def build_graph():
    from dagster import graph, op

    @op
    def seed(value: int) -> int:
        return value + 1

    @op
    def finish(value: int) -> int:
        return value * 10

    @graph
    def child(value):
        return finish(seed(value))

    @op
    def consume(left: int, right: int) -> dict:
        # Echo the actual received values, not execution input or predictions.
        return {"left": left, "right": right, "sum": left + right}

    @graph
    def p4_nested(left_seed, right_seed):
        return consume(child.alias("left")(left_seed), child.alias("right")(right_seed))

    return p4_nested


def extract_static(parent):
    from dagster import GraphDefinition

    # Deliberately two levels, not a recursive general-purpose walker.
    # These non-underscore enumeration properties lack the documented-public
    # status of input_mappings/output_mappings; preserve that gap in the record.
    top_nodes = list(parent.nodes)
    children = [node for node in top_nodes if isinstance(node.definition, GraphDefinition)]
    scopes = [(parent.name, "", parent)] + [
        (node.name, node.name + ".", node.definition) for node in children
    ]
    observed = {"graph_name": parent.name, "invocations": [], "membership": {},
                "dependencies": {}, "input_mappings": {}, "output_mappings": {}}
    for scope, prefix, definition in scopes:
        members = list(definition.nodes)
        observed["membership"][scope] = sorted(prefix + node.name for node in members)
        observed["invocations"].extend(
            [prefix + node.name, node.definition.name,
             "graph" if isinstance(node.definition, GraphDefinition) else "op"]
            for node in members
        )
        observed["dependencies"][scope] = sorted(
            [prefix + dep.node, dep.output, prefix + (invocation.alias or invocation.name), input_name]
            for invocation, inputs in definition.dependencies.items()
            for input_name, dep in inputs.items()
        )
        observed["input_mappings"][scope] = sorted(
            [mapping.graph_input_name, prefix + mapping.mapped_node_name,
             mapping.mapped_node_input_name, mapping.fan_in_index]
            for mapping in definition.input_mappings
        )
        observed["output_mappings"][scope] = sorted(
            [mapping.graph_output_name, prefix + mapping.mapped_node_name,
             mapping.mapped_node_output_name, mapping.from_dynamic_mapping]
            for mapping in definition.output_mappings
        )
    observed["invocations"].sort()
    observed["same_child_definition"] = (
        len(children) == 2 and children[0].definition is children[1].definition
    )
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("static", "execution"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    source = Path(__file__).resolve()
    require_equal(platform.python_version(), "3.11.16")
    require_equal(importlib.metadata.version("dagster"), "1.13.22")
    record = {
        "case_id": "P4-dagster-nested", "evidence_class": args.mode,
        "question": "Which nested invocation identities and boundaries are observable, and what does a two-input consumer receive in one local execution?",
        "minimal_input": {"graph": "two aliases of one two-op child feeding one two-input consumer",
                          "execution_input_values": INPUT_VALUES},
        "framework": "dagster", "version": "1.13.22", "python": platform.python_version(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
        "api_coverage": API_COVERAGE,
        "assertions": {"static": "exact equality with independent EXPECTED_STATIC"},
        "limitations": ["Source-visible enumeration is not a documented public compatibility guarantee.",
                        "No callable evaluation, arbitrary-depth traversal, or universal runtime/concurrency claim."],
    }
    for key in list(os.environ):
        if key.startswith("DAGSTER"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p4-dagster-") as home:
        os.environ["DAGSTER_HOME"] = home
        os.chdir(home)
        try:
            from dagster import DagsterInstance

            parent = build_graph()
            observed_static = extract_static(parent)
            require_equal(observed_static, EXPECTED_STATIC)
            record["static"] = observed_static
            if args.mode == "execution":
                with DagsterInstance.ephemeral(tempdir=home) as instance:
                    result = parent.to_job().execute_in_process(
                        instance=instance, input_values=INPUT_VALUES, raise_on_error=True,
                    )
                    # Query every observed invocation, including graph outputs;
                    # execution step IDs remain framework-provided, not inferred.
                    execution = {
                        "success": result.success,
                        "step_success_keys": sorted(event.step_key for event in result.all_events
                                                    if event.is_step_success),
                        "step_skipped_keys": sorted(event.step_key for event in result.all_events
                                                    if event.is_step_skipped),
                        "step_failure_keys": sorted(event.step_key for event in result.all_events
                                                    if event.is_step_failure),
                        "outputs": {path: result.output_for_node(path)
                                    for path, _, _ in observed_static["invocations"]},
                        "graph_output": result.output_value(),
                    }
                require_equal(execution, EXPECTED_EXECUTION)
                record["execution"] = execution
                record["assertions"]["execution"] = "exact equality with independent EXPECTED_EXECUTION"
        finally:
            os.chdir(previous)
    require_equal(Path(home).exists(), False)
    record["temporary_state_removed"] = True
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
