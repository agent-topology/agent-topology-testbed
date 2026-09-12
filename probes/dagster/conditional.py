"""P2-dagster-conditional: one op with two optional outputs and two
downstream consumers, over three emission cases, plus an ordinary
required-output fan-out control with its own two consumers in the same job.

Answers two separate questions, kept in separate record sections so one is
never presented as evidence for another:

  static    - what the job declares: op names, wiring, and each output's
              `is_required` flag. True regardless of what any op computes;
              read without invoking a single compute function.
  execution - `execute_in_process()` step results and emitted outputs for a
              fixed op-config selection. This is the only section that can
              show a step skipped versus run.

`is_required=False` is a static, structural fact. It is not, by itself, a
claim about which of an op's optional outputs a given run will emit, or which
downstream consumers will execute: see the `none`/`single`/`multiple` cases
below for what only execution can show. Dependency wiring alone does not
distinguish an ordinary edge from an optional-output edge either -- both are
just an ["op", "output"] -> ["op", "input"] pair; only the paired
`is_required` flag on the producing side marks the optional ones.

The `fanout` op and its two consumers are an ordinary required-output
fan-out, present in every case as a control: an in-process run completing
both of its consumers successfully shows completion, not concurrency (see
docs/evidence.md and P1's normalization/limitations section).

    pip install "dagster==1.13.22"
    python conditional.py --case single --mode execution --output out.json
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import tempfile

# Expectations are literal and written before extraction, per case. They are
# predictions from Dagster 1.13.22's documented optional-output semantics
# (https://docs.dagster.io/api/dagster/ops#dagster.Out,
# https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/output.py),
# not values copied from a prior run.
#
#   An Out(is_required=False) output that is not yielded by the op's compute
#   function causes every step that depends on it to be skipped, not failed;
#   the run itself still succeeds. An ordinary (default is_required=True)
#   output has no such skip path -- both its downstream consumers always run.

CASE_EMIT = {
    "none": [],
    "single": ["branch_a"],
    "multiple": ["branch_a", "branch_b"],
}

# Case-independent: op names, wiring, and is_required flags do not depend on
# what the case's op config asks the compute function to emit.
EXPECTED_STATIC = {
    "job_name": "p2_conditional",
    "op_names": [
        "conditional_source", "consumer_branch_a", "consumer_branch_b",
        "consumer_fanout_a", "consumer_fanout_b", "fanout_source",
    ],
    "dependencies": [
        ["conditional_source", "branch_a", "consumer_branch_a", "value"],
        ["conditional_source", "branch_b", "consumer_branch_b", "value"],
        ["fanout_source", "result", "consumer_fanout_a", "value"],
        ["fanout_source", "result", "consumer_fanout_b", "value"],
    ],
    "output_is_required": {
        "conditional_source": {"branch_a": False, "branch_b": False},
        "consumer_branch_a": {"result": True},
        "consumer_branch_b": {"result": True},
        "fanout_source": {"result": True},
        "consumer_fanout_a": {"result": True},
        "consumer_fanout_b": {"result": True},
    },
}

# Emitted outputs, per-step results, and the surviving consumer outputs. The
# fan-out control's four steps (fanout_source and both consumers) always
# succeed: they do not depend on the conditional_source case at all.
EXPECTED_EXECUTION = {
    "none": {
        "success": True,
        "emitted_outputs": [],
        "step_success_keys": [
            "conditional_source", "consumer_fanout_a", "consumer_fanout_b", "fanout_source",
        ],
        "step_skipped_keys": ["consumer_branch_a", "consumer_branch_b"],
        "consumer_outputs": {"consumer_fanout_a": 100, "consumer_fanout_b": 100},
    },
    "single": {
        "success": True,
        "emitted_outputs": ["branch_a"],
        "step_success_keys": [
            "conditional_source", "consumer_branch_a", "consumer_fanout_a",
            "consumer_fanout_b", "fanout_source",
        ],
        "step_skipped_keys": ["consumer_branch_b"],
        "consumer_outputs": {"consumer_branch_a": 1, "consumer_fanout_a": 100, "consumer_fanout_b": 100},
    },
    "multiple": {
        "success": True,
        "emitted_outputs": ["branch_a", "branch_b"],
        "step_success_keys": [
            "conditional_source", "consumer_branch_a", "consumer_branch_b",
            "consumer_fanout_a", "consumer_fanout_b", "fanout_source",
        ],
        "step_skipped_keys": [],
        "consumer_outputs": {
            "consumer_branch_a": 1, "consumer_branch_b": 2,
            "consumer_fanout_a": 100, "consumer_fanout_b": 100,
        },
    },
}


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"observation mismatch: {actual!r} != {expected!r}")


def build_job():
    from dagster import Config, In, Out, Output, job, op

    class ConditionalSourceConfig(Config):
        emit: list

    @op(out={"branch_a": Out(is_required=False), "branch_b": Out(is_required=False)})
    def conditional_source(config: ConditionalSourceConfig):
        if "branch_a" in config.emit:
            yield Output(1, output_name="branch_a")
        if "branch_b" in config.emit:
            yield Output(2, output_name="branch_b")

    @op(ins={"value": In()})
    def consumer_branch_a(value):
        return value

    @op(ins={"value": In()})
    def consumer_branch_b(value):
        return value

    @op
    def fanout_source():
        return 100

    @op(ins={"value": In()})
    def consumer_fanout_a(value):
        return value

    @op(ins={"value": In()})
    def consumer_fanout_b(value):
        return value

    @job
    def p2_conditional():
        branch_a, branch_b = conditional_source()
        consumer_branch_a(branch_a)
        consumer_branch_b(branch_b)
        result = fanout_source()
        consumer_fanout_a(result)
        consumer_fanout_b(result)

    return p2_conditional


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=tuple(CASE_EMIT), required=True)
    parser.add_argument("--mode", choices=("static", "execution"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    source = Path(__file__).resolve()
    require_equal(platform.python_version(), "3.11.16")
    require_equal(importlib.metadata.version("dagster"), "1.13.22")
    record = {"case_id": f"P2-dagster-conditional-{args.case}", "python": platform.python_version(),
              "framework": "dagster", "version": "1.13.22",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
              "evidence_class": args.mode}
    for key in list(os.environ):
        if key.startswith("DAGSTER"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p2-dagster-") as home:
        os.environ["DAGSTER_HOME"] = home
        os.chdir(home)
        try:
            from dagster import DagsterInstance

            p2_conditional = build_job()

            observed_static = {
                "job_name": p2_conditional.name,
                "op_names": sorted(node.name for node in p2_conditional.graph.nodes),
                "dependencies": sorted([dep.node, dep.output, name.alias or name.name, input_name]
                    for name, inputs in p2_conditional.graph.dependencies.items()
                    for input_name, dep in inputs.items()),
                "output_is_required": {
                    node.name: {out_name: out_def.is_required
                                for out_name, out_def in node.definition.output_dict.items()}
                    for node in p2_conditional.graph.nodes
                },
            }
            require_equal(observed_static, EXPECTED_STATIC)
            record["static"] = observed_static

            if args.mode == "execution":
                with DagsterInstance.ephemeral(tempdir=home) as instance:
                    result = p2_conditional.execute_in_process(
                        instance=instance, raise_on_error=True,
                        run_config={"ops": {"conditional_source": {"config": {"emit": CASE_EMIT[args.case]}}}},
                    )
                emitted_outputs = sorted(
                    event.step_output_data.step_output_handle.output_name
                    for event in result.all_events
                    if event.step_key == "conditional_source" and event.event_type_value == "STEP_OUTPUT"
                )
                consumer_names = (
                    "consumer_branch_a", "consumer_branch_b", "consumer_fanout_a", "consumer_fanout_b",
                )
                consumer_outputs = {}
                for name in consumer_names:
                    try:
                        consumer_outputs[name] = result.output_for_node(name)
                    except Exception:
                        pass
                execution = {
                    "success": result.success,
                    "emitted_outputs": emitted_outputs,
                    "step_success_keys": sorted(event.step_key for event in result.all_events
                                                 if event.is_step_success),
                    "step_skipped_keys": sorted(event.step_key for event in result.all_events
                                                 if event.is_step_skipped),
                    "consumer_outputs": consumer_outputs,
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
