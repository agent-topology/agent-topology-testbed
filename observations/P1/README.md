# P1: branch selection is not downstream execution

Question: for a `BranchPythonOperator` router with two destinations, which facts
about branch selection and downstream execution are visible statically, which
require invoking the callback directly, and which require executing the DAG —
and does changing only a join's trigger rule change what executes?

Historical baseline: [571e881e6d509b6e26ff8bf14b98e207d12e7ce9](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
These are new internal observations for
[issue #3](https://github.com/agent-topology/agent-topology-testbed/issues/3),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1),
blocked by and building on [P0](../P0/README.md) (issue #2). Historical findings,
transcripts, and gallery artifacts remain unchanged; see the correction appended to
[F1](../../findings/F1-fan-out-semantics/README.md#correction-p1).

## Minimal input

DAG `p1_branch`: `BranchPythonOperator` **router** with two `EmptyOperator`
destinations **a**, **b**, each feeding two joins on identical edges —
**join_all_success** (`trigger_rule=all_success`, Airflow's default) and
**join_none_failed_min_one_success** (`trigger_rule=none_failed_min_one_success`).
No external input; fixed logical date 2024-01-02 UTC. Three cases, differing only
in the router's hardcoded callback return value:

| Case | Callback returns | Selected targets |
| --- | --- | --- |
| `single` | `"a"` | `{a}` |
| `multiple` | `["a", "b"]` | `{a, b}` |
| `none` | `None` | `{}` |

## Evidence classes, kept separate

Each run records three sections, and no section is used as evidence for another:

- **static** — `dag_id`, `task_ids`, `dependencies`, `router`'s declared
  downstream (`router_downstream_declared`), and each join's declared
  `trigger_rule`. Identical across all three cases: none of it depends on what
  the callback returns.
- **callable** — the router's `python_callable` invoked directly, and its
  return value normalized into a target set (`selected_targets_normalized`).
  This is direct evaluation of user code. It is not scheduler evidence: it never
  constructs a `TaskInstance`, a `DagRun`, or touches trigger-rule dependency
  checks.
- **execution** — `dag.test()` task-instance states and the run's final
  `dag_state`. This is the only section produced by the scheduler-equivalent
  path (`dag.test()`, no scheduler/webserver process), and the only section that
  can show a task skipped versus run.

## Expected target sets and task states (written before extraction)

Written from the documented 2.10.5 trigger-rule semantics
([trigger rules](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#trigger-rules),
[`BranchMixIn.do_branch`](https://github.com/apache/airflow/blob/2.10.5/airflow/operators/python.py),
[`SkipMixin.skip_all_except`](https://github.com/apache/airflow/blob/2.10.5/airflow/models/skipmixin.py))
before the extraction logic in `probes/airflow/branch.py` was implemented, as
literal `EXPECTED_STATIC` / `EXPECTED_CALLABLE` / `EXPECTED_EXECUTION` constants
in the script:

| Case | `a` | `b` | `join_all_success` | `join_none_failed_min_one_success` | `router` | `dag_state` |
| --- | --- | --- | --- | --- | --- | --- |
| `single` | success | skipped | skipped | success | success | success |
| `multiple` | success | success | success | success | success | success |
| `none` | skipped | skipped | skipped | skipped | success | success |

All three predictions matched the corresponding `dag.test()` result on first
run, twice, with no expected-state correction needed.

## Observed results

Every case ran twice per evidence class (`static`, `callable`, `execution`); each
pair's normalized JSON is byte-identical (`cmp` exit 0). All commands exited
zero; `require_equal` raises `AssertionError` (nonzero exit) on any mismatch,
verified with a deliberate corrupted-expectation run under `python -O`.

| Case | Static | Callable | Execution |
| --- | --- | --- | --- |
| `single` | [run 1](branch-single-static-1.json), [run 2](branch-single-static-2.json) | [run 1](branch-single-callable-1.json), [run 2](branch-single-callable-2.json) | [run 1](branch-single-1.json), [run 2](branch-single-2.json) |
| `multiple` | [run 1](branch-multiple-static-1.json), [run 2](branch-multiple-static-2.json) | [run 1](branch-multiple-callable-1.json), [run 2](branch-multiple-callable-2.json) | [run 1](branch-multiple-1.json), [run 2](branch-multiple-2.json) |
| `none` | [run 1](branch-none-static-1.json), [run 2](branch-none-static-2.json) | [run 1](branch-none-callable-1.json), [run 2](branch-none-callable-2.json) | [run 1](branch-none-1.json), [run 2](branch-none-2.json) |

### The multiple-selection counterexample

`multiple` is a direct counterexample to "`BranchPythonOperator` fan-out is
exclusive": the callback selects two targets, and `dag.test()` shows both `a`
and `b` at `state: success`, not one selected and the other skipped. Branch
*selection* (what the callback returns), dependency *eligibility* (what a join's
trigger rule requires of its upstream states), and *execution* (what `dag.test()`
actually ran) are three different facts; an ordinary `router >> [a, b]` edge set
establishes none of them by itself, only that `a` and `b` are eligible to run if
selected and not skipped. See the linked [F1 correction](../../findings/F1-fan-out-semantics/README.md#correction-p1).

### The trigger-rule comparison

`single` is the case that exposes the trigger-rule difference, because it is the
only case where one destination succeeds and the other is skipped, with
identical upstream input to both joins:

- `join_all_success` (`all_success`): requires every upstream task instance to
  have succeeded. `b` is `skipped`, not `success`, so `join_all_success` is
  itself `skipped` — this is Airflow's skip-cascading behavior for the default
  trigger rule, not a failure.
- `join_none_failed_min_one_success` (`none_failed_min_one_success`): requires
  no upstream failure and at least one upstream success. `a` succeeded and
  nothing failed, so it runs (`success`), even though `b` was skipped.

Changing only the trigger rule, on the same edges and the same upstream states,
changes whether the join executes. In `multiple` both joins run (all upstream
succeeded); in `none` both joins are skipped (`join_none_failed_min_one_success`
requires *at least one* success, and neither `a` nor `b` ran).

## Provenance and reproduction

Verified with CPython 3.11.16, uv 0.12.10, macOS arm64; Airflow 2.10.5 (137
locked distributions), same environment and lock as [P0](../P0/README.md). Each
JSON records the framework/Python versions and SHA-256 hashes of the smoke
source and dependency lock at run time. Commands:

```sh
mkdir -p .probe-runs
for case in single multiple none; do
  for mode in static callable execution; do
    for n in 1 2; do
      .venvs/airflow/bin/python probes/airflow/branch.py \
        --case "$case" --mode "$mode" \
        --output ".probe-runs/branch-$case-$([ "$mode" = execution ] && echo "" || echo "$mode-")$n.json"
    done
  done
done
```

(The committed files use `branch-<case>-<n>.json` for `--mode execution`, which
also contains the `static` and `callable` sections, and `branch-<case>-static-<n>.json`
/ `branch-<case>-callable-<n>.json` for the corresponding standalone modes.)

- [`BranchPythonOperator` / `BranchMixIn` 2.10.5 source](https://github.com/apache/airflow/blob/2.10.5/airflow/operators/python.py)
- [`TriggerRule` 2.10.5 source](https://github.com/apache/airflow/blob/2.10.5/airflow/utils/trigger_rule.py)
- [`TriggerRuleDep` 2.10.5 source](https://github.com/apache/airflow/blob/2.10.5/airflow/ti_deps/deps/trigger_rule_dep.py)
- [Trigger rules, 2.10.5 docs](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#trigger-rules)

## Normalization and limitations

JSON sorts task IDs, dependency tuples, and task-instance identities; it does not
deduplicate. Task/DAG states and map index (`-1`, unmapped) are retained. Wall
timestamps, generated run IDs, durations, PIDs, log text, and temporary paths stay
outside the comparison. Logical execution date is fixed input.

**What this does and does not show.** This shows one router, one pair of
destinations, one pair of trigger rules, on `dag.test()` with `SequentialExecutor`
against Airflow 2.10.5 — not a general rule about every trigger rule (`one_success`,
`none_failed`, `all_done`, and others are untested), every operator (mapped
operators, dynamic task mapping, and `TaskGroup` branch targets are untested), or
another Airflow version. `dag.test()` with `SequentialExecutor` runs task
instances serially in one process; nothing here demonstrates or measures wall-clock
concurrency between `a` and `b` in the `multiple` case, only that both reach
`state: success` in the same run. The router's callback here is a hardcoded literal
per case, not a decision made from runtime data; this probe evaluates the
scheduler's response to a given return value, not arbitrary callback logic
(out of scope per the epic's non-goals). No `agent-topology` document is produced,
no schema or wire-format extension is proposed, and no upstream decision is made.
