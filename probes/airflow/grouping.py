"""P3-airflow-grouping: one TaskGroup with two tasks, a predecessor and
successor crossing its boundary, and a two-source convergence join that
reuses the trigger rule already tested by P1.

Answers two questions, kept in separate record sections so one is never
presented as evidence for the other:

  static    - what the DAG and the TaskGroup declare: task-group membership,
              qualified task IDs, dependencies crossing the group boundary
              (at both the task level and the TaskGroup's own
              upstream_task_ids/downstream_task_ids), DAG-level roots/leaves,
              the group's internal roots/leaves, and the declared join
              trigger rule. None of it requires running the DAG.
  execution - dag.test() task-instance states for a single default-success
              run. This does not retest P1's trigger-rule conclusions (see
              observations/P1/README.md): it only checks whether TaskGroup
              membership itself changes scheduling across the boundary, so
              one case suffices instead of P1's single/multiple/none matrix.

    pip install "apache-airflow==2.10.5"
    python grouping.py --mode execution --output out.json
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

# Expectations are literal and written from documented TaskGroup/DAG
# semantics before the extraction logic below ran against a real DAG:
#
#   - group_id prefixing of child task IDs is documented at
#     https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#taskgroups
#     ("child tasks/TaskGroups have their IDs prefixed with the group_id of
#     their parent TaskGroup").
#   - wiring a TaskGroup object directly with >> is documented on the same
#     page ("Dependency relationships can be applied across all tasks in a
#     TaskGroup with the >> and << operators").
#   - DAG.roots / DAG.leaves (airflow/models/dag.py:2350-2358 at the 2.10.5
#     tag) and TaskGroup.get_roots() / get_leaves()
#     (airflow/utils/task_group.py:386,394) are not covered by that prose
#     page at all; nor is TaskGroup.upstream_task_ids / downstream_task_ids
#     (airflow/utils/task_group.py:176-177, populated by _update_group_deps),
#     nor task.task_group.group_id for reading a task's own membership, nor
#     TaskGroup.children (airflow/utils/task_group.py:157) for distinguishing
#     a nested TaskGroup from an executable task among a group's children.
#     These are read from the TaskGroup source directly, not documented
#     prose; recorded as a public-API gap, not assumed absent.
#   - the join's trigger rule is NONE_FAILED_MIN_ONE_SUCCESS, the same rule
#     P1 (observations/P1/README.md) already tested for a two-source
#     convergence: with both sources successful, P1's "multiple" case found
#     the join runs. This probe does not re-derive that; it only checks the
#     rule still applies when both sources sit inside a TaskGroup crossing
#     out to the join, not as two ungrouped sibling tasks.

EXPECTED_STATIC = {
    "dag_id": "p3_grouping",
    "task_ids": ["after", "before", "g.g_a", "g.g_b", "join"],
    "dependencies": [
        ["before", "g.g_a"], ["before", "g.g_b"],
        ["g.g_a", "join"], ["g.g_b", "join"],
        ["join", "after"],
    ],
    # DAG.roots/leaves: structural facts about missing upstream/downstream
    # edges in this DAG. Not a claim about execution order or about what, if
    # anything, external to this DAG could trigger "before" -- see P3's
    # observations README for why root membership is not entry semantics.
    "roots": ["before"],
    "leaves": ["after"],
    # Group metadata (task_group.group_id) read per task, distinguishing
    # members of "g" from the three tasks outside any group.
    "group_membership": {"g": ["g.g_a", "g.g_b"]},
    # Top-level children of the DAG's root TaskGroup, split by whether each
    # child is itself a nested TaskGroup (has .children, carries no task
    # state of its own) or an executable task instance -- same idiom as
    # probes/airflow/airflow_probe.py's has_branch_operator check, applied to
    # hasattr(child, "children") instead.
    "top_level_children": {"group": ["g"], "task": ["after", "before", "join"]},
    # The TaskGroup's own boundary: which task IDs outside "g" it declares
    # itself upstream/downstream of, read from the group object, not
    # recomputed from the task-level dependency list above.
    "group_boundary": {"g": {"upstream_task_ids": ["before"], "downstream_task_ids": ["join"]}},
    # The group's internal roots/leaves (TaskGroup.get_roots/get_leaves):
    # both members are roots and leaves of "g" because they are parallel,
    # with no dependency between them.
    "group_internal_roots_leaves": {"g": {"roots": ["g.g_a", "g.g_b"], "leaves": ["g.g_a", "g.g_b"]}},
    "join_trigger_rule": "none_failed_min_one_success",
}

EXPECTED_EXECUTION = {
    "dag_state": "success",
    "task_instances": [
        {"task_id": "after", "map_index": -1, "state": "success"},
        {"task_id": "before", "map_index": -1, "state": "success"},
        {"task_id": "g.g_a", "map_index": -1, "state": "success"},
        {"task_id": "g.g_b", "map_index": -1, "state": "success"},
        {"task_id": "join", "map_index": -1, "state": "success"},
    ],
}


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
    record = {"case_id": "P3-airflow-grouping", "python": platform.python_version(),
              "framework": "apache-airflow", "version": "2.10.5",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "lock_sha256": hashlib.sha256(source.with_name("requirements.lock").read_bytes()).hexdigest(),
              "evidence_class": args.mode}
    # This command is process-scoped: never import Airflow before isolation.
    for key in list(os.environ):
        if key.startswith("AIRFLOW"):
            del os.environ[key]
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="p3-airflow-") as home:
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
            from airflow.utils.task_group import TaskGroup
            from airflow.utils.trigger_rule import TriggerRule
            from datetime import datetime, timezone

            with DAG("p3_grouping", start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                     schedule=None, catchup=False) as dag:
                before = EmptyOperator(task_id="before")
                with TaskGroup("g") as g:
                    g_a = EmptyOperator(task_id="g_a")
                    g_b = EmptyOperator(task_id="g_b")
                join = EmptyOperator(task_id="join", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
                after = EmptyOperator(task_id="after")
                before >> g
                g >> join
                join >> after

            group_children = {
                kind: sorted(name for name, child in dag.task_group.children.items()
                    if hasattr(child, "children") == (kind == "group"))
                for kind in ("group", "task")
            }
            group_membership: dict[str, list[str]] = {}
            for task in dag.tasks:
                group_id = task.task_group.group_id if task.task_group is not None else None
                if group_id is not None:
                    group_membership.setdefault(group_id, []).append(task.task_id)
            for members in group_membership.values():
                members.sort()

            observed_static = {
                "dag_id": dag.dag_id,
                "task_ids": sorted(dag.task_ids),
                "dependencies": sorted([task.task_id, downstream]
                    for task in dag.tasks for downstream in task.downstream_task_ids),
                "roots": sorted(t.task_id for t in dag.roots),
                "leaves": sorted(t.task_id for t in dag.leaves),
                "group_membership": group_membership,
                "top_level_children": group_children,
                "group_boundary": {
                    "g": {
                        "upstream_task_ids": sorted(g.upstream_task_ids),
                        "downstream_task_ids": sorted(g.downstream_task_ids),
                    },
                },
                "group_internal_roots_leaves": {
                    "g": {
                        "roots": sorted(t.task_id for t in g.get_roots()),
                        "leaves": sorted(t.task_id for t in g.get_leaves()),
                    },
                },
                "join_trigger_rule": str(dag.task_dict["join"].trigger_rule),
            }
            require_equal(observed_static, EXPECTED_STATIC)
            record["static"] = observed_static

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
