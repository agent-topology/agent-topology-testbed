# P2: optional outputs are a per-run fact, not a static one

Question: for a Dagster op with two `Out(is_required=False)` outputs feeding two
downstream consumers, which facts about which outputs will be emitted are visible
statically, which require executing the job, and does an ordinary required-output
fan-out in the same job behave differently?

Historical baseline: [571e881e6d509b6e26ff8bf14b98e207d12e7ce9](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
These are new internal observations for
[issue #4](https://github.com/agent-topology/agent-topology-testbed/issues/4),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1),
blocked by and building on [P0](../P0/README.md) (issue #2). Historical findings,
transcripts, and gallery artifacts remain unchanged.

## Minimal input

Job `p2_conditional`, six ops:

- **conditional_source** — one op, two optional outputs
  (`Out(is_required=False)`): `branch_a`, `branch_b`.
- **consumer_branch_a**, **consumer_branch_b** — one consumer per optional
  output, each declared with an ordinary required input.
- **fanout_source** — an ordinary op with a single, ordinary (default
  `is_required=True`) output, feeding two consumers on the same edge shape as
  above: the required-output fan-out control named in the issue.
- **consumer_fanout_a**, **consumer_fanout_b** — its two consumers.

No external input; no run config besides which of `conditional_source`'s
outputs to yield. Three cases, differing only in that op-config selection:

| Case | `conditional_source` config `emit` | Outputs yielded |
| --- | --- | --- |
| `none` | `[]` | neither |
| `single` | `["branch_a"]` | `branch_a` only |
| `multiple` | `["branch_a", "branch_b"]` | both |

`fanout_source` is not parameterized by case: it always returns a value, on
every case, because its output is not optional.

## Evidence classes, kept separate

Each run records two sections, and no section is used as evidence for another:

- **static** — `job_name`, `op_names`, `dependencies` (`[producer_op,
  output_name, consumer_op, input_name]` tuples), and `output_is_required`
  (every op's outputs, by name, with their declared `is_required` flag).
  Identical across all three cases: none of it depends on `conditional_source`'s
  op config. This is read from `p2_conditional.graph` and each node's
  `OutputDefinition`s without invoking any op's compute function.
- **execution** — `execute_in_process()` results: overall run `success`, the
  `emitted_outputs` `conditional_source` actually yielded (read from
  `STEP_OUTPUT` events, not from the case's config), `step_success_keys` and
  `step_skipped_keys` (from `DagsterEvent.is_step_success` /
  `is_step_skipped`), and `consumer_outputs` for whichever consumers produced a
  value. This is the only section that can show a step skipped versus run, and
  the only section produced by the execution engine rather than static
  inspection.

`is_required=False` on `branch_a`/`branch_b` is a static, structural fact,
symmetrically true in all three cases. It does not by itself say which of the
three cases occurred in a given run, or which consumers executed — see
[the claim record](#claim-record).

## Expected observations (written before extraction)

Written from Dagster 1.13.22's documented optional-output semantics
([`Out`](https://docs.dagster.io/api/dagster/ops#dagster.Out),
[`OutputDefinition` source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/output.py))
before the extraction logic in `probes/dagster/conditional.py` was implemented,
as literal `EXPECTED_STATIC` / `EXPECTED_EXECUTION` constants in the script: an
`Out(is_required=False)` output that is not yielded causes every downstream step
that depends on it to be skipped, not failed, and the run itself still succeeds;
an ordinary output has no such skip path.

| Case | `consumer_branch_a` | `consumer_branch_b` | `fanout_source` | `consumer_fanout_a` | `consumer_fanout_b` | run `success` |
| --- | --- | --- | --- | --- | --- | --- |
| `none` | skipped | skipped | success | success | success | true |
| `single` | success | skipped | success | success | success | true |
| `multiple` | success | success | success | success | success | true |

All three predictions matched the corresponding `execute_in_process()` result on
first run, twice, with no expected-state correction needed.

## Observed results

Every case ran twice per evidence class (`static`, `execution`); each pair's
normalized JSON is byte-identical (`cmp` exit 0). All commands exited zero;
`require_equal` raises `AssertionError` (nonzero exit) on any mismatch, verified
with a deliberate corrupted-expectation run and a corrupted-version run, both
under `python -O` (see [negative checks](#negative-checks)).

| Case | Static | Execution |
| --- | --- | --- |
| `none` | [run 1](conditional-none-static-1.json), [run 2](conditional-none-static-2.json) | [run 1](conditional-none-1.json), [run 2](conditional-none-2.json) |
| `single` | [run 1](conditional-single-static-1.json), [run 2](conditional-single-static-2.json) | [run 1](conditional-single-1.json), [run 2](conditional-single-2.json) |
| `multiple` | [run 1](conditional-multiple-static-1.json), [run 2](conditional-multiple-static-2.json) | [run 1](conditional-multiple-1.json), [run 2](conditional-multiple-2.json) |

### The fan-out control did not vary with the case

`fanout_source`, `consumer_fanout_a`, and `consumer_fanout_b` appear in
`step_success_keys` in all three cases, unconditionally. Their wiring is an
ordinary required-output edge, not a conditional one: nothing about them changes
whether `conditional_source` emits zero, one, or two outputs. In-process
execution ran all three cases' steps serially in one process; both fan-out
consumers reaching `STEP_SUCCESS` in the same run shows completion, not
concurrency (see [Normalization and limitations](#normalization-and-limitations),
and [P1's identical caution](../P1/README.md#the-trigger-rule-comparison) about
its own trigger-rule joins).

### Skip identity tracks the specific output, not the op or its name

`consumer_branch_a` and `consumer_branch_b` are structurally symmetric ops with
symmetric names; the only thing distinguishing their fate per case is which
named output `conditional_source` yielded that run. `step_skipped_keys` and
`emitted_outputs` are read from framework events keyed by step and output
identity (`DagsterEvent.is_step_skipped`, `STEP_OUTPUT` events'
`step_output_handle.output_name`), never from the op or output's name matching
a pattern, and never from `conditional_source`'s op type.

## Claim record

| Claim | Verdict |
| --- | --- |
| Static declared dependencies plus each output's `is_required` flag are sufficient, without executing the job, to predict which specific outputs a given run will emit. | **Contradicted.** `is_required=False` is symmetric across all three cases (see the `static` sections above, byte-identical regardless of case); it marks an output as *optional*, not which run-time selection occurred. Only `execution` distinguishes `none`/`single`/`multiple`. |
| Framework step results (`STEP_SUCCESS` / `STEP_SKIPPED`) can identify which consumers executed for a given case, independent of op naming or op type. | **Supported.** `step_skipped_keys` names exactly the consumers of outputs `conditional_source` did not yield, in all three cases, read from event step-key/output identity rather than op names or `OutputDefinition` type. |
| An ordinary required-output fan-out completing both consumers is evidence that Dagster executes them concurrently. | **Contradicted, by design.** `execute_in_process()` here runs everything serially in one process (see [P0](../P0/README.md#normalization-and-limitations)); both `consumer_fanout_a`/`consumer_fanout_b` reaching `success` shows the control ran unconditionally, not that it ran at the same wall-clock instant as anything else. |
| This generalizes beyond one op with two optional outputs and one ordinary required-output control, in one in-process ephemeral run. | **Unresolved.** Multiple optional outputs on the same op interacting with joins, nested graphs, dynamic output mapping, other executors, and other Dagster versions are untested and out of scope (see [Non-goals](https://github.com/agent-topology/agent-topology-testbed/issues/4)). |

## Provenance and reproduction

See [exact setup/run commands](../../probes/README.md#dagster-conditional-outputs-run-p2).
Verified with CPython 3.11.16, uv 0.12.10, macOS arm64; Dagster 1.13.22 (48
locked distributions), same environment and lock as [P0](../P0/README.md). Each
JSON records the framework/Python versions and SHA-256 hashes of the smoke
source and dependency lock at run time.

Verification on 2026-09-11 (America/New_York): `uv pip check` reported all 48
Dagster packages compatible.

- [`Out` / `OutputDefinition` 1.13.22 source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/output.py)
- [execution API](https://docs.dagster.io/api/dagster/execution)
- [`GraphDefinition` 1.13.22 source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/graph_definition.py)
- [`DagsterEvent` 1.13.22 source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/events/__init__.py)

### Negative checks

Two deliberate failure-path checks, both under `python -O` in separate
processes, neither writing an output file:

- Replaced `EXPECTED_STATIC` (via `runpy` and the loaded `main` function's
  `__globals__`, since `runpy.run_path` returns a snapshot copy rather than the
  live namespace `main` closes over) with an empty dict: exited 1 with an
  `AssertionError` observation mismatch.
- Monkeypatched `importlib.metadata.version("dagster")` to report `"unsupported"`:
  exited 1 with an `AssertionError` before any job was constructed.

## Normalization and limitations

JSON sorts op names, dependency tuples, and step-key lists; it does not
deduplicate. Output names, step keys, run success, and computed consumer output
values are retained. Generated run IDs, wall timestamps, durations, PIDs, log
text, and temporary paths stay outside the comparison.

**What this does and does not show.** This shows one op with two optional
outputs, two matching consumers, and one ordinary required-output fan-out
control, on `execute_in_process()` with an ephemeral instance against Dagster
1.13.22 — not a general rule about every output-skip interaction (partial input
availability on a multi-input consumer, `Nothing`-typed dependencies, dynamic
outputs, and asset-based graphs are untested), or another Dagster version.
`execute_in_process()` runs steps serially in one process; nothing here
demonstrates or measures wall-clock concurrency between `consumer_fanout_a` and
`consumer_fanout_b`, only that both reach `state: success` in the same run. No
`agent-topology` document is produced, no schema or wire-format extension is
proposed, and no upstream decision is made.

## Claim disposition

The [completed-cohort ledger](../../findings/completed-cohort-dispositions.md#p2)
classifies this observation’s material claims, their finding links or reasons for
non-promotion, and any specific minimal follow-up. Raw evidence remains unchanged.
