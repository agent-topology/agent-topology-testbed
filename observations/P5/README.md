# P5: Airflow mapped-task definitions are not runtime instances

Question: which dynamic-mapping facts exist in the DAG definition, and which
appear only after runtime expansion — using one source, one dynamically mapped
task, and one downstream aggregation, over input cardinalities 0, 1, and 2.

Historical baseline: [571e881e6d509b6e26ff8bf14b98e207d12e7ce9](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
These are new internal observations for
[issue #7](https://github.com/agent-topology/agent-topology-testbed/issues/7),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1),
blocked by [P3](../P3/README.md) (issue #5) per the epic's P0→P1→P3→P5
sequencing. The dynamic-mapping question below does not build on P3's
grouping content; it instead reuses the trigger-rule evidence [P1](../P1/README.md)
(issue #3) already established, the same way P3 did. Historical findings,
transcripts, and gallery artifacts remain unchanged.

## Minimal input

DAG `p5_mapped`: one TaskFlow source, one TaskFlow task mapped over the
source's output, and two downstream aggregations with different trigger
rules, run once per cardinality:

```
source() -> mapped.expand(x=source())
mapped -> aggregate_all_success                 (trigger_rule=ALL_SUCCESS)
mapped -> aggregate_none_failed_min_one_success  (trigger_rule=NONE_FAILED_MIN_ONE_SUCCESS)
```

`source`'s return value is hardcoded per case rather than external input:
`[]` (cardinality 0), `[10]` (cardinality 1), `[10, 20]` (cardinality 2). No
external input; fixed logical date 2024-01-02 UTC, three cases. Two
aggregations with different trigger rules are used, not one, because whether
aggregation behavior depends on the trigger rule is itself part of the
question — reusing the same two rules P1 already tested for a two-source
convergence (`all_success`, `none_failed_min_one_success`), applied here to a
mapped upstream instead of two fixed siblings.

## Evidence classes, kept separate

- **static** — `dag.task_ids`, task-level `dependencies`, whether the
  "mapped" and "source" tasks are `MappedOperator` instances
  (`isinstance(task, MappedOperator)`), and each aggregation's declared
  trigger rule. None of it requires running the DAG, and none of it depends
  on the cardinality case: the DAG definition names one mapped task
  consuming `source`'s XCom, not any particular number of expanded
  instances. This probe does not read an expansion length, a map count, or
  any per-index fact from the definition — there is no such fact to read
  before the DAG runs (see Limitations).
- **execution** — `dag.test()` task-instance states, map indexes, and the
  run's final `dag_state`, one run per cardinality (0, 1, 2). This is the
  only evidence class that shows how many mapped instances actually exist,
  what state each carries, and what each aggregation does with them.

## Expected facts and task states (written before extraction)

Written as literal `EXPECTED_STATIC` / `EXPECTED_EXECUTION` constants in
[`probes/airflow/mapped.py`](../../probes/airflow/mapped.py) from the
documented 2.10.5 semantics below, before the extraction logic ran:

- Dynamic task mapping, [2.10.5 docs](https://airflow.apache.org/docs/apache-airflow/2.10.5/authoring-and-scheduling/dynamic-task-mapping.html):
  "If the input is empty (zero length), no new tasks will be created and the
  mapped task will be marked as skipped." This is read here as one
  representative task instance for "mapped" at `map_index -1` in the
  cardinality-0 case, since `dag.test()` returns exactly one task-instance
  row per declared task even when its expand input is empty; the cited page
  itself does not state the map index that instance carries (see
  Public-API gaps).
- Trigger rules, [2.10.5 docs](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#trigger-rules),
  reused from [P1](../P1/README.md) rather than re-derived: `all_success`
  skips if any upstream was skipped; `none_failed_min_one_success` runs if no
  upstream failed and at least one upstream succeeded, and skips otherwise.
  Both rules are predicted to read a mapped upstream's instances
  collectively rather than per-index: cardinality 0 leaves the sole
  "mapped" instance skipped (not failed, zero succeeded), so both
  aggregations were predicted to skip; cardinalities 1 and 2 leave every
  "mapped" instance successful, so both aggregations were predicted to run.

All predictions matched the corresponding observation on first run, twice,
with no expected-value correction needed.

## Observed results

Each evidence class (`static`, `execution`) ran twice per cardinality; each
pair's normalized JSON is byte-identical (`cmp` exit 0). All commands exited
zero; `require_equal` raises `AssertionError` (nonzero exit) on any
mismatch, verified with a deliberate corrupted-expectation run under
`python -O` against the cardinality-0 case.

| Cardinality | static | execution |
| --- | --- | --- |
| 0 | [run 1](mapped-0-static-1.json) / [run 2](mapped-0-static-2.json) | [run 1](mapped-0-1.json) / [run 2](mapped-0-2.json) |
| 1 | [run 1](mapped-1-static-1.json) / [run 2](mapped-1-static-2.json) | [run 1](mapped-1-1.json) / [run 2](mapped-1-2.json) |
| 2 | [run 1](mapped-2-static-1.json) / [run 2](mapped-2-static-2.json) | [run 1](mapped-2-1.json) / [run 2](mapped-2-2.json) |

### Definition identity versus runtime instance identity

Every static record is identical across all three cardinalities: `task_ids`
names "mapped" exactly once, `dependencies` records one edge from `source`
to `mapped`, and `mapped_task_is_mapped_operator` is `true` regardless of how
many instances that task later expands into. The definition carries no
count, no per-index identity, and no cardinality — those exist only in the
`execution` record, which is where `map_index` first appears:

- Cardinality 0: `mapped` has exactly one task-instance row, `map_index -1`,
  `state skipped`. Airflow's own run log names this directly:
  `Marking <TaskInstance: p5_mapped.mapped ...> as SKIPPED since the map has
  0 values to expand`.
- Cardinality 1: `mapped` has exactly one task-instance row, `map_index 0`,
  `state success`.
- Cardinality 2: `mapped` has exactly two task-instance rows, `map_index 0`
  and `map_index 1`, both `state success` — two distinct runtime identities
  sharing one task ID, retained as separate rows rather than merged or
  deduplicated (see Normalization).

### Aggregation outcome depends on the trigger rule only through cardinality, not independently of it

At cardinality 0, `aggregate_all_success` and
`aggregate_none_failed_min_one_success` both skip — not because the two
rules agree in general, but because zero mapped instances means zero
successes, which both rules treat as "do not run" from opposite directions
(`all_success`: an upstream was skipped, so skip; `none_failed_min_one_success`:
no upstream succeeded, so skip). At cardinality 1 and 2, both aggregations
run, because every mapped instance succeeded and neither rule's skip
condition is met. This probe's two-rule, three-cardinality matrix did not
produce a case where the two rules diverge — unlike P1's `single` case, where
changing only the trigger rule changed whether the join ran. That divergence
is a property of *which* upstream tasks are skipped versus successful, not
of mapping specifically; nothing here should be read as a claim that
aggregation trigger rules never diverge under mapping, only that this
matrix did not exercise a mapped shape where they would (see Limitations).

## Provenance and reproduction

Verified with CPython 3.11.16, uv 0.12.10, macOS arm64; Airflow 2.10.5 (137
locked distributions), same environment and lock as [P0](../P0/README.md),
[P1](../P1/README.md), and [P3](../P3/README.md). Each JSON records the
framework/Python versions and SHA-256 hashes of the mapped-task probe source
and dependency lock at run time. Commands:

```sh
mkdir -p .probe-runs
for case in 0 1 2; do
  for n in 1 2; do
    .venvs/airflow/bin/python probes/airflow/mapped.py \
      --case "$case" --mode static --output ".probe-runs/mapped-$case-static-$n.json"
    .venvs/airflow/bin/python probes/airflow/mapped.py \
      --case "$case" --mode execution --output ".probe-runs/mapped-$case-$n.json"
  done
  cmp ".probe-runs/mapped-$case-static-1.json" ".probe-runs/mapped-$case-static-2.json"
  cmp ".probe-runs/mapped-$case-1.json" ".probe-runs/mapped-$case-2.json"
done
```

- [Dynamic task mapping, 2.10.5 docs](https://airflow.apache.org/docs/apache-airflow/2.10.5/authoring-and-scheduling/dynamic-task-mapping.html)
- [Trigger rules, 2.10.5 docs](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dags.html#trigger-rules)
  (reused from [P1](../P1/README.md), not re-derived here)
- [`MappedOperator` 2.10.5 source](https://github.com/apache/airflow/blob/2.10.5/airflow/models/mappedoperator.py)

## Public-API gaps

The dynamic-task-mapping page documents that an empty expand input produces
no new tasks and marks the mapped task skipped, but it does not document:

- What map index that one representative instance carries (`-1`, observed
  here, matching Airflow's convention for an unmapped/non-expanded task
  instance) — this probe reads it from the executed `TaskInstance`, not
  from prose.
- That a mapped upstream's map indexes are read collectively by a
  downstream task's trigger rule, rather than requiring the downstream task
  itself to be mapped or to iterate indexes explicitly — this is inferred
  from the observed `execution` outcomes across all three cardinalities, not
  asserted from documented prose.
- `MappedOperator` as the type distinguishing a mapped task definition from
  an ordinary one; this probe reads it from `airflow.models.mappedoperator`
  directly, an ordinary public class, not a private or underscore-prefixed
  API, but not one the concept pages name.

## Normalization and limitations

JSON sorts task IDs, dependency tuples, and task-instance identities by
`(task_id, map_index)`; it does not deduplicate. Map indexes and states are
retained exactly as returned, including the two distinct `map_index` rows
for "mapped" at cardinality 2. Wall timestamps, generated run IDs, durations,
PIDs, log text, and temporary paths stay outside the comparison. Logical
execution date is fixed input.

**What this does and does not show.** This shows one TaskFlow-mapped task
over a hardcoded, definition-time-unknowable cardinality of 0, 1, or 2, and
two downstream aggregations, on `dag.test()` with `SequentialExecutor`
against Airflow 2.10.5 — not a general rule about larger fan-outs (cardinality
above 2 is untested and out of scope, per the issue's non-goals), nested or
grouped mapped tasks (P3's `TaskGroup` findings are not retested here against
a mapped member), a mapped task that itself fails for some indexes and
succeeds for others (every instance here either all succeeds or does not
exist), `map_index_template` custom naming, classic-operator `.partial()`/
`.expand()` mapping (this probe uses TaskFlow's `@task`, not the classic
operator form), or another Airflow version. `dag.test()` with
`SequentialExecutor` runs task instances serially in one process; nothing
here demonstrates or measures wall-clock concurrency between the two
mapped instances at cardinality 2. No `agent-topology` document is produced,
no schema or wire-format extension is proposed, and no upstream decision is
made. In particular, this probe does not infer a generic "join contract" for
mapped-task aggregation from a matrix where the two trigger rules happened
to agree at every cardinality tested — see the previous section.

## Claim disposition

The [completed-cohort ledger](../../findings/completed-cohort-dispositions.md#p5)
classifies this observation’s material claims, their finding links or reasons for
non-promotion, and any specific minimal follow-up. Raw evidence remains unchanged.
