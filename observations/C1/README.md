# C1: CrewAI Flows — router label selection versus listener cardinality, and
AND/OR convergence

Question: can public definition inspection of a CrewAI Flow preserve the
distinction between `and_()` and `or_()`, and does the existing
`agent-topology` `joins[]` contract already represent their meaning — without
executing anything? Separately: for a router returning one of two fixed
labels, does one selected label imply exactly one triggered listener?

New internal observation for
[issue #13](https://github.com/agent-topology/agent-topology-testbed/issues/13),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1)
and the [M1 expanded priority](../../docs/issue-planning.md#expanded-investigation-priority-m1-c1-s1-and-boundary-probes)
(issue [#12](https://github.com/agent-topology/agent-topology-testbed/issues/12)).
CrewAI has no dependency relationship to P0–P6 (Airflow/Dagster); this is the
first framework probed under the expanded matrix. Historical findings,
transcripts, and gallery artifacts remain unchanged.

## Version resolution (done before installation)

`crewai==1.15.21`, resolved from [PyPI's release history](https://pypi.org/pypi/crewai/json)
as the newest non-dev release at investigation time, with a matching GitHub tag
(`1.15.21`, commit `4ed3dc929d0ee6b6981be452b2094c56fbbe7457`) and matching
version-pinned official docs at `https://docs.crewai.com/v1.15.21/en/concepts/flows`
(the unversioned URL 307-redirects to this exact path — confirmed by reading the
response headers before treating the docs as version-matched). CPython
**3.11.16**, same patch as every other probe in this repository, confirmed
compatible with crewai's own `requires-python = "<3.14,>=3.10"`.

## What public definition inspection exposes without kickoff

Read from the installed 1.15.21 source before writing any expectation:

- `crewai.flow.dsl._conditions.and_()` / `or_()` (`lib/crewai/src/crewai/flow/dsl/_conditions.py`)
  return a plain dict `{"type": "AND"|"OR", "conditions": [...]}` — the
  AND/OR distinction is a literal string, not inferred, from the moment a
  `@listen(and_(...))` / `@listen(or_(...))` decorator runs.
- `Flow.flow_definition()` (`lib/crewai/src/crewai/flow/runtime/__init__.py`) is
  a public, non-underscore **classmethod** that returns the whole static
  `FlowDefinition` from the class alone — no instance, no `kickoff()`. It is
  reachable but **not exported** in `crewai.flow.dsl.__all__` and **not
  mentioned** in the pinned docs page (0 hits for `flow_definition` in
  `flows.md`). This is the native-capability-versus-documented-public-API gap
  this repository's conventions ask to keep separate (see
  [P4's `api_coverage`](../P4/README.md#api-coverage-and-bounded-unsupported-inspection)).
- `crewai.flow.build_flow_structure()` **is** exported in `crewai.flow.__all__`
  (`lib/crewai/src/crewai/flow/__init__.py`) — a fully public, no-kickoff
  projection of `flow_definition()` into a `FlowStructure` TypedDict
  (`nodes`, `edges`, `start_methods`, `router_methods`). Each listener node and
  each edge it derives from an `and_()`/`or_()` condition carries a literal
  `condition_type: "AND" | "OR"` field. It is also **not mentioned** in the
  pinned docs page (0 hits for `build_flow_structure`/`FlowStructure`), even
  though the docs page documents `.plot()` (10 hits), which calls into the
  same visualization package internally.
- A plain `@router(...)` with no `emit=` and no `Literal`/`Enum` return-type
  annotation produces **no** statically enumerable route labels
  (`build_flow_structure` logs `"Router events ... are dynamic or not
  statically inferable"`); the router's own possible outputs are then a
  purely execution-class fact. `@router(a, emit=["go_b", "skip_b"])` (or a
  `-> Literal["go_b", "skip_b"]` return annotation — `router.py`'s own
  docstring recommends both) makes the labels and the router→listener edges
  statically visible. Both cases were exercised: the probe deliberately uses
  `emit=[...]` throughout, and this asymmetry is recorded as a bounded fact,
  not exploited silently.

Both `flow_definition()` and `build_flow_structure()` are read from the class
alone — this is what "static" means below, matching Q1's native-versus-public
distinction. See the [common matrix (M1)](../../probes/README.md#common-question-matrix-m1).

## Minimal input

No LLM, no crew, no tools: every flow method is a fixed Python function.
`probes/crewai/flow_probe.py` builds each case's `Flow` class inline in a
factory function — flow methods declared via `@start`/`@listen`/`@router` are
**not inherited into subclasses** by either `flow_definition()` or
`kickoff()` (`_iter_flow_methods` reads only `flow_class.__dict__`, never the
MRO, outside the unrelated "conversational" carve-out); a subclass that
overrides only a class attribute silently keeps zero flow methods. Confirmed
empirically before this was relied on: see [normalization and limitations](#normalization-and-limitations).

Two experiments, six cases:

| Case | Shape | Router returns | What it isolates |
| --- | --- | --- | --- |
| `router-route_a` | router-cardinality | `"route_a"` | two listeners (`listener_one`, `listener_two`) both wired to the same label fire together |
| `router-route_b` | router-cardinality | `"route_b"` | the same two listeners fire zero times — no label match |
| `and-both` | AND join | `"go_b"` (b runs) | `and_(a, b)` after a deterministic a-then-b chain |
| `and-only_a` | AND join | `"skip_b"` (b never runs) | `and_(a, b)` when one input never fires at all |
| `or-both` | OR join | `"go_b"` (b runs) | `or_(a, b)` over the same chain |
| `or-only_a` | OR join | `"skip_b"` (b never runs) | `or_(a, b)` reaching only `a` |

`and-*`/`or-*` share one chain: `a` (`@start`) → `route` (`@router(a,
emit=["go_b","skip_b"])`, hardcoded per case, direct analogue of the
[Airflow P1](../P1/README.md) branch callback) → `b` (`@listen("go_b")`,
which never exists as a triggered event in case `only_a`, not merely a
no-op body) → `join` (`and_(a, b)` or `or_(a, b)`). No timing sleeps;
ordering is causal (a chain), not a race — see the
[racing-groups caution](#normalization-and-limitations) for the concurrent
case this probe does not exercise.

## Evidence classes, kept separate

- **static** — `build_flow_structure(FlowClass)`, normalized (sorted node
  names; edges as `[source, target, condition_type, is_router_event,
  router_event]` tuples, sorted). Identical for both cases of a given
  experiment: it does not depend on which label the router selects.
- **callable** — the router method invoked directly on a freshly constructed,
  not-kicked-off instance (`FlowClass().route()`). Direct evaluation of user
  code, exactly as [Airflow P1](../P1/README.md#evidence-classes-kept-separate)'s
  `callable` section is for `BranchPythonOperator`. It never touches `Flow`'s
  listener-dispatch/trigger-accounting machinery.
- **execution** — `flow.kickoff()`. Each method appends its own name to
  `self.state["log"]`; a name appearing twice is two separate invocations.
  This is the only section that shows actual listener count and causal order.
  `self.state["id"]` (a generated run UUID) is excluded from comparison per
  [evidence conventions](../../docs/evidence.md).

## Expected values (written from source/docs reading, confirmed empirically, then encoded as literal constants)

Predictions came from reading `dsl/_conditions.py`, `visualization/builder.py`,
and the pinned docs page, then were confirmed by direct execution on the
pinned version before being written into `EXPECTED_STATIC` /
`EXPECTED_CALLABLE` / `EXPECTED_EXECUTION` in `probes/crewai/flow_probe.py` —
this repository's runtime engine internals (`runtime/__init__.py` is 4015
lines, undocumented beyond source) are not something this probe claims to
have derived by pure reading alone, unlike Airflow's published trigger-rule
docs. Both predictions matched on first execution; no correction was needed.

## Observed results

Every case ran twice per evidence class (18 case/mode combinations, 36 runs);
every pair's normalized JSON is byte-identical (`cmp` exit 0). All 36 runs
exited zero; `require_equal` raises `AssertionError` (nonzero exit) on any
mismatch, verified with a deliberate corrupted-expectation run under
`python -O` (`and-both`'s `join_count` changed from `1` to `99`): exit 1,
`AssertionError: observation mismatch: ...`.

| Case | Static | Callable | Execution |
| --- | --- | --- | --- |
| `router-route_a` | [run 1](c1-router-route_a-static-1.json), [run 2](c1-router-route_a-static-2.json) | [run 1](c1-router-route_a-callable-1.json), [run 2](c1-router-route_a-callable-2.json) | [run 1](c1-router-route_a-execution-1.json), [run 2](c1-router-route_a-execution-2.json) |
| `router-route_b` | [run 1](c1-router-route_b-static-1.json), [run 2](c1-router-route_b-static-2.json) | [run 1](c1-router-route_b-callable-1.json), [run 2](c1-router-route_b-callable-2.json) | [run 1](c1-router-route_b-execution-1.json), [run 2](c1-router-route_b-execution-2.json) |
| `and-both` | [run 1](c1-and-both-static-1.json), [run 2](c1-and-both-static-2.json) | [run 1](c1-and-both-callable-1.json), [run 2](c1-and-both-callable-2.json) | [run 1](c1-and-both-execution-1.json), [run 2](c1-and-both-execution-2.json) |
| `and-only_a` | [run 1](c1-and-only_a-static-1.json), [run 2](c1-and-only_a-static-2.json) | [run 1](c1-and-only_a-callable-1.json), [run 2](c1-and-only_a-callable-2.json) | [run 1](c1-and-only_a-execution-1.json), [run 2](c1-and-only_a-execution-2.json) |
| `or-both` | [run 1](c1-or-both-static-1.json), [run 2](c1-or-both-static-2.json) | [run 1](c1-or-both-callable-1.json), [run 2](c1-or-both-callable-2.json) | [run 1](c1-or-both-execution-1.json), [run 2](c1-or-both-execution-2.json) |
| `or-only_a` | [run 1](c1-or-only_a-static-1.json), [run 2](c1-or-only_a-static-2.json) | [run 1](c1-or-only_a-callable-1.json), [run 2](c1-or-only_a-callable-2.json) | [run 1](c1-or-only_a-execution-1.json), [run 2](c1-or-only_a-execution-2.json) |

### Router cardinality: one label, two listeners, cardinality is a runtime fact

`router-route_a`'s execution log is `["begin", "route", "listener_one",
"listener_two"]` — both listeners fire from one selected label.
`router-route_b`'s is `["begin", "route"]` — neither fires. The **static**
section is identical between the two cases (both listeners always show
`trigger_methods: ["route_a"]`); only **execution** evidence shows the actual
count (2 vs 0). A declared shape is necessary but not sufficient evidence of
selection cardinality — the same conclusion [Airflow P1](../P1/README.md#the-multiple-selection-counterexample)
and [Dagster P2](../P2/README.md#claim-record) reached by a different
mechanism (multi-target selection, not multi-listener sharing).

### AND/OR convergence: the distinction survives, both structurally and behaviorally

**Structurally** — `and-both`'s static `join` node reads `condition_type:
"AND"`, `trigger_methods: ["a", "b"]`; `or-both`'s reads `condition_type:
"OR"` over the identical `trigger_methods`. The edges each join derives carry
the same literal. This is read from the class alone, via the exported
`build_flow_structure()`, with no kickoff.

**Behaviorally** — over the shared a-then-b chain:

| Case | `and_(a,b)` log | `and_` `join_count` | `or_(a,b)` log | `or_` `join_count` |
| --- | --- | --- | --- | --- |
| `both` | `["a","route","b","join"]` | 1 | `["a","route","join","b"]` | 1 |
| `only_a` | `["a","route"]` (join never fires) | 0 | `["a","route","join"]` | 1 |

AND fires exactly once, only after **both** named triggers have completed,
and never fires when one never completes. OR fires exactly once, as soon as
**the first** of its named triggers completes (note `or-both`'s `join` runs
*before* `b`, immediately after `a` — it does not wait for `b` at all) — and
does not fire again when the second trigger later completes. This is a
clean, bounded pair of convergence policies, not an ambiguity: AND is
sources-required-all, OR is sources-required-any-one, each firing exactly
once per flow run (absent a router-driven "rearm", which this probe does not
exercise — see below).

### The pinned docs' own OR example does not reproduce on 1.15.21

The version-pinned docs page's `or_()` example (`start_method` →
`@listen(start_method) def second_method` → `@listen(or_(start_method,
second_method)) def logger`) claims output:

```
Logger: Hello from the start method
Logger: Hello from the second method
```

Replicating that exact example against the pinned installation instead
produces `logger` firing **once**:

```
Logger: Hello from the start method
```

(`flow.state["log"] == ["start_method", "second_method", ("logger", "Hello
from the start method")]` — `second_method` still ran; `logger` simply never
fired a second time.) This matches this probe's own `or-both` result (OR
fires once, on the first of its named triggers) and is consistent with
`runtime/__init__.py`'s `_fired_or_listeners` set: an OR listener is marked
fired and is only re-armed by `_rearm_or_listeners_for_trigger`, which the
source comment restricts to "When a router emits a fresh signal" — a
cyclic-flow mechanism neither the docs' example nor this probe's chain
exercises. **Documentation supports semantic interpretation but is not
execution evidence** (per [evidence conventions](../../docs/evidence.md)):
this is exactly that gap, reproduced against the exact pinned version,
independent of and in addition to this probe's own six cases.

## The upstream joins contract already models AND; OR is an ordinary edge relationship

Read at `agent-topology` commit `3715dd32a0efc3e7bd500d26d038774d6a37f4e6`
(current `main` at investigation time):

- `spec/agent-topology.schema.json`'s `$defs/join` has exactly three
  properties — `id`, `sources` (`minItems: 2`), `target` — with
  `additionalProperties: false` (only `x-*` extensions allowed). There is no
  `type`/`mode`/`policy` field distinguishing AND from OR.
- `packages/python/spec/src/agent_topology/spec/_joins.py`'s
  `derived_join_edges()` docstring states outright: "these links retain
  **AND convergence semantics**."
- `docs/guides/consuming-documents.md` states the same explicitly: "They
  describe the original join's **AND convergence**: all its sources are
  required."

AND is already implicit in `joins[]` — a join *is* the AND-convergence
construct, not one policy among several. There is no dedicated OR-join
construct; an OR-style convergence (fire when any predecessor completes) is
not a gap in the contract, it is **an ordinary edge relationship** — each
predecessor gets its own direct edge to the same target, matching what this
probe's own OR case does at the CrewAI-execution level (each of `a`/`b`
independently triggers `join` when it completes; nothing enforces they both
must).

## Claim record

**F7 (reserved in [evidence conventions](../../docs/evidence.md#cross-framework-matrix-conventions)
for this investigation) is withdrawn as unsupported: no counterexample of
information loss was reproduced.** `and_()`/`or_()` survive public,
no-kickoff definition inspection as a literal `condition_type` field
(`build_flow_structure()`, exported), and the two convergence policies are
behaviorally distinct and well-defined (all-required-once vs.
any-one-required-once). The existing `joins[]` contract already models AND
convergence by construction; OR requires no new construct, only ordinary
edges. This does not establish that every CrewAI topology maps losslessly
onto `agent-topology` — the `router_events`-visibility asymmetry above is a
real, separate, bounded gap (route labels are only statically enumerable
when the author opts into `emit=`/a `Literal` return annotation) — but it is
not the AND/OR loss this investigation set out to test, and no such loss
was found. F7 remains available as a label if a future case reproduces one;
this record does not claim the hypothesis was ever established, only that
it did not survive here.

## Provenance and reproduction

CPython 3.11.16, uv 0.12.10, macOS arm64; `crewai==1.15.21` (134 locked
distributions, `probes/crewai/requirements.lock`). Each JSON records the
framework/Python versions and SHA-256 hashes of the probe source and
dependency lock at run time.

```sh
uv venv --python 3.11.16 .venvs/crewai
uv pip sync --python .venvs/crewai/bin/python --require-hashes probes/crewai/requirements.lock
uv pip check --python .venvs/crewai/bin/python

mkdir -p .probe-runs
for case in router-route_a router-route_b and-both and-only_a or-both or-only_a; do
  for mode in static callable execution; do
    for n in 1 2; do
      .venvs/crewai/bin/python probes/crewai/flow_probe.py \
        --case "$case" --mode "$mode" \
        --output ".probe-runs/c1-$case-$mode-$n.json"
    done
    cmp ".probe-runs/c1-$case-$mode-1.json" ".probe-runs/c1-$case-$mode-2.json"
  done
done
```

No LLM keys, no network calls beyond the one-time `pip`/`uv` install, and no
scheduler/database process are required. `kickoff()` is a single in-process
call per instance; there is no equivalent of Airflow's `AIRFLOW_HOME` or
Dagster's `DAGSTER_HOME` isolation because CrewAI Flows do not use a local
scheduler database — the one framework-level side effect encountered and
controlled for is documented below.

- [`crewai==1.15.21` on PyPI](https://pypi.org/pypi/crewai/1.15.21/json)
- [crewAI GitHub tag `1.15.21`](https://github.com/crewAIInc/crewAI/tree/1.15.21)
- [Flow DSL source, tag `1.15.21`](https://github.com/crewAIInc/crewAI/blob/1.15.21/lib/crewai/src/crewai/flow/dsl/_conditions.py)
- [Flow visualization builder source, tag `1.15.21`](https://github.com/crewAIInc/crewAI/blob/1.15.21/lib/crewai/src/crewai/flow/visualization/builder.py)
- [Pinned Flows concept docs](https://docs.crewai.com/v1.15.21/en/concepts/flows)
- [`agent-topology` schema at `3715dd32a0efc3e7bd500d26d038774d6a37f4e6`](https://github.com/agent-topology/agent-topology/blob/3715dd32a0efc3e7bd500d26d038774d6a37f4e6/spec/agent-topology.schema.json)
- [`agent-topology` consuming-documents guide at the same commit](https://github.com/agent-topology/agent-topology/blob/3715dd32a0efc3e7bd500d26d038774d6a37f4e6/docs/guides/consuming-documents.md)

### A framework-level side effect, controlled and documented

crewai's own first-run bookkeeping (`crewai_core.user_data`, unrelated to
this repository) writes a small local JSON file — an anonymized
SHA-256(username, machine id) pair and a `trace_consent: false` flag, no
network call — to an app-data directory named by `CREWAI_STORAGE_DIR`
(default: the current directory name) the first time any `Flow.kickoff()`
runs on a machine where it has never run before. `Flow.kickoff()`'s
first-run check consults only an in-process context variable that nothing
outside `Crew.kickoff()` sets in this version — `CREWAI_TRACING_ENABLED`
does not gate it for a bare `Flow`, confirmed by reading
`crewai/events/listeners/tracing/utils.py` and reproducing the panel
appearing regardless of that variable. `probes/crewai/flow_probe.py` sets a
**fixed** `CREWAI_STORAGE_DIR=c1-crewai-probe` so this write, if it has never
happened on the running machine, lands once in one clearly-named directory
under the platform's application-support root (`appdirs.user_data_dir`) —
not one new directory per invocation, and not the file a real project would
use. `OTEL_SDK_DISABLED`, `CREWAI_DISABLE_TELEMETRY`, and
`CREWAI_DISABLE_TRACKING` are all set redundantly; each alone is sufficient
per `crewai_core.telemetry.CoreTelemetry._is_telemetry_disabled()` (read from
installed source) to prevent the separate, real network-capable OTLP
telemetry exporter from ever being constructed. No LLM keys, crew, or tools
are constructed anywhere in this probe, so no model call or agent telemetry
exists to opt out of beyond this.

## Normalization and limitations

JSON sorts node names and edge tuples; it does not deduplicate. Method
invocation order in `execution`'s `log` is retained verbatim (a name appearing
twice is two invocations). The generated run `id` is excluded from comparison.
Wall timestamps, PIDs, and temporary paths stay outside the comparison (none
are collected here; `kickoff()` writes nothing to a database or filesystem
this probe controls beyond `self.state`).

**What this does and does not show.** This shows one router, one pair of
convergence policies, one deterministic a-then-b chain, on crewai 1.15.21 —
not a general rule about every possible condition tree (nested `and_(or_(...),
...)` combinations are untested), every trigger shape (a bare-string trigger
and a single-element `or_()` are visually indistinguishable at the
`build_flow_structure()` layer — both project to `condition_type: "OR"` — this
is a projection-layer simplification, not evidence they behave identically in
every internal code path), or cyclic flows (the `_fired_or_listeners`
re-arming mechanism this probe's docs-mismatch finding surfaces is
specifically for cycles, and is out of scope here). **Racing OR listeners are
untested**: `runtime/__init__.py`'s `_build_racing_groups`/
`_execute_racing_listeners` implement first-wins cancellation specifically for
listeners whose alternative triggers fire from the *same* batch of
concurrently-completing sibling methods (not this probe's sequential chain);
this probe's deterministic a-then-b design was chosen precisely to avoid that
scenario, per the issue's own minimal-input requirement, and the racing
scenario remains a bounded unknown, not a claim about what it does. Flow-class
subclassing losing all flow methods (see [minimal input](#minimal-input)) is
recorded as a framework caution because it shaped this probe's construction,
not as a claim about every crewai version or an intentional design decision
verified with its maintainers. No `agent-topology` document is produced, no
schema or wire-format extension is proposed, and no upstream decision is made.
