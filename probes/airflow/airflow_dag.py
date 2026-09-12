import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.task_group import TaskGroup

with DAG("demo", start_date=datetime.datetime(2024, 1, 1), schedule=None) as dag:
    start = EmptyOperator(task_id="start")

    # An ordinary operator's downstream edges do not by themselves say how
    # many of these run or whether they run simultaneously; see P1
    # (observations/P1/) for execution evidence on that question.
    fork = EmptyOperator(task_id="fork")
    left = EmptyOperator(task_id="left")
    right = EmptyOperator(task_id="right")
    joined = EmptyOperator(task_id="joined")

    # A BranchPythonOperator selects among its downstream tasks via its
    # callback. The callback here always returns "a"; that is a fact about
    # this callback, not a guarantee that BranchPythonOperator callbacks
    # always select exactly one target — see the P1 correction linked from
    # findings/F1-fan-out-semantics for a counterexample.
    router = BranchPythonOperator(task_id="router", python_callable=lambda: "a")
    a = EmptyOperator(task_id="a")
    b = EmptyOperator(task_id="b")

    with TaskGroup("nested") as nested:
        EmptyOperator(task_id="inner1") >> EmptyOperator(task_id="inner2")

    end = EmptyOperator(task_id="end")

    start >> fork >> [left, right] >> joined >> router >> [a, b]
    [a, b] >> nested >> end
