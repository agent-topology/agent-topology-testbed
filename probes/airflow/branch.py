"""P1-airflow-branch: one router, two destinations, two joins with different
trigger rules, over three branch-selection cases.

Answers three separate questions, kept in separate record sections so one is
never presented as evidence for another:

  static   - what the DAG declares: which tasks exist, which edges are wired,
             and each join's trigger rule. True regardless of any callback.
  callable - what the router's python_callable returns when invoked directly.
             This is user code, not the scheduler; it does not by itself prove
             which tasks the scheduler will skip or run.
  execution - dag.test() task-instance states for a fixed logical date. This
             is the only section that reflects scheduler behavior.

    pip install "apache-airflow==2.10.5"
    python branch.py --case single --mode execution --output out.json
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

# Expectations are literal and written before extraction, per case. They are
# predictions from the documented 2.10.5 trigger-rule semantics
# (https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#trigger-rules),
# not values copied from a prior run.
#
#   all_success                 - skipped if any upstream was skipped.
#   none_failed_min_one_success - runs if no upstream failed and at least one
#                                  upstream succeeded; skipped otherwise.

CASE_CALLBACKS = {
    "single": lambda: "a",
    "multiple": lambda: ["a", "b"],
    "none": lambda: None,
}

# Case-independent: the DAG's wiring and each join's trigger rule do not
# depend on what the router's callable returns.
EXPECTED_STATIC = {
    "dag_id": "p1_branch",
    "task_ids": ["a", "b", "join_all_success", "join_none_failed_min_one_success", "router"],
    "dependencies": [
        ["a", "join_all_success"], ["a", "join_none_failed_min_one_success"],
        ["b", "join_all_success"], ["b", "join_none_failed_min_one_success"],
        ["router", "a"], ["router", "b"],
    ],
    "router_downstream_declared": ["a", "b"],
    "join_trigger_rules": {
        "join_all_success": "all_success",
        "join_none_failed_min_one_success": "none_failed_min_one_success",
    },
}

# The router's callback result and its normalized target-set reading, kept
# separate from any claim about what the scheduler does with it.
EXPECTED_CALLABLE = {
    "single": {"callback_result": "a", "selected_targets_normalized": ["a"]},
    "multiple": {"callback_result": ["a", "b"], "selected_targets_normalized": ["a", "b"]},
    "none": {"callback_result": None, "selected_targets_normalized": []},
}

# dag.test() task-instance states. The multiple-selection case runs both
# destinations and both joins concurrently succeed: the old "BranchPythonOperator
# fan-out is exclusive" claim does not hold once a callback selects more than
# one target. The two joins diverge only in the single-selection case, where
# changing nothing but the trigger rule changes whether the join runs.
EXPECTED_EXECUTION = {
    "single": {
        "dag_state": "success",
        "task_instances": [
            {"task_id": "a", "map_index": -1, "state": "success"},
            {"task_id": "b", "map_index": -1, "state": "skipped"},
            {"task_id": "join_all_success", "map_index": -1, "state": "skipped"},
            {"task_id": "join_none_failed_min_one_success", "map_index": -1, "state": "success"},
            {"task_id": "router", "map_index": -1, "state": "success"},
        ],
    },
    "multiple": {
        "dag_state": "success",
        "task_instances": [
            {"task_id": "a", "map_index": -1, "state": "success"},
            {"task_id": "b", "map_index": -1, "state": "success"},
            {"task_id": "join_all_success", "map_index": -1, "state": "success"},
            {"task_id": "join_none_failed_min_one_success", "map_index": -1, "state": "success"},
            {"task_id": "router", "map_index": -1, "state": "success"},
        ],
    },
    "none": {
        "dag_state": "success",
        "task_instances": [
            {"task_id": "a", "map_index": -1, "state": "skipped"},
            {"task_id": "b", "map_index": -1, "state": "skipped"},
            {"task_id": "join_all_success", "map_index": -1, "state": "skipped"},
            {"task_id": "join_none_failed_min_one_success", "map_index": -1, "state": "skipped"},
            {"task_id": "router", "map_index": -1, "state": "success"},
        ],
    },
}


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"observation mismatch: {actual!r} != {expected!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=tuple(CASE_CALLBACKS), required=True)
    parser.add_argument("--mode", choices=("static", "callable", "execution"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    source = Path(__file__).resolve()
    require_equal(platform.python_version(), "3.11.16")
    require_equal(importlib.metadata.version("apache-airflow"), "2.10.5")
    record = {"case_id": f"P1-airflow-branch-{args.case}", "python": platform.python_version(),
              "framework": "apache-airflow", "version": "2.10.5",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
              "evidence_class": args.mode}
    # This command is process-scoped: never import Airflow before isolation.
    for key in list(os.environ):
        if key.startswith("AIRFLOW"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p1-airflow-") as home:
        os.environ.update({"AIRFLOW_HOME": home,
            "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": f"sqlite:///{home}/airflow.db",
            "AIRFLOW__CORE__LOAD_EXAMPLES": "False",
            "AIRFLOW__CORE__EXECUTOR": "SequentialExecutor",
            "AIRFLOW__CORE__DAGS_FOLDER": f"{home}/dags",
            "AIRFLOW__CORE__PLUGINS_FOLDER": f"{home}/plugins",
            "AIRFLOW__CORE__UNIT_TEST_MODE": "True"})
        os.chdir(home)
        try:
            if args.mode == "execution":
                subprocess.run([sys.executable, "-m", "airflow", "db", "migrate"], check=True)
            from airflow import DAG, settings
            from airflow.operators.empty import EmptyOperator
            from airflow.operators.python import BranchPythonOperator
            from airflow.utils.trigger_rule import TriggerRule
            from datetime import datetime, timezone

            callback = CASE_CALLBACKS[args.case]
            with DAG("p1_branch", start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                     schedule=None, catchup=False) as dag:
                router = BranchPythonOperator(task_id="router", python_callable=callback)
                a = EmptyOperator(task_id="a")
                b = EmptyOperator(task_id="b")
                join_all = EmptyOperator(task_id="join_all_success", trigger_rule=TriggerRule.ALL_SUCCESS)
                join_min1 = EmptyOperator(
                    task_id="join_none_failed_min_one_success",
                    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
                )
                router >> [a, b]
                [a, b] >> join_all
                [a, b] >> join_min1

            observed_static = {
                "dag_id": dag.dag_id,
                "task_ids": sorted(dag.task_ids),
                "dependencies": sorted([task.task_id, downstream]
                    for task in dag.tasks for downstream in task.downstream_task_ids),
                "router_downstream_declared": sorted(dag.task_dict["router"].downstream_task_ids),
                "join_trigger_rules": {
                    "join_all_success": str(dag.task_dict["join_all_success"].trigger_rule),
                    "join_none_failed_min_one_success":
                        str(dag.task_dict["join_none_failed_min_one_success"].trigger_rule),
                },
            }
            require_equal(observed_static, EXPECTED_STATIC)
            record["static"] = observed_static

            if args.mode in ("callable", "execution"):
                # Direct invocation of user code. This is not scheduler evidence:
                # it never touches a TaskInstance, a DAG run, or the dependency
                # graph's skip/trigger-rule machinery.
                callback_result = callback()
                if callback_result is None:
                    selected = []
                elif isinstance(callback_result, str):
                    selected = [callback_result]
                else:
                    selected = sorted(callback_result)
                observed_callable = {
                    "callback_result": callback_result if not isinstance(callback_result, list)
                        else sorted(callback_result),
                    "selected_targets_normalized": selected,
                }
                require_equal(observed_callable, EXPECTED_CALLABLE[args.case])
                record["callable"] = observed_callable

            if args.mode == "execution":
                run = dag.test(execution_date=datetime(2024, 1, 2, tzinfo=timezone.utc))
                execution = {"dag_state": run.state, "task_instances": sorted([
                    {"task_id": ti.task_id, "map_index": ti.map_index, "state": ti.state}
                    for ti in run.get_task_instances()], key=lambda ti: (ti["task_id"], ti["map_index"]))}
                require_equal(execution, EXPECTED_EXECUTION[args.case])
                record["execution"] = execution
            settings.dispose_orm()
        finally:
            os.chdir(previous)
    require_equal(Path(home).exists(), False)
    record["temporary_state_removed"] = True
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
