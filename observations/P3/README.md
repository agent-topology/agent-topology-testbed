# P3: grouping, roots, and convergence are not confirmed execution semantics

Question: what does a `TaskGroup` expose about membership and boundaries, how do
DAG roots/leaves differ from confirmed entry semantics, and does a two-source
convergence's trigger rule still apply once both sources sit inside a group —
using documented public APIs where available, and recording where they are not.

Historical baseline: [571e881e6d509b6e26ff8bf14b98e207d12e7ce9](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
These are new internal observations for
[issue #5](https://github.com/agent-topology/agent-topology-testbed/issues/5),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1),
blocked by and building on [P1](../P1/README.md) (issue #3). Historical findings,
transcripts, and gallery artifacts remain unchanged; see the correction appended to
[F3](../../findings/F3-opaque-subgraph/README.md#correction-p3).

## Minimal input

DAG `p3_grouping`: one predecessor **before**, a `TaskGroup` **g** containing two
parallel `EmptyOperator` members **g_a**, **g_b** (no dependency between them), a
convergence join **join** downstream of both, and one successor **after**:

```
before >> g            # g = TaskGroup("g"): g_a, g_b
g >> join              # join: trigger_rule=NONE_FAILED_MIN_ONE_SUCCESS
join >> after
```

`join`'s trigger rule is the same `none_failed_min_one_success` rule P1 already
tested for a two-source convergence (P1's `join_none_failed_min_one_success`).
This is deliberately not a new rule or a new case matrix: the question here is
whether grouping `g_a`/`g_b` inside a `TaskGroup` changes what P1 already
established about that rule, not whether the rule itself behaves differently.
No external input; fixed logical date 2024-01-02 UTC, one case.

## Evidence classes, kept separate

- **static** — DAG-level `task_ids` (qualified), `dependencies`, `roots`,
  `leaves`; task-level group membership (`task.task_group.group_id`); the DAG's
  top-level children split into nested-`TaskGroup` metadata versus executable
  task instances; the group's own boundary (`TaskGroup.upstream_task_ids` /
  `downstream_task_ids`) kept separate from the task-level edges it is derived
  from; the group's internal roots/leaves (`TaskGroup.get_roots()` /
  `get_leaves()`); and `join`'s declared trigger rule. None of it requires
  running the DAG.
- **execution** — `dag.test()` task-instance states and the run's final
  `dag_state`, for the single default-success case described above. This is
  scheduler-equivalent evidence (`dag.test()`, no scheduler/webserver process),
  and is used only to check whether `TaskGroup` membership itself perturbs
  scheduling across the group's boundary — not to re-derive P1's trigger-rule
  conclusions, which this probe reuses rather than retesting.

## Expected facts and task states (written before extraction)

Written as literal `EXPECTED_STATIC` / `EXPECTED_EXECUTION` constants in
[`probes/airflow/grouping.py`](../../probes/airflow/grouping.py) from the
documented and source-level semantics below, before the extraction logic ran:

- Qualified task IDs carry the group's `group_id` prefix
  (`g.g_a`, `g.g_b`) — documented at
  [dags.html#taskgroups](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#taskgroups):
  "child tasks/TaskGroups have their IDs prefixed with the `group_id` of their
  parent TaskGroup."
- Wiring a `TaskGroup` object directly with `>>` fans out to/from its internal
  roots/leaves — documented on the same page: "Dependency relationships can be
  applied across all tasks in a TaskGroup with the `>>` and `<<` operators."
  So `before >> g` becomes two task-level edges (`before → g.g_a`,
  `before → g.g_b`), and `g >> join` becomes two more (`g.g_a → join`,
  `g.g_b → join`) — the two-source convergence, produced by crossing the group
  boundary rather than declared directly between `g_a`/`g_b` and `join`.
- `before` is the DAG's only root, `after` its only leaf
  (`DAG.roots` / `DAG.leaves`, `airflow/models/dag.py:2350-2358` at the 2.10.5
  tag): nodes with no upstream/downstream edge, respectively. The source
  docstring itself calls roots "first to execute"; this probe does not treat
  that as confirmed by running the DAG — see Limitations.
- `g_a` and `g_b` are both the group's internal roots and its internal leaves
  (`TaskGroup.get_roots()` / `get_leaves()`,
  `airflow/utils/task_group.py:386,394`): each is "a task with no
  upstream/downstream dependency within the TaskGroup" per their docstrings,
  true here because the two members have no edge between them.
- `g`'s own boundary, read from the group object itself
  (`TaskGroup.upstream_task_ids` / `downstream_task_ids`,
  `airflow/utils/task_group.py:176-177`, populated by its internal
  `_update_group_deps`): `{before}` upstream, `{join}` downstream.
- Given both `g_a` and `g_b` succeed, `join` (`none_failed_min_one_success`)
  runs — the same outcome P1's `multiple` case already established for two
  succeeding sources feeding that rule, now with both sources inside a group
  rather than as ungrouped siblings.

All predictions matched the corresponding observation on first run, twice, with
no expected-value correction needed.

## Observed results

Each evidence class (`static`, `execution`) ran twice; each pair's normalized
JSON is byte-identical (`cmp` exit 0). All commands exited zero;
`require_equal` raises `AssertionError` (nonzero exit) on any mismatch, verified
with a deliberate corrupted-expectation run under `python -O`.

| Evidence | Run 1 | Run 2 |
| --- | --- | --- |
| static | [run 1](grouping-static-1.json) | [run 2](grouping-static-2.json) |
| execution | [run 1](grouping-1.json) | [run 2](grouping-2.json) |

### Group metadata versus executable task instances

`dag.task_group.children` at the DAG's top level has four entries: `before`,
`g`, `join`, `after`. Splitting them by `hasattr(child, "children")` — the same
idiom `probes/airflow/airflow_probe.py` already uses to list task groups —
separates the one nested `TaskGroup` object (`g`, which carries no task state
of its own) from the three executable task instances. `g.g_a` and `g.g_b` do
not appear at this level at all; they are reached only through `g.children`,
keyed by their qualified IDs. Group membership and task-instance identity are
two different kinds of fact, read from two different attributes
(`task.task_group.group_id` for "which group is this task in", versus
`dag.task_group.children` / `TaskGroup.children` for "what is directly inside
this container"), and this probe keeps them in separate record fields rather
than inferring one from the other.

### Roots as a structural fact, not confirmed entry semantics

`before` is recorded as the DAG's only root because it is the only task with no
upstream edge in *this* DAG — a fact about the edge set constructed above, nothing
more. The one-root shape of this DAG cannot test whether multiple roots execute
in any particular relative order, or whether `DAG.roots`' own docstring
("first to execute") holds when there is more than one; P1 and P0 do not test
this either, and it is out of scope here (the epic's dependency boundaries are
P0→P1→P3, not a new root-ordering suite). Nor does root membership say anything
about what, if anything, outside this DAG definition could have caused `before`
to run — a sensor, an external trigger, or a dataset-aware schedule are all
invisible to this structural query and are not exercised by `dag.test()`. This
caution mirrors [F2](../../findings/README.md#f2--entrynodeids-conflates-a-graph-entry-with-a-node-that-lost-its-predecessor),
where `agent-topology`'s own `entryNodeIds` was found to conflate "this is where
the graph starts" with "the producer could not see what points here" — the same
conflation this probe declines to make for Airflow's `roots`.

### The boundary-crossing convergence

`g.g_a → join` and `g.g_b → join` exist as ordinary task-level edges, exactly
like P1's `[a, b] >> join_none_failed_min_one_success` — the fact that `g_a` and
`g_b` sit inside `g` added a `group_id` prefix to their IDs and registered `g`
as upstream of `join` at the group level, but did not add, remove, or alter any
edge or trigger-rule evaluation. The `execution` record confirms this for the
succeed/succeed case: `dag_state: success`, every task instance `success`,
matching P1's `multiple` outcome for the same rule. This probe does not repeat
P1's `single`/`none` cases, because the question here is whether grouping
changes that behavior (it does not, on this evidence), not whether the rule
itself has more than one outcome (P1 already answered that).

## Provenance and reproduction

Verified with CPython 3.11.16, uv 0.12.10, macOS arm64; Airflow 2.10.5 (137
locked distributions), same environment and lock as [P0](../P0/README.md) and
[P1](../P1/README.md). Each JSON records the framework/Python versions and
SHA-256 hashes of the grouping-probe source and dependency lock at run time.
Commands:

```sh
mkdir -p .probe-runs
for mode in static execution; do
  for n in 1 2; do
    .venvs/airflow/bin/python probes/airflow/grouping.py \
      --mode "$mode" --output ".probe-runs/grouping-$([ "$mode" = execution ] && echo "" || echo "$mode-")$n.json"
  done
done
cmp .probe-runs/grouping-static-1.json .probe-runs/grouping-static-2.json
cmp .probe-runs/grouping-1.json .probe-runs/grouping-2.json
```

- [`DAG.roots` / `DAG.leaves`, 2.10.5 source](https://github.com/apache/airflow/blob/2.10.5/airflow/models/dag.py#L2350-L2358)
- [`TaskGroup` 2.10.5 source](https://github.com/apache/airflow/blob/2.10.5/airflow/utils/task_group.py)
  (`get_roots`/`get_leaves` at lines 386/394; `upstream_task_ids`/
  `downstream_task_ids` initialized at lines 176-177)
- [`DependencyMixin` / `DAGNode` 2.10.5 source](https://github.com/apache/airflow/blob/2.10.5/airflow/models/taskmixin.py)
  (`upstream_task_ids`/`downstream_task_ids` declared at lines 173-174)
- [TaskGroups, 2.10.5 docs](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#taskgroups)
- [Trigger rules, 2.10.5 docs](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#trigger-rules)
  (reused from [P1](../P1/README.md), not re-derived here)

## Public-API gaps

The `dags.html` concept page documents `group_id` prefixing of qualified task
IDs and wiring a `TaskGroup` with `>>`/`<<`, and separately documents trigger
rules — but it documents none of the following, which this probe instead reads
directly from source, as cited above:

- `DAG.roots` / `DAG.leaves` are not mentioned anywhere on that page.
- No method for reading a `TaskGroup`'s own internal roots/leaves
  (`get_roots()`/`get_leaves()`) is documented in prose.
- No documented way to read a single task's own group membership
  (`task.task_group.group_id`); it is inferred here, not asserted to be the
  only way to ask the question.
- No documented way to read a `TaskGroup`'s own boundary
  (`upstream_task_ids`/`downstream_task_ids`) as distinct from recomputing it
  from the task-level dependency list; both are recorded separately here
  specifically to check they agree, not assuming they must.
- `TaskGroup.children` (for separating a nested group from an executable task
  among a container's direct children) is likewise undocumented in prose; this
  probe reuses the `hasattr(child, "children")` idiom already present in
  `probes/airflow/airflow_probe.py` rather than introducing a second way to ask
  the same question.

None of the above is a private or underscore-prefixed API; all are ordinary
public attributes/methods on `DAG` and `TaskGroup`. The gap is in the prose
documentation's coverage, not in API visibility — recorded as a limitation of
what a consumer can learn without reading source, not as evidence that the
facts are unavailable.

## Normalization and limitations

JSON sorts task IDs, dependency tuples, and task-instance identities; it does
not deduplicate. Task/DAG states and map index (`-1`, unmapped) are retained.
Wall timestamps, generated run IDs, durations, PIDs, log text, and temporary
paths stay outside the comparison. Logical execution date is fixed input.

**What this does and does not show.** This shows one `TaskGroup` with two
parallel members, one predecessor, one successor, and one two-source
convergence, on `dag.test()` with `SequentialExecutor` against Airflow 2.10.5 —
not a general rule about nested `TaskGroup`s (a group containing another group
is untested), nested dependencies between group members (the two members here
have no edge between them, so `get_roots()`/`get_leaves()` returning the same
two tasks is specific to this shape and not evidence either method behaves the
same when members are chained), dynamic task mapping inside a group, every
trigger rule (only `none_failed_min_one_success` is exercised, reused from
P1), or another Airflow version. `dag.test()` with `SequentialExecutor` runs
task instances serially in one process; nothing here demonstrates or measures
wall-clock concurrency between `g_a` and `g_b`. No `agent-topology` document is
produced, no schema or wire-format extension is proposed, and no upstream
decision is made. In particular, nothing here establishes that an Airflow
`TaskGroup` is equivalent to an opaque executable subgraph in the sense
`agent-topology`'s `subgraphId`/depth-gating raises — see the correction
appended to [F3](../../findings/F3-opaque-subgraph/README.md#correction-p3)
for why grouping and opaque-subgraph containment are not the same claim.
