"""P6-dagster-dynamic: one DynamicOut source, one mapped op, one collect
consumer, over three cardinalities (0, 1, 2 emitted DynamicOutput records)
with explicit stable mapping keys.

Answers two separate questions, kept in separate record sections so one is
never presented as evidence for another:

  static    - what the job declares: op names, each dependency's kind
              (an ordinary `DependencyDefinition` versus a fan-in
              `DynamicCollectDependencyDefinition`), and which outputs are
              declared dynamic (`OutputDefinition.is_dynamic`). True
              regardless of how many `DynamicOutput` records any run
              produces; read without invoking a single compute function.
  execution - `execute_in_process()` results for a fixed cardinality: the
              mapping keys `dynamic_source` actually emitted, the per-key
              step identities Dagster materializes for `mapped`, and
              `collect`'s result. Only execution can show cardinality or a
              concrete mapped-step identity; the static section is
              identical across all three cases.

`is_dynamic=True` on `dynamic_source`'s output and the
`DynamicCollectDependencyDefinition` on `collect`'s input are static,
structural facts: they say the wiring uses dynamic mapping and a fan-in
collect boundary. Neither says how many `DynamicOutput` records a given run
will emit, or what step identities the mapped op will receive: see the
`0`/`1`/`2` cases below for what only execution can show.

    pip install "dagster==1.13.22"
    python dynamic.py --case 1 --mode execution --output out.json
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import tempfile
from pathlib import Path

# Expectations are literal and written before extraction, per case. They are
# predictions from Dagster 1.13.22's documented dynamic-output semantics
# (https://docs.dagster.io/api/dagster/dynamic,
# https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/dependency.py),
# not values copied from a prior run.
#
#   Each DynamicOutput a source op yields gets its own mapped-op step,
#   identified as "<op_name>[<mapping_key>]"; collect blocks on every mapped
#   step and receives a list. Zero DynamicOutput records means the mapped op
#   never gets a step at all (not a skipped one), and querying its per-node
#   output raises rather than returning an empty container -- a public-API
#   limitation this probe records rather than works around. A duplicate
#   mapping key across a single source's yields is a framework-enforced
#   invariant, not a case this probe can reach: Dagster raises
#   DagsterInvariantViolationError from within the run itself (see
#   test_dynamic.py's `mapping_keys` check), before any of this script's own
#   assertions run.

CASE_KEYS = {
    "0": [],
    "1": ["k0"],
    "2": ["k0", "k1"],
}

# Case-independent: op names, dependency kinds, and is_dynamic flags do not
# depend on how many mapping keys a case's op config asks the source to emit.
EXPECTED_STATIC = {
    "job_name": "p6_dynamic",
    "op_names": ["collect", "dynamic_source", "mapped"],
    "dependencies": [
        ["dynamic_source", "result", "mapped", "value", "direct"],
        ["mapped", "result", "collect", "values", "dynamic_collect"],
    ],
    "output_is_dynamic": {
        "collect": {"result": False},
        "dynamic_source": {"result": True},
        "mapped": {"result": False},
    },
}

# Emitted mapping keys, mapped-step identities, and collect results, per
# cardinality. `dynamic_source_output`/`mapped_output` record either the
# per-mapping-key dict `output_for_node` returns, or the fact that it raised
# -- the zero-cardinality public-API limitation named above.
EXPECTED_EXECUTION = {
    "0": {
        "success": True,
        "step_success_keys": ["collect", "dynamic_source"],
        "step_skipped_keys": [],
        "emitted_mapping_keys": [],
        "mapped_step_keys": [],
        "dynamic_source_output": {"status": "error", "error_type": "DagsterInvariantViolationError"},
        "mapped_output": {"status": "error", "error_type": "DagsterInvariantViolationError"},
        "collect_output": [],
    },
    "1": {
        "success": True,
        "step_success_keys": ["collect", "dynamic_source", "mapped[k0]"],
        "step_skipped_keys": [],
        "emitted_mapping_keys": ["k0"],
        "mapped_step_keys": ["mapped[k0]"],
        "dynamic_source_output": {"status": "ok", "value": {"k0": 1}},
        "mapped_output": {"status": "ok", "value": {"k0": 100}},
        "collect_output": [100],
    },
    "2": {
        "success": True,
        "step_success_keys": ["collect", "dynamic_source", "mapped[k0]", "mapped[k1]"],
        "step_skipped_keys": [],
        "emitted_mapping_keys": ["k0", "k1"],
        "mapped_step_keys": ["mapped[k0]", "mapped[k1]"],
        "dynamic_source_output": {"status": "ok", "value": {"k0": 1, "k1": 2}},
        "mapped_output": {"status": "ok", "value": {"k0": 100, "k1": 200}},
        "collect_output": [100, 200],
    },
}


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"observation mismatch: {actual!r} != {expected!r}")


def build_job():
    from dagster import Config, DynamicOut, DynamicOutput, job, op

    class DynamicSourceConfig(Config):
        keys: list

    @op(out=DynamicOut())
    def dynamic_source(config: DynamicSourceConfig):
        for index, key in enumerate(config.keys):
            yield DynamicOutput(value=index + 1, mapping_key=key)

    @op
    def mapped(value):
        return value * 100

    @op
    def collect(values):
        return sorted(values)

    @job
    def p6_dynamic():
        collect(dynamic_source().map(mapped).collect())

    return p6_dynamic


def extract_static(built):
    from dagster._core.definitions.dependency import DynamicCollectDependencyDefinition

    graph = built.graph
    dependencies = []
    for invocation, inputs in graph.dependencies.items():
        consumer_name = invocation.alias or invocation.name
        for input_name, dep in inputs.items():
            if isinstance(dep, DynamicCollectDependencyDefinition):
                dependencies.append([dep.node_name, dep.output_name, consumer_name, input_name, "dynamic_collect"])
            else:
                dependencies.append([dep.node, dep.output, consumer_name, input_name, "direct"])
    return {
        "job_name": built.name,
        "op_names": sorted(node.name for node in graph.nodes),
        "dependencies": sorted(dependencies),
        "output_is_dynamic": {
            node.name: {out_name: out_def.is_dynamic for out_name, out_def in node.definition.output_dict.items()}
            for node in graph.nodes
        },
    }


def node_output(result, name):
    # A dynamic-mapped node with zero emitted DynamicOutput records has no
    # step at all; querying it raises rather than returning an empty
    # container. Record the raise as data, not as a caught-and-hidden error.
    try:
        return {"status": "ok", "value": result.output_for_node(name)}
    except Exception as exc:
        return {"status": "error", "error_type": type(exc).__name__}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=tuple(CASE_KEYS), required=True)
    parser.add_argument("--mode", choices=("static", "execution"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    source = Path(__file__).resolve()
    require_equal(platform.python_version(), "3.11.16")
    require_equal(importlib.metadata.version("dagster"), "1.13.22")
    record = {"case_id": f"P6-dagster-dynamic-{args.case}", "python": platform.python_version(),
              "framework": "dagster", "version": "1.13.22",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
              "evidence_class": args.mode}
    for key in list(os.environ):
        if key.startswith("DAGSTER"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p6-dagster-") as home:
        os.environ["DAGSTER_HOME"] = home
        os.chdir(home)
        try:
            from dagster import DagsterInstance

            p6_dynamic = build_job()

            observed_static = extract_static(p6_dynamic)
            require_equal(observed_static, EXPECTED_STATIC)
            record["static"] = observed_static

            if args.mode == "execution":
                with DagsterInstance.ephemeral(tempdir=home) as instance:
                    result = p6_dynamic.execute_in_process(
                        instance=instance, raise_on_error=True,
                        run_config={"ops": {"dynamic_source": {"config": {"keys": CASE_KEYS[args.case]}}}},
                    )
                emitted_mapping_keys = sorted(
                    event.step_output_data.mapping_key for event in result.all_events
                    if event.step_key == "dynamic_source" and event.event_type_value == "STEP_OUTPUT"
                )
                step_success_keys = sorted(event.step_key for event in result.all_events if event.is_step_success)
                execution = {
                    "success": result.success,
                    "step_success_keys": step_success_keys,
                    "step_skipped_keys": sorted(event.step_key for event in result.all_events
                                                 if event.is_step_skipped),
                    "emitted_mapping_keys": emitted_mapping_keys,
                    "mapped_step_keys": sorted(key for key in step_success_keys if key.startswith("mapped[")),
                    "dynamic_source_output": node_output(result, "dynamic_source"),
                    "mapped_output": node_output(result, "mapped"),
                    "collect_output": node_output(result, "collect")["value"],
                }
                require_equal(execution, EXPECTED_EXECUTION[args.case])
                record["execution"] = execution
        finally:
            os.chdir(previous)
    require_equal(Path(home).exists(), False)
    record["temporary_state_removed"] = True
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
