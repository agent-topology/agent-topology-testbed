# T1: Temporal public static structure boundaries

For [#15](https://github.com/agent-topology/agent-topology-testbed/issues/15),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1)
and [M1](../../probes/README.md#common-question-matrix-m1).
Historical beta.2 baseline `571e881e6d509b6e26ff8bf14b98e207d12e7ce9` is untouched.

**Result:** the inspected Python SDK 1.18.0 surface supports definition authoring
and worker registration, but no documented public definition-to-topology export
was found in the bounded search below. The two fixtures retain Python names and
identical run signatures without running their bodies; these are not invocation
nodes or edges. This supports a **runtime observation path as a candidate**, not
a ready static producer. A restricted source-analysis subset remains possible,
but is neither implemented nor validated here. This is not proof that Temporal
has no static structure, or that every SDK/version shares this boundary.

## Question and minimal input

Measured question: can public SDK definition inspection distinguish the invocation
structure of a linear workflow from an input-dependent choice?

Input: [fixtures.py](../../probes/boundaries/temporal/fixtures.py) contains exactly
two deterministic string activities, reused by two decorated workflow classes:

| Definition | Source-level reasoning, not extracted SDK edges | Supplied execution input |
| --- | --- | --- |
| `LinearWorkflow`, authored type `t1.linear` | Await `activity_a(value)`, then await `activity_b(result)` | None |
| `ChoiceWorkflow`, authored type `t1.choice` | If `value == "a"`, await A; otherwise await B | None |

Both run methods have `(self, value: str) -> str`. The activities are Python
`activity_a`/`activity_b`, with deliberately different authored Temporal names
`t1.a`/`t1.b`. Thus Python `__name__` must not masquerade as an SDK type-name
extractor. The strings `"a"` and `"b"` would suffice for a future branch execution
experiment; no callback is invoked with either here.

## Evidence classes and expectations

**Static:** import definitions through public `workflow.defn`, `workflow.run`,
and `activity.defn`; inspect the supplied Python objects using `inspect`;
inspect the public `Worker` constructor signature and `workflow.Info` /
`activity.Info` dataclass schemas. Decorators execute definition validation,
but workflow and activity bodies do not execute. No Worker, Client, Info instance,
event loop, mock, private SDK accessor, or server is constructed.

**Source/documentation reasoning:** authored control flow, decorator name
configuration, private storage, registration semantics, and the export-capability
review below. These facts are not added as if they were graph extraction results.
**Callable and execution evidence:** none.

[expected.json](../../probes/boundaries/temporal/expected.json) was written before
the extractor, from the fixture design and pinned API declarations. It requires
two workflow names with identical run signatures, two async activity signatures,
registration parameters `activities`/`workflows`, empty `bodies_entered`, false
runtime-context flags, and the literal identity-field subsets listed in the
records. It does not assert a fabricated empty graph or assert that a guessed
`export_graph` attribute is missing. Additional public Info fields are out of
the identity subset's scope.

## Observations

[Run 1](inspection-1.json) and [run 2](inspection-2.json), each in a fresh process,
match the independent expectations and compare byte-identically. The optimized
positive run also compares identically. Three integrity tests pass: preserve
duplicate definitions; profile the extractor to reject entry into any fixture
body; reject a corrupted expected workflow name with nonzero exit and no new
output, both normally and under `python -O`.

The observed Python signatures do not distinguish the two control-flow shapes.
Even the linear control has no invocation graph in this inspected metadata.
Knowing its sequence from reading the source is useful, but is a different
extraction mechanism. The explicit class/activity lists are investigator inputs;
the probe does not claim to discover registrations or entry methods globally.

## Public API and graph/export search

Pinned SDK: released **1.18.0** (PyPI upload 2025-09-19), selected as a bounded,
Python 3.11-compatible baseline, not a claim to test the latest SDK.
Tagged source commit: **3fe7e422b008bcb8cd94e985f18ebec2de70e8e6**.
[source-review.json](source-review.json) records source hashes; installed
`workflow.py` and `activity.py` matched the tagged files exactly.

The search on 2026-09-12 covered the pinned README and Python SDK implementation,
excluding generated API/protobuf bindings. It combined the lexical search below
with manual review of definition decorators, registration, context accessors,
message handlers, and history serialization. Keyword absence alone is not a
capability proof. Current [Workflow Definition documentation](https://docs.temporal.io/workflow-definition)
and the [workflow](https://python.temporal.io/temporalio.workflow.html) /
[activity](https://python.temporal.io/temporalio.activity.html) API indexes were
also checked for graph/export and name-accessor leads; those moving pages are
orientation only. Version-specific conclusions use the pinned source links.

| Surface reviewed | What it establishes / boundary |
| --- | --- |
| [workflow decorators](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/workflow.py#L113-L204), [activity decorator](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/activity.py#L66-L100) | Public definition authoring and name configuration; decorators retain the Python class/callable. |
| [workflow `_Definition`](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/workflow.py#L1591-L1629), [activity `_Definition`](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/activity.py#L560-L618) | Native metadata exists: names, callable/type information, and workflow handler maps. Accessors and storage are underscore-prefixed; T1 reads their source but never invokes them. The reviewed records have no invocation-edge field. Public authoring is not public metadata retrieval. |
| [Worker registration and config](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/worker/_worker.py#L155-L173), [config implementation](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/worker/_worker.py#L618-L628) | Accepts definitions, and returns a copy of supplied configuration. A registration inventory is not workflow-to-activity incidence, ordering, or instance cardinality. No registration was performed here. |
| [history fetch](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/client.py#L1855-L1880), [history JSON](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/client.py#L3255-L3312) | Public export exists for execution history. It needs events from an execution; JSON serialization alone does not discover an unexecuted definition graph. `to_json()` omits workflow ID, so a future observer must retain it separately. |
| [static summary/details](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/client.py#L556-L560) | User-supplied UI text for an execution, not a structural graph. |

Search hits also included OpenAI span-data `export`, cloud namespace export-sink
RPCs, metric exporting, `graphlib` in sandbox restrictions, and the substring
in “cryptographically.” Their contexts concern tracing, services, metrics,
imports, or randomness, respectively. None is a definition-to-graph API.
The [pinned replay documentation](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/README.md#workflow-replay)
likewise takes pre-existing history; no replay was attempted.

Repeat the source review in a disposable directory:

```sh
git clone --depth 1 --branch 1.18.0 https://github.com/temporalio/sdk-python.git /tmp/t1-sdk-review
git -C /tmp/t1-sdk-review rev-parse HEAD
rg -n -i 'graph|topology|export|visualiz' /tmp/t1-sdk-review/README.md /tmp/t1-sdk-review/temporalio \
  --glob '*.py' --glob '*.md' --glob '!**/api/**' --glob '!**/bridge/proto/**'
```

No documented public graph export was found **within this reviewed surface**.
Other releases, SDK languages, integrations, and application-authored DSLs are
unexamined. Finding such an API would require reassessing this boundary, not
explaining it away.

## Seven-question matrix answers

| ID | Status | Scoped answer |
| --- | --- | --- |
| Q1 | partial | Static definition authoring/Python inspection works; a public exported invocation topology was not found for either fixture. Native private metadata and a supported public extractor are distinct. |
| Q2 | partial | Supplied definitions and authored type names are explicit; SDK-exported invocation node IDs/edges are not established. Python names are neither custom Temporal type names nor activity-instance IDs. |
| Q3 | untested | Source says sequential A→B versus input-dependent A/B. This is neither a declared SDK fan-out graph nor measured selection, scheduled work, retries, or concurrency. |
| Q4 | untested | No multi-source convergence input. Sequential awaiting of B after A is not an AND/OR join experiment. |
| Q5 | untested | No child workflow input. Child-workflow APIs exist in the pinned SDK, but nested membership, ports, and opaque graph-boundary extraction were not measured. |
| Q6 | partial, documentation only | Signal/update decorators name handlers; [pinned handler documentation](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/README.md#signal-and-update-handlers) describes incoming messages starting handler tasks. This does not attach a before/after interrupt to a static invocation node. No signal, update, wait, pause, or HITL case was executed or added to the fixtures. |
| Q7 | partial | Python definition names/signatures repeat across two imports; authored Temporal type strings are source facts. Public [workflow Info](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/workflow.py#L481-L536) and [activity Info](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/activity.py#L103-L126) expose separate field schemas for workflow type/ID/run ID and activity type/ID. No execution IDs were generated or measured; two imports do not establish universal identity stability. |

For Q6 specifically, the public [get_signal_handler](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/temporalio/workflow.py#L4812-L4824)
consults the current runtime. A named handler may enable a human-driven workflow,
but is not by itself a statically placed interruption point.

## Decision and execution boundary

Execution is unnecessary to finish this public-static-inspection question.
No test server was downloaded; no server version, production/cloud connection,
or custom orchestration environment exists for T1.

Distinct unanswered runtime question: for the two branch inputs and the linear
control, which ActivityTaskScheduled/completion events, identities, and ordering
does Temporal actually record? If that becomes decision-relevant, use only a
disposable SDK `WorkflowEnvironment`, a local worker, and these deterministic
activities after revalidating their inputs. Record the test-server artifact,
version, and download. The pinned [testing guidance](https://github.com/temporalio/sdk-python/blob/3fe7e422b008bcb8cd94e985f18ebec2de70e8e6/README.md#testing)
documents the time-skipping server download and macOS ARM/x64 caveat. That is a
future infrastructure requirement, not evidence of a failed setup here.

Candidate criterion: a static producer would need an independently supported
graph API or an explicitly bounded source/DSL analysis with correctness evidence.
Execution history is a documented candidate for a runtime observer, still
unvalidated locally. Neither route is certified by T1; no upstream contract,
publication, renderer change, release gate, or framework-wide rejection follows.

## Reproduction, normalization, and checks

Verified macOS arm64 (Darwin 25.5.0), CPython **3.11.16**, `uv 0.12.10`.
The isolated [requirements](../../probes/boundaries/temporal/requirements.txt)
pin SDK 1.18.0; the [lock](../../probes/boundaries/temporal/requirements.lock)
contains all five installed distributions with hashes, no extras. Other OSes
and Python patches were not tested. Inspect the tiny fixture, expectations, and
lock before setup. Lock generation (already done; do not re-resolve to reproduce):

```sh
uv pip compile --python 3.11.16 --generate-hashes --output-file probes/boundaries/temporal/requirements.lock probes/boundaries/temporal/requirements.txt
```

From the repository root, with a fresh `.venvs/temporal`:

```sh
set -eu
cat probes/boundaries/temporal/fixtures.py probes/boundaries/temporal/expected.json
cat probes/boundaries/temporal/requirements.txt probes/boundaries/temporal/requirements.lock
uv venv --python 3.11.16 .venvs/temporal
uv pip sync --python .venvs/temporal/bin/python --require-hashes probes/boundaries/temporal/requirements.lock
uv pip check --python .venvs/temporal/bin/python
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/temporal/bin/python probes/boundaries/temporal/inspect_definitions.py --output .probe-runs/t1-$n.json
done
cmp .probe-runs/t1-1.json .probe-runs/t1-2.json
cmp .probe-runs/t1-1.json observations/T1/inspection-1.json
.venvs/temporal/bin/python -O probes/boundaries/temporal/inspect_definitions.py --output .probe-runs/t1-optimized.json
cmp .probe-runs/t1-1.json .probe-runs/t1-optimized.json
.venvs/temporal/bin/python -m unittest discover -s probes/boundaries/temporal -p 'test_*.py' -v
```

All final commands passed: dependency check, two fresh-process inspections,
three comparisons (including optimized mode), and 3 tests (the corruption test
covers both interpreter modes). One preliminary optimized-output command failed
because `.probe-runs` had not been created; after `mkdir -p` it passed. This was
an output-path error, not a Temporal capability result, and its output was not
used as evidence.

Normalization sorts unordered definition/field collections without deduplication
and serializes JSON with sorted keys. No semantic identity, count, or event order
is discarded. There are no runtime events or generated IDs to normalize. Absolute
paths, timestamps, durations, and host details are absent from semantic records;
Python/SDK versions and source/lock hashes remain. Missing dependencies, wrong
versions, API errors, or expectation failures exit nonzero. Always inspect exit
status before trusting any existing output file.
