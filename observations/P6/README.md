# P6: dynamic output definitions do not say how many mapped instances a run has

Question: how do dynamic output definitions relate to observed mapping keys,
mapped steps, and collect results, for one `DynamicOut` source, one map
operation, and one collect consumer, parameterized to emit 0, 1, or 2 outputs
with explicit stable mapping keys?

Historical baseline: [571e881e6d509b6e26ff8bf14b98e207d12e7ce9](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
These are new internal observations for
[issue #8](https://github.com/agent-topology/agent-topology-testbed/issues/8),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1),
building on [P0](../P0/README.md) (issue #2) and
[P2](../P2/README.md) (issue #4), and blocked by
[P4](../P4/README.md) (issue #6). Historical findings, transcripts, and
gallery artifacts remain unchanged.

## Minimal input

Job `p6_dynamic`, three ops, no nested graph (P4 already covers nested
boundaries; this probe keeps that variable fixed):

- **dynamic_source** — one op with `out=DynamicOut()`, yielding zero, one, or
  two `DynamicOutput` records depending on run config, each with an explicit
  stable `mapping_key` (`"k0"`, `"k1"`) and a value that encodes its position
  (`index + 1`), never a value computed from the key's own name or count.
- **mapped** — one ordinary op wired to `dynamic_source` via `.map(mapped)`,
  multiplying its input by 100.
- **collect** — one ordinary op wired to `mapped` via `.collect()`, returning
  `sorted(values)`.

No external input; no run config besides which mapping keys
`dynamic_source`'s op config asks it to yield:

| Case | `dynamic_source` config `keys` | `DynamicOutput` records |
| --- | --- | --- |
| `0` | `[]` | none |
| `1` | `["k0"]` | one |
| `2` | `["k0", "k1"]` | two |

## Evidence classes, kept separate

Each run records two sections, and no section is used as evidence for
another:

- **static** — `job_name`, `op_names`, `dependencies` (`[producer_node,
  producer_output, consumer_node, input_name, dependency_kind]` tuples, where
  `dependency_kind` is `"direct"` for an ordinary `DependencyDefinition` and
  `"dynamic_collect"` for a `DynamicCollectDependencyDefinition`), and
  `output_is_dynamic` (every op's outputs, by name, with their declared
  `OutputDefinition.is_dynamic` flag). Identical across all three cases: none
  of it depends on `dynamic_source`'s op config. This is read from
  `p6_dynamic.graph` and each node's output/dependency definitions without
  invoking any op's compute function.
- **execution** — `execute_in_process()` results: overall run `success`,
  `step_success_keys`/`step_skipped_keys` (from `DagsterEvent.is_step_success`
  / `is_step_skipped`), `emitted_mapping_keys` (the mapping keys
  `dynamic_source` actually yielded, read from `STEP_OUTPUT` events'
  `step_output_data.mapping_key`, not from the case's config),
  `mapped_step_keys` (the `"mapped[<mapping_key>]"` step identities Dagster
  materializes, one per emitted record), and `dynamic_source_output` /
  `mapped_output` / `collect_output` (from `output_for_node`, recording
  either the returned per-key dict/list or the fact that the call raised —
  see [Normalization and limitations](#normalization-and-limitations)). This
  is the only section that can show cardinality or a concrete mapped-step
  identity, and the only section produced by the execution engine rather
  than static inspection.

`output_is_dynamic["dynamic_source"]["result"] == True` and the
`dynamic_collect` dependency kind on `collect`'s input are static, structural
facts, symmetrically true in all three cases. Neither says how many
`DynamicOutput` records a given run will emit, or what step identities the
mapped op will receive — see [the claim record](#claim-record).

## Expected observations (written before extraction)

Written from Dagster 1.13.22's documented dynamic-mapping semantics
([dynamic API](https://docs.dagster.io/api/dagster/dynamic),
[`dependency.py` source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/dependency.py))
before the extraction logic in `probes/dagster/dynamic.py` was implemented,
as literal `EXPECTED_STATIC` / `EXPECTED_EXECUTION` constants in the script:
each `DynamicOutput` a source op yields gets its own mapped-op step,
identified as `"<op_name>[<mapping_key>]"`; collect blocks on every mapped
step and receives a list; zero `DynamicOutput` records means the mapped op
never gets a step at all (not a skipped one).

| Case | `emitted_mapping_keys` | `mapped_step_keys` | `collect_output` | run `success` |
| --- | --- | --- | --- | --- |
| `0` | `[]` | `[]` | `[]` | true |
| `1` | `["k0"]` | `["mapped[k0]"]` | `[100]` | true |
| `2` | `["k0", "k1"]` | `["mapped[k0]", "mapped[k1]"]` | `[100, 200]` | true |

All three predictions matched the corresponding `execute_in_process()` result
on first run, twice, with no expected-state correction needed.

## Observed results

Every case ran twice per evidence class (`static`, `execution`); each pair's
normalized JSON is byte-identical (`cmp` exit 0). All commands exited zero;
`require_equal` raises `AssertionError` (nonzero exit) on any mismatch,
verified with five deliberate corruption/mismatch runs and a static-mode
execution-attempt guard, all under `python -O` (see
[negative checks](#negative-checks)).

| Case | Static | Execution |
| --- | --- | --- |
| `0` | [run 1](dynamic-0-static-1.json), [run 2](dynamic-0-static-2.json) | [run 1](dynamic-0-1.json), [run 2](dynamic-0-2.json) |
| `1` | [run 1](dynamic-1-static-1.json), [run 2](dynamic-1-static-2.json) | [run 1](dynamic-1-1.json), [run 2](dynamic-1-2.json) |
| `2` | [run 1](dynamic-2-static-1.json), [run 2](dynamic-2-static-2.json) | [run 1](dynamic-2-1.json), [run 2](dynamic-2-2.json) |

### Zero cardinality removes the mapped step entirely, not just its output

At `keys=[]`, `step_success_keys` is exactly `["collect", "dynamic_source"]`:
no `mapped` entry appears in either `step_success_keys` or
`step_skipped_keys`. The mapped op is never instantiated as a step at all —
there is no "zero mapped steps ran" state distinct from "no step exists" in
the event record. Querying `output_for_node("dynamic_source")` or
`output_for_node("mapped")` in this case raises
`DagsterInvariantViolationError` ("No outputs found for output 'result' from
node '<name>'"), rather than returning an empty dict; this probe records the
raise itself (`{"status": "error", "error_type":
"DagsterInvariantViolationError"}`) as the observation, not a caught-and-hidden
empty container. `collect_output` is still `[]` — `collect`'s own op runs
and receives zero elements, which is not the same fact as "the mapped op ran
zero times" above.

### Mapped-step identity is keyed by mapping key, not position or count

`mapped_step_keys` for case `2` is `["mapped[k0]", "mapped[k1]"]`: the
bracketed suffix is the stable mapping key from `dynamic_source`'s
`DynamicOutput`, not an index or the total emitted count. `dynamic_source_output`
and `mapped_output` are themselves dicts keyed by mapping key
(`{"k0": 1, "k1": 2}`, `{"k0": 100, "k1": 200}`), matching the framework's own
per-node accessor rather than a position-based list. `collect_output` is a
plain list (`sorted(values)`, this op's own return value) — collect receives
values, not the mapping keys that produced them; nothing in `collect`'s
static or execution record recovers which key contributed which element,
which is itself a limitation of the flat `.collect()` shape used here.

## Claim record

| Claim | Verdict |
| --- | --- |
| The static `output_is_dynamic` flag plus the `dynamic_collect` dependency kind are sufficient, without executing the job, to predict how many mapped-step instances a given run will have. | **Contradicted.** Both are symmetric across all three cases (see the `static` sections above, byte-identical regardless of case); they mark the wiring as dynamic and fan-in, not how many `DynamicOutput` records any run will emit. Only `execution` distinguishes cardinalities `0`/`1`/`2`. |
| Framework step and event records (`STEP_OUTPUT` mapping keys, `"<op>[<key>]"` step identities, `output_for_node`) can identify emitted cardinality and per-instance identity for a given case, independent of op naming or count. | **Supported.** `emitted_mapping_keys` and `mapped_step_keys` name exactly the mapping keys `dynamic_source` yielded in each case, read from event/step identity rather than a computed count or op name pattern. |
| Zero emitted `DynamicOutput` records behaves like "the mapped op ran and produced nothing" (an empty-container case). | **Contradicted.** The mapped step is absent from the step record entirely, and `output_for_node` raises rather than returning an empty dict — a distinct state from a mapped op that ran once with a value of `None` or an empty payload. |
| This generalizes beyond one source op with two possible mapping keys, one map operation, one flat collect, one op-config-driven cardinality selection, in one in-process ephemeral run. | **Unresolved.** Nested dynamic mapping, dynamic mapping crossing a graph boundary (as opposed to P4's non-dynamic nested case), larger cardinalities, dynamic partitions/assets, other executors, concurrent mapped-step scheduling, and other Dagster versions are untested and out of scope (see [Non-goals](https://github.com/agent-topology/agent-topology-testbed/issues/8)). |

## Provenance and reproduction

See [exact setup/run commands](../../probes/README.md#dagster-dynamic-mapping-run-p6).
Verified with CPython 3.11.16, uv 0.12.10, macOS arm64; Dagster 1.13.22 (48
locked distributions), same environment and lock as
[P0](../P0/README.md)/[P2](../P2/README.md)/[P4](../P4/README.md). Each JSON
records the framework/Python versions and SHA-256 hashes of the probe source
and dependency lock at run time.

Verification on 2026-09-11 (America/New_York): `uv pip check` reported all 48
Dagster packages compatible.

- [Dagster dynamic-mapping API](https://docs.dagster.io/api/dagster/dynamic)
- [execution API](https://docs.dagster.io/api/dagster/execution)
- [`dependency.py` 1.13.22 source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/dependency.py)
  (`DependencyDefinition`, `DynamicCollectDependencyDefinition`)
- [`output.py` 1.13.22 source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/output.py)
  (`OutputDefinition.is_dynamic`)
- [`DagsterEvent` 1.13.22 source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/events/__init__.py)

### Negative checks

Six deliberate failure-path checks, all under `python -O` in separate
processes, none writing an output file:

- Replaced the `dynamic_collect` dependency kind on `collect`'s input with
  `"direct"` (via `runpy` and the loaded `main` function's `__globals__`,
  since `runpy.run_path` returns a snapshot copy rather than the live
  namespace `main` closes over): exited 1 with an `AssertionError`
  observation mismatch.
- Replaced `dynamic_source`'s `output_is_dynamic` flag with `False`: same.
- Set case `2`'s mapping keys to a duplicate (`["k0", "k0"]`): exited 1 with
  a **framework-raised** `DagsterInvariantViolationError` ("yielded a
  DynamicOutput with mapping_key 'k0' multiple times"), before this script's
  own assertions ever run — a duplicate mapping key is a framework-enforced
  invariant on a single source's yields, not a state this probe's own
  `require_equal` needs to catch. See [`test_dynamic.py`](../../probes/dagster/test_dynamic.py).
- Set case `2`'s mapping keys to `["k0"]` only (a wrong cardinality against
  the case's own literal expectation): exited 1 with an `AssertionError`
  observation mismatch.
- Monkeypatched `importlib.metadata.version("dagster")` to report
  `"unsupported"`: exited 1 with an `AssertionError` before any job was
  constructed.
- A standalone `--mode static` run with `JobDefinition.execute_in_process`
  replaced by a function that raises: exited 0, confirming static mode never
  reaches execution.

## Normalization and limitations

JSON sorts op names, dependency tuples, mapping keys, and step-key lists; it
does not deduplicate. Mapping keys, step identities, run success, and
computed output values are retained. Generated run IDs, wall timestamps,
durations, PIDs, log text, and temporary paths stay outside the comparison.

**What this does and does not show.** This shows one `DynamicOut` source, one
map operation, and one flat collect consumer, at three explicit cardinalities,
on `execute_in_process()` with an ephemeral instance against Dagster 1.13.22
— not a general rule about dynamic mapping crossing a nested graph boundary
(untested; P4 covers nested boundaries without dynamic outputs), larger
cardinalities, dynamic partitions or assets (explicit non-goals), other
executors, or another Dagster version. `execute_in_process()` runs steps
serially in one process; nothing here demonstrates or measures wall-clock
concurrency between `mapped[k0]` and `mapped[k1]`, only that both reach
`state: success` in the same run (see
[P0](../P0/README.md#normalization-and-limitations) and
[P2's identical caution](../P2/README.md#the-fan-out-control-did-not-vary-with-the-case)).
No `agent-topology` document is produced, no schema or wire-format extension
is proposed, and no upstream decision is made.

## Claim disposition

The [completed-cohort ledger](../../findings/completed-cohort-dispositions.md#p6)
classifies this observation’s material claims, their finding links or reasons for
non-promotion, and any specific minimal follow-up. Raw evidence remains unchanged.

**Provenance qualification (2026-09-12, #29):** The saved `source_sha256`
differs from the checked-in probe source, although the saved measured sections
match its literal assertions. See the ledger’s [provenance limits](../../findings/completed-cohort-dispositions.md#provenance-limits)
for exact digests and the minimal follow-up. This is not a fresh reproduction.
