"""P0-airflow-linear: two tasks, static dependencies and dag.test evidence."""
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

# Expectations are literal and independent of extraction.
EXPECTED_STATIC = {"dag_id": "p0_linear", "task_ids": ["first", "second"],
                   "dependencies": [["first", "second"]]}
EXPECTED_EXECUTION = {"dag_state": "success", "task_instances": [
    {"task_id": "first", "map_index": -1, "state": "success"},
    {"task_id": "second", "map_index": -1, "state": "success"}]}


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
    require_equal(importlib.metadata.version("apache-airflow"), "2.10.5")
    record = {"case_id": "P0-airflow-linear", "python": platform.python_version(),
              "framework": "apache-airflow", "version": "2.10.5",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
              "evidence_class": args.mode}
    # This command is process-scoped: never import Airflow before isolation.
    for key in list(os.environ):
        if key.startswith("AIRFLOW"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p0-airflow-") as home:
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
            from datetime import datetime, timezone
            with DAG("p0_linear", start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                     schedule=None, catchup=False) as dag:
                first = EmptyOperator(task_id="first")
                second = EmptyOperator(task_id="second")
                first >> second
            observed = {"dag_id": dag.dag_id, "task_ids": sorted(dag.task_ids),
                        "dependencies": sorted([task.task_id, downstream]
                            for task in dag.tasks for downstream in task.downstream_task_ids)}
            require_equal(observed, EXPECTED_STATIC)
            record["static"] = observed
            if args.mode == "execution":
                run = dag.test(execution_date=datetime(2024, 1, 2, tzinfo=timezone.utc))
                execution = {"dag_state": run.state, "task_instances": sorted([
                    {"task_id": ti.task_id, "map_index": ti.map_index, "state": ti.state}
                    for ti in run.get_task_instances()], key=lambda ti: (ti["task_id"], ti["map_index"]))}
                require_equal(execution, EXPECTED_EXECUTION)
                record["execution"] = execution
            settings.dispose_orm()
        finally:
            os.chdir(previous)
    require_equal(Path(home).exists(), False)
    record["temporary_state_removed"] = True
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
