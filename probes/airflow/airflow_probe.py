"""Evidence that a structurally different framework can populate the proposed
branch field, and that deriving it needs no infrastructure.

No scheduler, no webserver, no metadata database, no `airflow db init`.
The DAG file is imported to construct the object, exactly as `agt describe`
imports a Python target to resolve a compiled graph. Nothing is executed.

    pip install "apache-airflow==2.10.5"
    python airflow_probe.py
"""

import importlib.util
import os
import pathlib

os.environ.setdefault("AIRFLOW_HOME", str(pathlib.Path(__file__).parent / ".airflow"))

from airflow.operators.python import BranchPythonOperator  # noqa: E402


def load_dag(path: str, name: str = "dag"):
    spec = importlib.util.spec_from_file_location("dagmod", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, name)


def fan_out_mode(task) -> str | None:
    """Airflow distinguishes exclusive from concurrent fan-out natively.

    A branch operator selects among its downstream tasks. Every other operator
    runs all of them. That is exactly the distinction `agent-topology` 0.1
    cannot currently express.
    """
    if len(task.downstream_task_ids) < 2:
        return None
    return "exclusive" if isinstance(task, BranchPythonOperator) else "concurrent"


def main() -> None:
    dag = load_dag(str(pathlib.Path(__file__).parent / "airflow_dag.py"))

    print("dag id     :", dag.dag_id)
    print("roots      :", sorted(t.task_id for t in dag.roots))
    print("leaves     :", sorted(t.task_id for t in dag.leaves))
    print("task groups:", sorted(
        name for name, child in dag.task_group.children.items()
        if hasattr(child, "children")
    ))
    print()
    print(f"{'task':14} {'downstream':28} fan-out mode")
    for task_id in sorted(dag.task_dict):
        task = dag.task_dict[task_id]
        downstream = ",".join(sorted(task.downstream_task_ids))
        print(f"{task_id:14} {downstream[:27]:28} {fan_out_mode(task) or '-'}")


if __name__ == "__main__":
    main()
