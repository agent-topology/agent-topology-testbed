# Common question matrix (M1)

This section is the decision-oriented index over every probe's evidence; the
reproduction instructions below it are unchanged. It answers, per framework and
per question, *which unresolved framework facts would change a topology
contract recommendation or producer-candidate assessment* — see
[issue #12](https://github.com/agent-topology/agent-topology-testbed/issues/12)
and [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1).
It backfills existing P0–P6 evidence; it invents no new results and runs no new
experiments.

## Seven question IDs

| ID | Question |
| --- | --- |
| Q1 | Is the structure available without executing anything (static extractability)? |
| Q2 | Are nodes and edges explicit — enumerable identities, not inferred from naming or side channels? |
| Q3 | What do fan-out selection and downstream execution actually establish, separately? |
| Q4 | What do AND/OR-style convergence/join semantics actually establish, separately from declaring a policy? |
| Q5 | Is an opaque nested-graph boundary visible, and what does visibility of its membership/ports actually prove? |
| Q6 | Are interrupt/human-in-the-loop concepts structurally visible? |
| Q7 | Are definition-level identifiers stable across runs, separate from generated run IDs and mapped-instance IDs? |

These IDs are stable: a new probe cites them by number rather than restating the
question, and a cell that is not yet answered says **untested**, not "no" — see
[evidence conventions](../docs/evidence.md) on never inferring a negative result
from absent evidence.

A new probe should answer all seven questions for its framework, leaving cells
explicitly **untested** where they do not apply or were not exercised — it
should not grow into seven separate experiments. Each probe still has one
primary decision-changing experiment; the seven-question pass over its
existing evidence is a backfill against that experiment, not a mandate to
design seven new ones.

## Frameworks and programming models

| Framework | Exact version | Programming model |
| --- | --- | --- |
| Apache Airflow | 2.10.5 | Declarative DAG authored in Python (TaskFlow + classic operators); structure is fixed at parse time, independent of runtime data. |
| Dagster (ops/graphs) | 1.13.22 | Declarative `GraphDefinition`/`JobDefinition` composed from Python-decorated ops; structure is fixed at definition time. Assets and partitions are out of scope (epic non-goal). |
| CrewAI Flows | Untested here; version to be pinned and recorded in [#13](https://github.com/agent-topology/agent-topology-testbed/issues/13). | Python `@start`/`@listen`/`@router`-decorated flow methods; not yet probed. |
| Amazon States Language (ASL) | Untested here; spec revision to be recorded in [#14](https://github.com/agent-topology/agent-topology-testbed/issues/14). | Declarative JSON/YAML state-machine document, no SDK; interpreted by AWS Step Functions. Local parsing/structural checks are documentary evidence, not AWS validation or cloud execution. |
| Temporal (Python SDK) | Untested here; SDK version to be pinned and recorded in [#15](https://github.com/agent-topology/agent-topology-testbed/issues/15). | Imperative Python workflow code; per [F1's note](../findings/F1-fan-out-semantics/README.md#note-on-the-core-field-test), structure is not statically available without execution — this is itself a candidate-boundary fact, not an assumed impossibility. |
| Prefect 3 | Untested here; SDK version to be pinned and recorded in [#16](https://github.com/agent-topology/agent-topology-testbed/issues/16). | Python-decorated flows/tasks; structure is inferred from the decorated call graph versus runtime task invocation; not yet probed. |
| AutoGen SelectorGroupChat | Untested here; SDK version to be pinned and recorded in [#17](https://github.com/agent-topology/agent-topology-testbed/issues/17). | Python multi-agent group chat; a selector function chooses the next speaker at runtime, not from a pre-declared edge set. |
| AutoGen GraphFlow | Untested here; SDK version to be pinned and recorded in [#17](https://github.com/agent-topology/agent-topology-testbed/issues/17). | Python multi-agent flow over an explicitly constructed digraph of agents; a potential positive control against GroupChat-based negative claims. |

## Answer matrix

Legend: **support** = observed support, **limit** = observed limitation,
**partial** = both, scoped below, **untested** = no probe has answered this yet
for this framework, **n/a** = the question does not apply to this programming
model. No cell infers a negative from missing evidence.

| Framework | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Airflow | support | support | partial | partial | partial | untested | partial |
| Dagster | partial | partial | partial | partial | partial | untested | partial |
| CrewAI Flows | untested | untested | untested | untested | untested | untested | untested |
| ASL | untested | untested | untested | untested | untested | untested | untested |
| Temporal (Python) | untested | untested | untested | untested | untested | untested | untested |
| Prefect 3 | untested | untested | untested | untested | untested | untested | untested |
| AutoGen SelectorGroupChat | untested | untested | untested | untested | untested | untested | untested |
| AutoGen GraphFlow | untested | untested | untested | untested | untested | untested | untested |

### Q1 — structure available without execution

- **Airflow — support.** `dag_id`/`task_ids`/`dependencies` (and, per probe,
  trigger rules, group membership/boundary, `MappedOperator` flags) are read
  from the DAG object with no `dag.test()` call: [P0](../observations/P0/README.md)
  static section, [P1](../observations/P1/README.md#evidence-classes-kept-separate)
  static section, [P3](../observations/P3/README.md#evidence-classes-kept-separate)
  static section, [P5](../observations/P5/README.md#evidence-classes-kept-separate)
  static section.
- **Dagster — partial.** `job_name`/`op_names`/`dependencies` (and, per probe,
  `output_is_required`/`output_is_dynamic` flags) are read from
  `graph`/`OutputDefinition`s with no `execute_in_process()` call: [P0](../observations/P0/README.md),
  [P2](../observations/P2/README.md#evidence-classes-kept-separate),
  [P4](../observations/P4/README.md#api-coverage-and-bounded-unsupported-inspection),
  [P6](../observations/P6/README.md#evidence-classes-kept-separate). Native,
  source-visible extractability is supported; **complete documented-`@public`
  extractability is not** — P4 found `GraphDefinition.nodes` and
  `.dependencies` lack `@public` in the installed 1.13.22 source, so a producer
  restricted to documented-public accessors alone remains an open gap. This is
  the native-capability-versus-public-extractability distinction, not a claim
  that the structure is unavailable.

### Q2 — explicit nodes and edges

- **Airflow — support.** Same static sections as Q1 carry typed `task_ids` and
  `(upstream, downstream)` dependency tuples, sorted but not deduplicated, in
  every probe.
- **Dagster — partial.** Same static sections carry typed `op_names` and
  `[producer, output, consumer, input]` (and, for P6, `dependency_kind`)
  tuples. The added nuance: node identity is not definition identity.
  [P4](../observations/P4/README.md#comparison-and-claim-record) contradicts
  "reusing one child definition requires only one set of local node IDs" —
  two invocations (`left`, `right`) of the same `GraphDefinition` keep distinct
  invocation-scoped node identities, and an extractor that reads only the
  shared definition name loses them.

### Q3 — fan-out selection and execution semantics

- **Airflow — partial.** The router's declared downstream set and each join's
  trigger rule are static and symmetric across every callback outcome; they do
  not say which targets a given run selects. `python_callable` invoked
  directly (**callable** evidence) is not scheduler evidence either — it never
  builds a `TaskInstance` or evaluates a trigger-rule dependency. Only
  **execution** evidence (`dag.test()`) shows what actually ran versus
  skipped. The `multiple` case (callback returns `["a", "b"]`) is a direct
  counterexample to "`BranchPythonOperator` fan-out is exclusive," corrected
  into [F1](../findings/F1-fan-out-semantics/README.md#correction-p1). See
  [P1](../observations/P1/README.md).
- **Dagster — partial.** The analogous mechanism is `Out(is_required=False)`:
  the static `is_required` flag is symmetric across every case and does not
  say which outputs a given run emits; only **execution** evidence
  distinguishes `none`/`single`/`multiple` and shows which consumers were
  skipped. See [P2's claim record](../observations/P2/README.md#claim-record).

### Q4 — AND/OR convergence semantics

- **Airflow — partial.** A join's trigger rule (e.g. `all_success`,
  `none_failed_min_one_success`) is a static, declared policy — an AND-like
  versus OR-like requirement over upstream states — but whether the join
  actually runs still depends on execution evidence tied to which upstream
  states occurred: [P1](../observations/P1/README.md#the-trigger-rule-comparison).
  The same declared rule produces the same outcome pattern whether its
  sources are ungrouped siblings ([P1](../observations/P1/README.md)), inside
  a `TaskGroup` ([P3](../observations/P3/README.md#the-boundary-crossing-convergence)),
  or mapped-task instances ([P5](../observations/P5/README.md#aggregation-outcome-depends-on-the-trigger-rule-only-through-cardinality-not-independently-of-it)) —
  three shapes, not a claim that every trigger rule behaves identically in
  general.
- **Dagster — partial.** No probe here found an ops/graphs primitive with
  Airflow's multi-mode trigger-rule vocabulary. [P2](../observations/P2/README.md)'s
  optional-output skip-forwarding is the closest OR-like behavior found, and
  [P4](../observations/P4/README.md)'s `consume` op has two ordinary required
  inputs (implicit AND, untested to a failure/skip case). Per the epic's F7
  caution, **a missing join-mode property does not by itself prove an
  information gap** — this cell records what ops/graphs execution showed, not
  a completeness claim about Dagster overall (assets/sensors are out of scope
  here). The normative comparison this caution requires belongs to CrewAI's
  own AND/OR investigation ([#13](https://github.com/agent-topology/agent-topology-testbed/issues/13)),
  not to Dagster.

### Q5 — opaque nested-graph visibility and boundaries

- **Airflow — partial.** A `TaskGroup`'s membership, qualified task IDs, and
  its own boundary (`upstream_task_ids`/`downstream_task_ids`) are all
  discoverable through public attributes with no execution:
  [P3](../observations/P3/README.md). This is **not** equivalent to an opaque
  subgraph node in [F3](../findings/F3-opaque-subgraph/README.md)'s sense — a
  `TaskGroup` is a label on already-enumerable tasks, not a boundary node that
  can hide a graph, fail as a unit, or carry a `hasSubgraph` marker. See the
  [F3 correction](../findings/F3-opaque-subgraph/README.md#correction-p3).
  All of the attributes above are ordinary public, non-underscore APIs, but
  none of `DAG.roots`/`leaves`, `TaskGroup.get_roots()`/`get_leaves()`, a
  task's own group membership, or `TaskGroup.children` is named in Airflow's
  prose docs — a gap in documentation coverage, not in API visibility, per
  [P3's public-API gaps](../observations/P3/README.md#public-api-gaps).
- **Dagster — partial.** Public `input_mappings`/`output_mappings` APIs expose
  a nested graph's local boundary endpoints — contradicting "nested graph
  boundaries are completely opaque to inspection." Complete documented-public
  enumeration of `nodes`/`dependencies` remains unresolved (same Q1 gap). See
  [P4's claim record](../observations/P4/README.md#comparison-and-claim-record),
  which also states Dagster nested graphs and Airflow `TaskGroup`s are **not
  established** as equivalent to each other.

### Q6 — interrupt/HITL concepts and structural visibility

**Untested for every framework listed above.** No existing probe constructs an
interrupt or human-in-the-loop case; none of #13–#17 is scoped to this
question either. This is a follow-up candidate, not a claim that any of these
frameworks lacks the concept.

### Q7 — stable definition identifiers across runs

- **Airflow — partial.** The mapped task's definition-level task ID
  (`"mapped"`) is identical across all three expansion cardinalities; `map_index`
  is the separate runtime-instance identifier, and the DAG run's own generated
  run ID is excluded from comparison entirely (see
  [evidence conventions](../docs/evidence.md)). See
  [P5](../observations/P5/README.md#definition-identity-versus-runtime-instance-identity).
- **Dagster — partial.** Dynamic mapping keys (`"k0"`, `"k1"`) are stable,
  explicit identifiers distinct from position or count
  ([P6](../observations/P6/README.md#mapped-step-identity-is-keyed-by-mapping-key-not-position-or-count));
  invocation paths (`"left"`, `"right"`) are stable identifiers distinct from
  the shared child `GraphDefinition` name they both instantiate
  ([P4](../observations/P4/README.md)). Both are separate from the run's own
  generated run ID, excluded from comparison.
- **Both frameworks, explicitly bounded.** Each case above compares exactly
  two runs per definition/cardinality (`cmp`, byte-identical). Two stable runs
  show the identifier did not change between those two runs; they do not
  establish that it is stable across arbitrary future runs, code changes, or
  framework versions — see [evidence conventions](../docs/evidence.md).

## Priority

Per [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1)
and [issue planning](../docs/issue-planning.md#approved-framework-investigation):
this matrix ([#12](https://github.com/agent-topology/agent-topology-testbed/issues/12)) →
CrewAI ([#13](https://github.com/agent-topology/agent-topology-testbed/issues/13)) →
ASL ([#14](https://github.com/agent-topology/agent-topology-testbed/issues/14)),
then remaining Dagster/Airflow work and the three boundary probes
([#15](https://github.com/agent-topology/agent-topology-testbed/issues/15),
[#16](https://github.com/agent-topology/agent-topology-testbed/issues/16),
[#17](https://github.com/agent-topology/agent-topology-testbed/issues/17)).
Priority is not a blocked-by relationship: the existing dependency chains
(P0→P1→P3→P5, P0→P2→P4→P6) are unchanged, ASL does not depend on CrewAI, and
the three boundary probes do not depend on each other. Completed
[#2](https://github.com/agent-topology/agent-topology-testbed/issues/2)/[#3](https://github.com/agent-topology/agent-topology-testbed/issues/3)
evidence is preserved as-is. Keep at most two issues in progress at a time.

---

# Reproduce P0

Run from the repository root in a POSIX shell. Verified environment: macOS arm64,
CPython **3.11.16**, `uv 0.12.10`. The locks resolve for this platform; other OSes
and Python versions are not verified. The scripts reject other Python patch or
framework versions. Report installation/API failures without changing the pins.
No agent-topology package, renderer build, scheduler, or service is required.

## Inspect before setup

Read [Airflow smoke input](airflow/smoke.py), [Dagster smoke input](dagster/smoke.py),
their literal expectations, and [P0's question/limitations](../observations/P0/README.md).
Inspect the direct requirements, full resolved pins/hashes, and vendored official
Airflow constraints **before** installing. Locks include transitive runtime
dependencies; source distributions may need a compiler/build tools. They do not
pin an OS image or build-tool environment.

```sh
cat probes/airflow/requirements.txt probes/airflow/constraints-3.11.txt
cat probes/airflow/requirements.lock
cat probes/dagster/requirements.txt probes/dagster/requirements.lock
uv --version
uv python install 3.11.16
```

## Airflow setup

Use a new `.venvs/airflow` directory for clean reproduction. Do not reuse an
environment with unrelated packages. `sync` installs the committed lock without
re-resolving dependencies; `--require-hashes` verifies downloaded distributions.

```sh
uv venv --python 3.11.16 .venvs/airflow
uv pip sync --python .venvs/airflow/bin/python --require-hashes probes/airflow/requirements.lock
uv pip check --python .venvs/airflow/bin/python
```

## Airflow run

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/airflow/bin/python probes/airflow/smoke.py --mode static --output .probe-runs/airflow-static-$n.json > .probe-runs/airflow-static-$n.log 2>&1
  .venvs/airflow/bin/python probes/airflow/smoke.py --mode execution --output .probe-runs/airflow-$n.json > .probe-runs/airflow-$n.log 2>&1
done
cmp .probe-runs/airflow-static-1.json .probe-runs/airflow-static-2.json
cmp .probe-runs/airflow-1.json .probe-runs/airflow-2.json
```

Each command clears inherited Airflow settings before importing it, changes into
a fresh temporary directory, and removes that state afterwards. Execution first
runs `python -m airflow db migrate` against its own SQLite database, then
`dag.test()` at the fixed logical date `2024-01-02T00:00:00Z`.

## Airflow branch/join run (P1)

Same `.venvs/airflow` environment as above; no separate install. Read
[the branch/join probe](airflow/branch.py) and [P1's question/expected states](../observations/P1/README.md)
before running.

```sh
set -eu
mkdir -p .probe-runs
for case in single multiple none; do
  for n in 1 2; do
    .venvs/airflow/bin/python probes/airflow/branch.py --case "$case" --mode static \
      --output ".probe-runs/branch-$case-static-$n.json" > ".probe-runs/branch-$case-static-$n.log" 2>&1
    .venvs/airflow/bin/python probes/airflow/branch.py --case "$case" --mode callable \
      --output ".probe-runs/branch-$case-callable-$n.json" > ".probe-runs/branch-$case-callable-$n.log" 2>&1
    .venvs/airflow/bin/python probes/airflow/branch.py --case "$case" --mode execution \
      --output ".probe-runs/branch-$case-$n.json" > ".probe-runs/branch-$case-$n.log" 2>&1
  done
  cmp ".probe-runs/branch-$case-static-1.json" ".probe-runs/branch-$case-static-2.json"
  cmp ".probe-runs/branch-$case-callable-1.json" ".probe-runs/branch-$case-callable-2.json"
  cmp ".probe-runs/branch-$case-1.json" ".probe-runs/branch-$case-2.json"
done
```

Each case builds DAG `p1_branch` with the router's callback hardcoded to that
case's return value, then isolates state exactly as the P0 Airflow run does.
`--mode execution` also produces the `static` and `callable` sections; the
standalone `static`/`callable` modes skip `airflow db migrate` and `dag.test()`
entirely, so they carry no execution evidence.

## Airflow grouping/roots/join run (P3)

Same `.venvs/airflow` environment as above; no separate install. Read
[the grouping probe](airflow/grouping.py) and [P3's question/expected facts](../observations/P3/README.md)
before running.

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/airflow/bin/python probes/airflow/grouping.py --mode static \
    --output ".probe-runs/grouping-static-$n.json" > ".probe-runs/grouping-static-$n.log" 2>&1
  .venvs/airflow/bin/python probes/airflow/grouping.py --mode execution \
    --output ".probe-runs/grouping-$n.json" > ".probe-runs/grouping-$n.log" 2>&1
done
cmp .probe-runs/grouping-static-1.json .probe-runs/grouping-static-2.json
cmp .probe-runs/grouping-1.json .probe-runs/grouping-2.json
```

Builds DAG `p3_grouping`: one `TaskGroup` with two parallel members, a
predecessor and successor crossing its boundary, and a two-source convergence
join reusing P1's `none_failed_min_one_success` rule, then isolates state
exactly as the P0 Airflow run does. `--mode execution` also produces the
`static` section; the standalone `static` mode skips `airflow db migrate` and
`dag.test()` entirely, so it carries no execution evidence. This probe runs one
case, not P1's matrix, because it reuses P1's trigger-rule evidence rather than
retesting it — see P3's README for why.

## Airflow mapped-task run (P5)

Same `.venvs/airflow` environment as above; no separate install. Read
[the mapped-task probe](airflow/mapped.py) and [P5's question/expected facts](../observations/P5/README.md)
before running.

```sh
set -eu
mkdir -p .probe-runs
for case in 0 1 2; do
  for n in 1 2; do
    .venvs/airflow/bin/python probes/airflow/mapped.py --case "$case" --mode static \
      --output ".probe-runs/mapped-$case-static-$n.json" > ".probe-runs/mapped-$case-static-$n.log" 2>&1
    .venvs/airflow/bin/python probes/airflow/mapped.py --case "$case" --mode execution \
      --output ".probe-runs/mapped-$case-$n.json" > ".probe-runs/mapped-$case-$n.log" 2>&1
  done
  cmp ".probe-runs/mapped-$case-static-1.json" ".probe-runs/mapped-$case-static-2.json"
  cmp ".probe-runs/mapped-$case-1.json" ".probe-runs/mapped-$case-2.json"
done
```

Builds DAG `p5_mapped`: one TaskFlow source hardcoded per case to return a
list of length 0, 1, or 2, one TaskFlow task mapped over that list, and two
downstream aggregations reusing P1's `all_success`/`none_failed_min_one_success`
rules, then isolates state exactly as the P0 Airflow run does. `--mode
execution` also produces the `static` section; the standalone `static` mode
skips `airflow db migrate` and `dag.test()` entirely, so it carries no
execution evidence. The `static` section is identical across all three cases:
the DAG definition names one mapped task, not any particular expansion count.

## Dagster setup

```sh
uv venv --python 3.11.16 .venvs/dagster
uv pip sync --python .venvs/dagster/bin/python --require-hashes probes/dagster/requirements.lock
uv pip check --python .venvs/dagster/bin/python
```

## Dagster run

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/dagster/bin/python probes/dagster/smoke.py --mode static --output .probe-runs/dagster-static-$n.json > .probe-runs/dagster-static-$n.log 2>&1
  .venvs/dagster/bin/python probes/dagster/smoke.py --mode execution --output .probe-runs/dagster-$n.json > .probe-runs/dagster-$n.log 2>&1
done
cmp .probe-runs/dagster-static-1.json .probe-runs/dagster-static-2.json
cmp .probe-runs/dagster-1.json .probe-runs/dagster-2.json
```

Each process clears inherited Dagster settings and uses a new temporary home and
working directory. Execution uses `DagsterInstance.ephemeral(tempdir=home)` and
`execute_in_process(raise_on_error=True)`, with in-memory output storage.

## Dagster conditional-outputs run (P2)

Same `.venvs/dagster` environment as above; no separate install. Read
[the conditional-outputs probe](dagster/conditional.py) and
[P2's question/expected states](../observations/P2/README.md) before running.

```sh
set -eu
mkdir -p .probe-runs
for case in none single multiple; do
  for n in 1 2; do
    .venvs/dagster/bin/python probes/dagster/conditional.py --case "$case" --mode static \
      --output ".probe-runs/conditional-$case-static-$n.json" > ".probe-runs/conditional-$case-static-$n.log" 2>&1
    .venvs/dagster/bin/python probes/dagster/conditional.py --case "$case" --mode execution \
      --output ".probe-runs/conditional-$case-$n.json" > ".probe-runs/conditional-$case-$n.log" 2>&1
  done
  cmp ".probe-runs/conditional-$case-static-1.json" ".probe-runs/conditional-$case-static-2.json"
  cmp ".probe-runs/conditional-$case-1.json" ".probe-runs/conditional-$case-2.json"
done
```

Each case runs job `p2_conditional` with `conditional_source`'s op config
hardcoded to that case's emitted-output list, then isolates state exactly as
the P0 Dagster run does (`DagsterInstance.ephemeral(tempdir=home)`, fresh
`DAGSTER_HOME`). `--mode execution` also produces the `static` section; the
standalone `static` mode never calls `execute_in_process()`, so it carries no
execution evidence.

## Dagster nested boundaries/convergence run (P4)

Use the same isolated Dagster setup and unchanged lock above. Read
[the nested input and literal expectations](dagster/nested.py) and
[P4's question/API limitations](../observations/P4/README.md) first.

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/dagster/bin/python probes/dagster/nested.py --mode static \
    --output ".probe-runs/nested-static-$n.json" > ".probe-runs/nested-static-$n.log" 2>&1
  .venvs/dagster/bin/python probes/dagster/nested.py --mode execution \
    --output ".probe-runs/nested-$n.json" > ".probe-runs/nested-$n.log" 2>&1
done
cmp .probe-runs/nested-static-1.json .probe-runs/nested-static-2.json
cmp .probe-runs/nested-1.json .probe-runs/nested-2.json
.venvs/dagster/bin/python probes/dagster/test_nested.py
```

Graph `p4_nested` invokes the same two-op child as `left` and `right`, with
top-level inputs `1` and `2`, then passes both outputs to `consume`. Five op
steps execute; the two graph invocations have mapped outputs, not separate op
step states. The standalone static mode never creates or executes a job.
Execution uses a fresh temporary home and an ephemeral instance, as in P0/P2.
`test_nested.py` checks that identity/edge loss, a crossed boundary mapping,
wrong execution input, and an unsupported version exit nonzero under `-O`;
it also prevents execution entry points in a standalone static run.

## Dagster dynamic-mapping run (P6)

Use the same isolated Dagster setup and unchanged lock above. Read
[the dynamic-mapping probe](dagster/dynamic.py) and
[P6's question/expected states](../observations/P6/README.md) first.

```sh
set -eu
mkdir -p .probe-runs
for case in 0 1 2; do
  for n in 1 2; do
    .venvs/dagster/bin/python probes/dagster/dynamic.py --case "$case" --mode static \
      --output ".probe-runs/dynamic-$case-static-$n.json" > ".probe-runs/dynamic-$case-static-$n.log" 2>&1
    .venvs/dagster/bin/python probes/dagster/dynamic.py --case "$case" --mode execution \
      --output ".probe-runs/dynamic-$case-$n.json" > ".probe-runs/dynamic-$case-$n.log" 2>&1
  done
  cmp ".probe-runs/dynamic-$case-static-1.json" ".probe-runs/dynamic-$case-static-2.json"
  cmp ".probe-runs/dynamic-$case-1.json" ".probe-runs/dynamic-$case-2.json"
done
.venvs/dagster/bin/python probes/dagster/test_dynamic.py
```

Job `p6_dynamic` wires one `DynamicOut()` source into one mapped op via
`.map()` and one collect consumer via `.collect()`, then isolates state
exactly as the P0/P2/P4 Dagster runs do. Each case's op config sets
`dynamic_source`'s emitted mapping keys to `[]`, `["k0"]`, or `["k0",
"k1"]`. `--mode execution` also produces the `static` section; the
standalone `static` mode never calls `execute_in_process()`, so it carries
no execution evidence. `test_dynamic.py` checks that dependency-kind loss,
`is_dynamic`-flag loss, a duplicate mapping key, a wrong cardinality, and an
unsupported version all exit nonzero under `-O`; it also prevents execution
entry points in a standalone static run.

## Failure interpretation

All commands must exit zero before records count as evidence. Assertions raise
explicit exceptions even with Python `-O`; missing dependencies, wrong versions,
database/API failures, and output errors also exit nonzero. `cmp` returns nonzero
on differences. Read the corresponding `.log` on failure; never use a stale JSON
file as a pass. Raw logs include transient timestamps, paths, PIDs, and run IDs;
JSON contains the normalized facts described in [P0](../observations/P0/README.md).

## Lock provenance and deliberate regeneration

`airflow/constraints-3.11.txt` is the unmodified
[Airflow 2.10.5 official Python 3.11 constraint file](https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt).
The direct inputs are `apache-airflow==2.10.5` and `dagster==1.13.22`, separately.
The following commands generated the locks using uv 0.12.10; regeneration is a
reviewed dependency change, **not** a reproduction step. Inspect the resulting
pins and hashes again before installation, then rerun both observations for the
affected framework and record new provenance.

```sh
uv pip compile probes/airflow/requirements.txt --constraint probes/airflow/constraints-3.11.txt --python-version 3.11.16 --generate-hashes --output-file probes/airflow/requirements.lock
uv pip compile probes/dagster/requirements.txt --python-version 3.11.16 --generate-hashes --output-file probes/dagster/requirements.lock
```
