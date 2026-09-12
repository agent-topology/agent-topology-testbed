"""P0-dagster-linear: two ops, static dependencies and in-process evidence."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import tempfile

EXPECTED_STATIC = {"job_name": "p0_linear", "op_names": ["first", "second"],
                   "dependencies": [["first", "result", "second", "value"]]}
EXPECTED_EXECUTION = {"success": True, "step_success_keys": ["first", "second"],
                      "second_output": 2}


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"observation mismatch: {actual!r} != {expected!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("static", "execution"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    source = Path(__file__).resolve()
    require_equal(platform.python_version(), "3.11.16")
    require_equal(importlib.metadata.version("dagster"), "1.13.22")
    record = {"case_id": "P0-dagster-linear", "python": platform.python_version(),
              "framework": "dagster", "version": "1.13.22",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
              "evidence_class": args.mode}
    for key in list(os.environ):
        if key.startswith("DAGSTER"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p0-dagster-") as home:
        os.environ["DAGSTER_HOME"] = home
        os.chdir(home)
        try:
            from dagster import DagsterInstance, job, op

            @op
            def first():
                return 1

            @op
            def second(value):
                return value + 1

            @job
            def p0_linear():
                second(first())

            observed = {"job_name": p0_linear.name,
                        "op_names": sorted(node.name for node in p0_linear.graph.nodes),
                        "dependencies": sorted([dep.node, dep.output, name.alias or name.name, input_name]
                            for name, inputs in p0_linear.graph.dependencies.items()
                            for input_name, dep in inputs.items())}
            require_equal(observed, EXPECTED_STATIC)
            record["static"] = observed
            if args.mode == "execution":
                with DagsterInstance.ephemeral(tempdir=home) as instance:
                    result = p0_linear.execute_in_process(instance=instance, raise_on_error=True)
                    execution = {"success": result.success,
                        "step_success_keys": sorted(event.step_key for event in result.all_events
                                                    if event.is_step_success),
                        "second_output": result.output_for_node("second")}
                    require_equal(execution, EXPECTED_EXECUTION)
                    record["execution"] = execution
        finally:
            os.chdir(previous)
    require_equal(Path(home).exists(), False)
    record["temporary_state_removed"] = True
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
