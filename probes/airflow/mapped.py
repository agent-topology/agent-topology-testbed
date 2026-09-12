"""P5-airflow-mapped: one source, one dynamically mapped task, and two
downstream aggregations with different trigger rules, over input
cardinalities 0, 1, and 2.

Answers two questions, kept in separate record sections so one is never
presented as evidence for the other:

  static    - what the DAG declares: task IDs, dependencies, which task is a
              MappedOperator, and each aggregation's trigger rule. This is
              the same for every cardinality: the DAG definition names one
              mapped task consuming "source"'s XCom, not any particular
              number of expanded instances -- how many instances that
              produces is a runtime fact this probe does not claim to read
              from the definition. None of it requires running the DAG.
  execution - dag.test() task-instance states, map indexes, and the two
              aggregations' outcomes for a fixed logical date, one run per
              cardinality. This is the only section that reflects the
              scheduler's zero-length-expand and trigger-rule behavior.

    pip install "apache-airflow==2.10.5"
    python mapped.py --case 1 --mode execution --output out.json
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

# Expectations are literal and written per case, before the extraction logic
# below ran against a real DAG. They are predictions from the documented
# 2.10.5 dynamic-task-mapping and trigger-rule semantics, not values copied
# from a prior run:
#
#   https://airflow.apache.org/docs/apache-airflow/2.10.5/authoring-and-scheduling/dynamic-task-mapping.html
#   "If the input is empty (zero length), no new tasks will be created and
#   the mapped task will be marked as skipped." -- read here as one
#   representative task instance at map_index -1, since dag.test() always
#   returns exactly one TaskInstance row per declared task even when its
#   expand input is empty; this probe records that reading as an observation,
#   not as prose the cited page states directly (see README limitations).
#
#   https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#trigger-rules
#   all_success                 - skipped if any upstream was skipped.
#   none_failed_min_one_success - runs if no upstream failed and at least one
#                                 upstream succeeded; skipped otherwise.
#   Both rules read a mapped upstream's map indexes collectively: cardinality
#   0 leaves the sole "mapped" instance skipped (not failed, zero succeeded),
#   so both aggregations skip; cardinality 1 and 2 leave every "mapped"
#   instance successful, so both aggregations run.

CASE_INPUTS = {
    "0": [],
    "1": [10],
    "2": [10, 20],
}

# Case-independent: the DAG's wiring, which task is mapped, and each
# aggregation's trigger rule do not depend on how many elements "source"
# returns -- that count is a runtime fact of expansion, not a definition-time
# fact this section claims to know.
EXPECTED_STATIC = {
    "dag_id": "p5_mapped",
    "task_ids": ["aggregate_all_success", "aggregate_none_failed_min_one_success", "mapped", "source"],
    "dependencies": [
        ["mapped", "aggregate_all_success"], ["mapped", "aggregate_none_failed_min_one_success"],
        ["source", "mapped"],
    ],
    "mapped_task_is_mapped_operator": True,
    "source_task_is_mapped_operator": False,
    "aggregate_trigger_rules": {
        "aggregate_all_success": "all_success",
        "aggregate_none_failed_min_one_success": "none_failed_min_one_success",
    },
}

EXPECTED_EXECUTION = {
    "0": {
        "dag_state": "success",
        "task_instances": [
            {"task_id": "aggregate_all_success", "map_index": -1, "state": "skipped"},
            {"task_id": "aggregate_none_failed_min_one_success", "map_index": -1, "state": "skipped"},
            {"task_id": "mapped", "map_index": -1, "state": "skipped"},
            {"task_id": "source", "map_index": -1, "state": "success"},
        ],
    },
    "1": {
        "dag_state": "success",
        "task_instances": [
            {"task_id": "aggregate_all_success", "map_index": -1, "state": "success"},
            {"task_id": "aggregate_none_failed_min_one_success", "map_index": -1, "state": "success"},
            {"task_id": "mapped", "map_index": 0, "state": "success"},
            {"task_id": "source", "map_index": -1, "state": "success"},
        ],
    },
    "2": {
        "dag_state": "success",
        "task_instances": [
            {"task_id": "aggregate_all_success", "map_index": -1, "state": "success"},
            {"task_id": "aggregate_none_failed_min_one_success", "map_index": -1, "state": "success"},
            {"task_id": "mapped", "map_index": 0, "state": "success"},
            {"task_id": "mapped", "map_index": 1, "state": "success"},
            {"task_id": "source", "map_index": -1, "state": "success"},
        ],
    },
}


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"observation mismatch: {actual!r} != {expected!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=tuple(CASE_INPUTS), required=True)
    parser.add_argument("--mode", choices=("static", "execution"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    source_file = Path(__file__).resolve()
    require_equal(platform.python_version(), "3.11.16")
    require_equal(importlib.metadata.version("apache-airflow"), "2.10.5")
    record = {"case_id": f"P5-airflow-mapped-{args.case}", "python": platform.python_version(),
              "framework": "apache-airflow", "version": "2.10.5",
              "source_sha256": hashlib.sha256(source_file.read_bytes()).hexdigest(),
              "lock_sha256": hashlib.sha256(source_file.with_name("requirements.lock").read_bytes()).hexdigest(),
              "evidence_class": args.mode}
    # This command is process-scoped: never import Airflow before isolation.
    for key in list(os.environ):
        if key.startswith("AIRFLOW"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p5-airflow-") as home:
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
            from airflow.decorators import task
            from airflow.models.mappedoperator import MappedOperator
            from airflow.operators.empty import EmptyOperator
            from airflow.utils.trigger_rule import TriggerRule
            from datetime import datetime, timezone

            case_input = CASE_INPUTS[args.case]
            with DAG("p5_mapped", start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                     schedule=None, catchup=False) as dag:
                @task
                def source():
                    return case_input

                @task
                def mapped(x):
                    return x

                aggregate_all = EmptyOperator(
                    task_id="aggregate_all_success", trigger_rule=TriggerRule.ALL_SUCCESS)
                aggregate_min1 = EmptyOperator(
                    task_id="aggregate_none_failed_min_one_success",
                    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
                )
                mapped_output = mapped.expand(x=source())
                mapped_output >> aggregate_all
                mapped_output >> aggregate_min1

            observed_static = {
                "dag_id": dag.dag_id,
                "task_ids": sorted(dag.task_ids),
                "dependencies": sorted([task_.task_id, downstream]
                    for task_ in dag.tasks for downstream in task_.downstream_task_ids),
                "mapped_task_is_mapped_operator": isinstance(dag.task_dict["mapped"], MappedOperator),
                "source_task_is_mapped_operator": isinstance(dag.task_dict["source"], MappedOperator),
                "aggregate_trigger_rules": {
                    "aggregate_all_success": str(dag.task_dict["aggregate_all_success"].trigger_rule),
                    "aggregate_none_failed_min_one_success":
                        str(dag.task_dict["aggregate_none_failed_min_one_success"].trigger_rule),
                },
            }
            require_equal(observed_static, EXPECTED_STATIC)
            record["static"] = observed_static

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
