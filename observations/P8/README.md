# P8: Prefect definition metadata versus task invocation structure

For [#16](https://github.com/agent-topology/agent-topology-testbed/issues/16),
[epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1), and
[M1](../../probes/README.md#common-question-matrix-m1).

**Result:** in Prefect **3.6.22**, the inspected public flow/task metadata
identifies supplied definitions but does not enumerate their invocation graph.
There is a public visualization path before *task* execution, but it evaluates
the flow's Python body; it is not extraction without executing user code.
The local framework runs expose task instances and input dependencies: the
linear control has 2 task runs/1 edge, the loop at 0 has 0/0, and the loop at 2
has 4/2. Reusing two task definitions does not reduce those four instances to two.
This supports a **runtime observation path for this imperative programming
model**, with a separately bounded visualization/source-analysis candidate.
It neither rejects every Prefect 3 program nor says anything about Prefect 2.

## Question, input, and independent expectations

Question: can public inspection obtain the selected flow's task topology without
executing its body, and what changes when the same tasks are invoked repeatedly?

Minimal input: [fixtures.py](../../probes/boundaries/prefect/fixtures.py) has two
small deterministic tasks, A returning `["a"]` and B returning `"ab"` from that
value. `linear` calls A then B once. `loop(count)` repeats the same A/B pair.
Only inputs **0 and 2** are used. Passing A's public `State` to B retains an
explicit dependency even for small return values. Cache policy is `NO_CACHE`,
results are not persisted, and there are no retries. This is direct synchronous
Prefect task calling, not `.submit()`, `.map()`, deployment, or distributed work.
No external data, cloud workspace, worker, or task runner concurrency experiment.

[expected.json](../../probes/boundaries/prefect/expected.json) was authored before
the extraction logic. Its literal expectations are:

| Case | Task body order | Return value | Native input edges, expressed using comparison-local invocation positions |
| --- | --- | --- | --- |
| linear | A, B | `["ab"]` | 0 → 1, input `value` |
| loop-0 | none | `[]` | none |
| loop-2 | A, B, A, B | `["ab", "ab"]` | 0 → 1 and 2 → 3, both input `value` |

Each task must have exactly `PENDING`, `RUNNING`, `COMPLETED` in that order and
`run_count=1`. The verifier also requires sequential lifecycle order across these
synchronous invocations. The fixture's body-entry list independently records
execution order and measured return values; **edges come from public task-run
inputs, not that instrumentation**. The explicit supplied flow/task lists are
investigator inputs, not automatic discovery of all tasks reachable from a flow.

One initial identity hypothesis was corrected transparently: expecting dynamic
keys `0,0` and `0,0,1,1` failed on the first working linear run. Pinned source
shows this direct-call engine requests `stable=False` and generates UUID4 values.
The final checks require UUID4 validity and uniqueness and retain the actual
values in native records. Invocation/count/value/edge expectations did not change.

## Evidence classes and public API review

**Static:** import the decorated definitions; read `name`, explicit `version`,
`fn`, flow `parameters`, task `task_key`, and Python signatures. No flow or task
body runs, no API service is started. A profiler test guards all four bodies.
Metadata is recorded before the test harness or any flow invocation.

**Source/documentary:** the graph/export and pause capabilities below. The metadata/visualization/entrypoint review preceded task execution;
runtime identity helper review followed the failed dynamic-key hypothesis. [source-review.json](source-review.json)
records tagged source hashes and byte equality with installed SDK files. The
released baseline was selected as a Python 3.11-compatible version, not as a
claim to cover the latest release. PyPI records its upload on 2026-03-12.

**Execution:** call decorated flows normally with `return_state=True`, then read
public [SyncPrefectClient.read_task_runs() and read_task_run_states()](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/client/orchestration/__init__.py#L1565) against
the disposable local API. The records contain API-persisted lifecycle states,
not a websocket event stream or complete provenance collector. State persistence
is asynchronous, so collection polls for terminal records/history for at most
30 seconds and fails on timeout or any count/identity/edge mismatch.

**Callable evidence:** none was collected. We did not call `Flow.visualize()` or
invoke `.fn` directly. Its behavior below is a pinned-source conclusion, not a
locally observed visualization result.

| Reviewed surface | Boundary |
| --- | --- |
| [Flow metadata and authoring](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/flows.py), [Task authoring](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/tasks.py) | Public definition objects retain names, versions, callables, parameter schemas/task keys. These fields contain neither an invocation registry nor task dependency edges for these fixtures. A supplied task inventory is not selected-flow membership. |
| [Flow.visualize, lines 1916–1979](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/flows.py#L1916), [visualization implementation](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/utilities/visualization.py#L152) | A real positive capability: builds a Graphviz graph with task calls tracked instead of executing task bodies. However, it calls `self.fn(*args, **kwargs)` and can depend on inputs or `viz_return_value` mocks. It is a path evaluation before task execution, not a universal static graph. Rendering requires Graphviz and opens a viewer; neither was needed or attempted here. |
| [Flow.from_source](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/flows.py#L1286), [Flow.to_deployment](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/flows.py#L853) | File/module entrypoints select executable flow code; deployments configure scheduling/infrastructure/parameters. Neither is task dependency enumeration. No source-loading/deployment operation was invoked. |
| [REST graph and graph-v2](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/server/api/flow_runs.py#L341) | Graph export also exists for a **flow run UUID**: task dependencies and task/subflow run structure. It consumes observed run records, not an unexecuted flow definition. These endpoints were source-reviewed; the probe reads the underlying public task-run/state APIs instead. |
| [Direct task-run creation](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/task_engine.py#L146), [dynamic key generation](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/utilities/_engine.py#L13) | This call path requests nonstable dynamic keys. Their UUID values are invocation facts, not reusable structural IDs. Private implementation source explains this observation; the probe never calls private helpers. |
| [Task key generation](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/tasks.py#L268) | Public `task_key` includes a function/code-derived hash. Equal keys in this pair of runs do not promise stability across path/code/version changes. Explicit `p8-v1` versions are authored labels, not discovered graph identity. |

The bounded review covered the tagged Flow/Task authoring APIs, their visualization
implementation, source/deployment entrypoints, flow-run graph routes, and the
runtime identity/pause/testing surfaces linked here. No public zero-body-execution
invocation graph was found in that surface. This is not an exhaustive proof about
all integrations, custom DSLs, Python source analyzers, or other SDK versions.

Current [flow docs](https://docs.prefect.io/v3/concepts/flows),
[task docs](https://docs.prefect.io/v3/concepts/tasks), and
[visualization guide](https://docs.prefect.io/v3/how-to-guides/workflows/visualize-workflow-structure)
were consulted for API leads. Moving docs now also mention
`generate_mermaid_graph`; that method is absent from the inspected 3.6.22 Flow
implementation, so no result is attributed to it for this pin. Tagged source is
the version-specific authority here.

## Seven-question matrix answers

| ID | Status | Scoped answer |
| --- | --- | --- |
| Q1 | partial | Static metadata works, but no zero-body-execution invocation graph was found. A documented visualization route evaluates Python flow code before task execution; runtime graph routes consume runs. These are three distinct boundaries. |
| Q2 | partial | Definition names/task keys are inspectable. Public runtime task UUIDs and `task_inputs` enumerate instances and input edges, including repeated uses; metadata alone does not identify selected-flow invocation membership. |
| Q3 | partial | Executed loop counts 0/2 produce 0/4 task runs, with exactly the observed A/B pairs. This is input-dependent cardinality, not a declared fan-out, branch-selection, parallelism, or production scheduling guarantee. |
| Q4 | untested | No multi-source convergence or AND/OR comparison. B depending on one A does not answer join semantics. |
| Q5 | untested | No nested-flow fixture. A run-graph endpoint documenting subflows does not measure static nested boundaries, membership, or ports. |
| Q6 | partial, documentary | Public pause/resume and typed human input exist, but no static interrupt placement metadata was extracted from these definitions; no pause was executed. |
| Q7 | partial | Definition names, explicit versions and task keys match in two fresh processes. Flow/task run UUIDs and this path's dynamic UUIDs differ and remain in native evidence. Repeated invocations share task keys but retain separate identity. No universal stability claim. |

For Q6, [pause_flow_run in the pinned source](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/flow_runs.py#L334)
blocks an executing flow until resumed and supports `wait_for_input` types.
The [interactive workflow guide](https://docs.prefect.io/v3/advanced/interactive)
documents human-supplied input. Native HITL capability does not automatically
attach an interrupt before/after a statically enumerable task node. The absence
of pause in these tiny fixtures is not evidence Prefect lacks that capability.

## Reproduction and state isolation

Verified on macOS arm64, CPython **3.11.16**, `uv 0.12.10`. The isolated
[requirements](../../probes/boundaries/prefect/requirements.txt) pin Prefect 3.6.22,
FastAPI 0.132.0 and Starlette 0.50.0. The
[hash lock](../../probes/boundaries/prefect/requirements.lock) fixes all 105
installed distributions. No other framework environment or CI is involved.

Setup incident: the first resolver chose FastAPI 0.141.1 / Starlette 1.6.0,
which met declared package constraints but failed the API request with
`AttributeError: 'PrefectRouter' object has no attribute 'routes'` (HTTP 500).
This was blocked setup evidence, not a capability result. The two compatibility
pins match [Prefect 3.6.22's own uv.lock](https://github.com/PrefectHQ/prefect/blob/3.6.22/uv.lock);
the SDK/Python pins were not changed. An initial source lookup also used a
nonexistent client file path (HTTP 404); installed public client methods were
subsequently inspected. Neither failed attempt produced accepted observations.

The public [prefect_test_harness](https://github.com/PrefectHQ/prefect/blob/3.6.22/src/prefect/testing/utilities.py#L114)
starts a temporary local ASGI API subprocess with SQLite. The server uses the same
pinned Prefect installation; no separate binary is downloaded. Each fresh process
gets a new temporary Prefect home/profile and database; ambient `PREFECT_*`
settings are removed before SDK import, analytics disabled, no credentials loaded.
The harness stops its server and drains workers on normal exit. Its database
cleanup is registered at process exit. The probe catches validation exceptions
inside the harness and rethrows after its normal shutdown, since this SDK's
post-yield stop is not protected by `finally`. A hard kill/startup failure is
outside that cleanup guarantee; no later run reuses state. No persistent service
is operated. Prefect's ordinary background services are not measurements of
production concurrency.

Inspect input and constraints before installation. From the repository root:

```sh
cat probes/boundaries/prefect/fixtures.py probes/boundaries/prefect/expected.json
cat probes/boundaries/prefect/requirements.txt probes/boundaries/prefect/requirements.lock
uv venv --python 3.11.16 .venvs/prefect
uv pip sync --python .venvs/prefect/bin/python --require-hashes probes/boundaries/prefect/requirements.lock
uv pip check --python .venvs/prefect/bin/python
.venvs/prefect/bin/python probes/boundaries/prefect/probe.py --static-only --output .probe-runs/p8-static.json
for n in 1 2; do
  .venvs/prefect/bin/python probes/boundaries/prefect/probe.py --output .probe-runs/p8-$n.json
done
.venvs/prefect/bin/python probes/boundaries/prefect/verify.py .probe-runs/p8-1.json .probe-runs/p8-2.json
cmp .probe-runs/p8-1.json observations/P8/run-1.json
.venvs/prefect/bin/python -O probes/boundaries/prefect/probe.py --output .probe-runs/p8-optimized.json
.venvs/prefect/bin/python -O probes/boundaries/prefect/verify.py .probe-runs/p8-1.json .probe-runs/p8-optimized.json
.venvs/prefect/bin/python -m unittest discover -s probes/boundaries/prefect -p 'test_*.py' -v
```

Lock generation, already done (do not re-resolve to reproduce):

```sh
uv pip compile --python 3.11.16 --generate-hashes --output-file probes/boundaries/prefect/requirements.lock probes/boundaries/prefect/requirements.txt
```

## Records, normalization, and decision

[Run 1](run-1.json) and [run 2](run-2.json) are semantic records;
[native run 1](run-1.raw.json) and [native run 2](run-2.raw.json) retain generated
flow/task IDs, dynamic UUIDs, native inputs, names, state IDs/timestamps and order.
Source/lock/expectation/test hashes are embedded in the semantic records.

Normalization sorts unordered dependency collections without deduplication.
Invocation positions are assigned by native start time and used only to compare
edge references and event order; **they are not stable graph IDs**. Names/task
keys/versions, counts, input ports, results, states and meaningful lifecycle order
remain in comparisons. Generated UUIDs, timestamp values, durations and generated
run names remain in native evidence rather than semantic comparisons. The verifier
checks every native dependency against the expected invocation positions, validates
UUID uniqueness within and disjointness across runs, and rejects added instances,
wrong repeated-instance edges, or reordered states. No unexpected records are
trimmed to obtain an equal comparison.

Final checks: dependency compatibility; two fresh-process executions and semantic
comparison; an optimized execution and comparison; three integrity tests, including
negative assertions under normal and optimized Python; source/lock hashes and
local documentation links. All passed. No package-manager/build/Cargo checks from
unrelated projects were introduced; historical beta.2 evidence is unchanged.

A static adapter would be justified by a public invocation-graph API that requires
no body evaluation, or an explicitly restricted declarative/source-analysis subset
with independent correctness evidence and unsupported-case handling. A safe,
input-specific visualization evaluation is a different candidate and needs its
own validation; the source review alone does not certify it. For this fixture's
actual invocation multiplicity, the measured public task-run path works and must
retain run identity and dependencies. No upstream producer, topology contract,
publication, release gate, or Prefect 2 conclusion follows from this local result.

## Indexed closure disposition

The [P7 P8 claim inventory](../../findings/cross-framework-reconciliation.md#p8-disposition)
records each measured claim as supported, contradicted or unresolved, with its
non-finding reason, decision impact and smallest follow-up. It is reachable from
the [findings index](../../findings/README.md). This completes the retrospective
[closure checklist](../../docs/issue-planning.md#probe-closure-disposition)
without changing the experiment, raw records or closed measurement issue.
