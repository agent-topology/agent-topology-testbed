# S1: ASL declarations as a control for branch and nested-graph semantics

Question: when a source document explicitly declares control-flow meaning —
state type, ordered rule selection, declared-all-branches convergence, mapped
expansion versus concurrency bound — which of that meaning survives as a
representable distinction against the current topology contract, and which
remains an open question the format itself does not settle?

Historical baseline: [571e881e6d509b6e26ff8bf14b98e207d12e7ce9](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
This is a new internal observation for
[issue #14](https://github.com/agent-topology/agent-topology-testbed/issues/14),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1)
and the [common question matrix](../../probes/README.md#common-question-matrix-m1)
(issue #12). It does not depend on CrewAI ([#13](https://github.com/agent-topology/agent-topology-testbed/issues/13))
and does not revalidate any P0–P6 evidence.

AWS Step Functions is a **general workflow engine**, not an agent framework —
its role here is as a *control*: a source language that states its own
control-flow meaning explicitly (a distinct `Choice`/`Parallel`/`Map` state
type per construct, not one generic branching primitive), against which the
other probed frameworks' inferred or partially-declared structure can be
compared. See [Comparison against the current topology contract](#comparison-against-the-current-topology-contract).

Unlike every other probe in this repository, Amazon States Language (ASL) has
no SDK, package, or execution engine to install locally: a state machine is a
plain JSON document, interpreted only by the AWS Step Functions service. This
probe parses that document with Python's standard-library `json` module and
performs its own bounded structural checks — it never calls AWS, never
evaluates a `Choice` rule's comparison expression, and implements no
simulator. See [Normalization and limitations](#normalization-and-limitations)
for exactly what that does and does not establish.

## Minimal input

Four small JSON definitions under [`probes/step-functions/fixtures/`](../../probes/step-functions/fixtures/),
each independently minimal for the fact it is meant to isolate:

- [`choice.json`](../../probes/step-functions/fixtures/choice.json) — a
  `Choice` state with two ordered rules (`StringEquals` on `$.status`) and an
  explicit `Default` fallback, feeding three terminal `Pass` states.
- [`parallel.json`](../../probes/step-functions/fixtures/parallel.json) — a
  `Parallel` state with two one-state `Pass` branches that **reuse the same
  local state name** (`"Step"` in both), converging into one downstream
  `Pass` state.
- [`map.json`](../../probes/step-functions/fixtures/map.json) — an inline
  `Map` state (`ItemProcessor` with `ProcessorConfig.Mode: "INLINE"`) with a
  one-state `ItemProcessor`, `ItemsPath: "$.items"`, and an explicit
  `MaxConcurrency: 1`.
- Two negative fixtures, each isolating one reference failure: [`invalid_missing_target.json`](../../probes/step-functions/fixtures/invalid_missing_target.json)
  (a `Next` naming a state that exists nowhere in the document) and
  [`invalid_cross_boundary.json`](../../probes/step-functions/fixtures/invalid_cross_boundary.json)
  (a `Parallel` branch state's `Next` naming a state defined only in the
  parent scope, not in the branch's own `States`).

## Evidence class

**Static only.** Every record below is `"evidence_class": "static"` — read
from the parsed JSON document with zero execution, zero AWS request, and no
expression evaluation. This probe has no callable or execution section: there
is no local callable to invoke and no local engine to execute against (see
[evidence conventions](../../docs/evidence.md)). Successful JSON parsing and
this probe's own structural checks are recorded as `json_parsed` and the
`scopes` list, separately from the `probe_disclaimer` field every record
carries, naming exactly what neither of those facts proves: not authoritative
ASL validation (the real AWS validator implements checks this probe does
not), and not execution evidence.

## Expected observations (written before extraction)

Written from [the ASL spec](https://states-language.net/spec.html) (retrieved
2026-09-11; the spec carries no dated revision tag, so retrieval date stands
in for one) before `probes/step-functions/asl_probe.py`'s extraction logic
ran against the fixtures, as the literal `EXPECTED_FACTS` constants in the
script:

| Fixture | Expected scopes | Expected distinguishing fact |
| --- | --- | --- |
| `choice` | 1 (`root`) | `choice_rules["CheckStatus"].ordered_targets == ["Approved", "Rejected"]`, `default == "Pending"`, kept as a list in declared order |
| `parallel` | 3 (`root`, `root/RunBoth/branch0`, `root/RunBoth/branch1`) | both branch scopes have `state_names == ["Step"]`; `root`'s own `state_names` never includes `"Step"` |
| `map` | 2 (`root`, `root/ProcessItems/item_processor`) | `map_config["ProcessItems"] == {"items_path": "$.items", "max_concurrency": 1, "mode": "INLINE", "array_length_known": false}` |

All three predictions matched the corresponding extraction on first run,
twice, with no expected-state correction needed.

## Observed results

Every positive fixture ran twice; each pair's normalized JSON is
byte-identical (`cmp` exit 0). All commands exited zero;
`require_equal` raises `AssertionError` (nonzero exit) on any mismatch,
verified with four deliberate corruption checks plus the two negative
fixtures' own structural failures, all under `python -O` (see
[negative checks](#negative-checks)).

| Fixture | Run 1 | Run 2 |
| --- | --- | --- |
| `choice` | [run 1](choice-1.json) | [run 2](choice-2.json) |
| `parallel` | [run 1](parallel-1.json) | [run 2](parallel-2.json) |
| `map` | [run 1](map-1.json) | [run 2](map-2.json) |

### Choice uses ordered rule selection, with Default as a distinct fallback slot

`choice_rules["CheckStatus"]` records `ordered_targets` as a list, `["Approved",
"Rejected"]`, in the exact order the `Choices` array declares them — never
sorted — because ASL evaluates `Choices` in list order and the first matching
rule wins ([spec §"Choice Rules"](https://states-language.net/spec.html)).
`Default` (`"Pending"`) is recorded in a separate field, not appended as a
third ordered target: it is a fallback reached only when every preceding rule
fails to match, a structurally different role than "one more alternative."
This probe records the declared order and the separate fallback slot; it does
not evaluate `$.status` against any input, so which target a given execution
selects is outside this evidence class entirely — an execution question, not
a static one.

### Parallel branches keep independently scoped state identity, even with an identical local name

Both branches of `RunBoth` declare a state literally named `"Step"`. The
extracted `state_names` for `root/RunBoth/branch0` and
`root/RunBoth/branch1` are each exactly `["Step"]` — two distinct states,
neither merged nor renamed to disambiguate — while `root`'s own
`state_names` is `["Converge", "RunBoth"]` and never includes `"Step"` at
all. Branch scoping is not a naming convention this probe applies; it falls
directly out of extracting each branch's own `States` object independently,
per [spec §"Parallel State"](https://states-language.net/spec.html): a branch
is its own complete state machine, and nothing above generalizes into it or
below leaks out of it. `parallel_branch_counts["RunBoth"] == 2` is the
declared-fan-out fact: both branches are declared, and per the state type's
own semantics the `Parallel` state runs all of them — not a choice among
alternatives the way `Choice`'s rules are. Whether both branches actually
execute concurrently, serially, or with what failure/retry semantics on a
branch fault is documented behavior this probe does not measure (see
[Normalization and limitations](#normalization-and-limitations)); the state
declares "all branches, converge after" regardless of how any engine
schedules them.

### Map cardinality and concurrency are declared as two separate, unrelated facts

`map_config["ProcessItems"]` carries `max_concurrency: 1` and
`array_length_known: false` as sibling fields, not one field standing in for
the other. `MaxConcurrency` bounds how many item-processor invocations may
run at once; `ItemsPath` names where the runtime array lives, and this probe
never reads or infers that array's length from the template — there is no
array in the static document to count. Setting `MaxConcurrency: 1` does not
change the state's own type or its `ItemProcessor` structure: `ProcessItems`
is still a `Map` state with one `ItemProcessor` template, extracted as one
child scope (`root/ProcessItems/item_processor`) exactly as it would be at
any other `MaxConcurrency` value. **A Map state forcing serial invocation via
`MaxConcurrency: 1` is still mapped expansion** — the same per-item template
applied across however many runtime items exist — not evidence that mapping
collapses into a single ordinary invocation. Which is exactly the
Dagster P6 finding this parallels: [P6](../P6/README.md#claim-record) found
static dynamic-output/collect wiring symmetric across cardinalities `0`/`1`/`2`,
with only execution distinguishing them; here, `MaxConcurrency` is an
orthogonal declared bound on top of the same undetermined-cardinality
situation, one static axis further from anything this probe can resolve
without an execution engine.

## Comparison against the current topology contract

- **F1 ([fan-out semantics](../../findings/F1-fan-out-semantics/README.md))
  — representable distinction, not a loss, at the ASL source.** F1's claim is
  that a 0.1 topology document cannot say whether several destinations out of
  a branching node are alternatives or run together, because the format
  represents convergence (`joins[]`) but has no divergence construct at all.
  ASL's *source* document does not have this ambiguity: `Choice` and
  `Parallel` are distinct state types with distinct declared semantics
  (exclusive ordered selection versus declare-all-branches-and-converge).
  A producer that reads the ASL `Type` field and preserves it (rather than
  flattening both to generic fan-out edges) has the information F1 says the
  target format cannot express on its own. This is not a new finding against
  F1 — it does not change what the topology format's core fields can carry —
  it locates the loss precisely at the producer boundary: the ambiguity F1
  describes is created by discarding the source's own declared distinction,
  not by any necessity of the domain.
- **F3 ([opaque subgraph](../../findings/F3-opaque-subgraph/README.md)) — ASL
  is a stronger positive control than Airflow/Dagster gave.** F3's claim is
  that a topology node cannot be marked as containing a nested graph at
  `depth: 0`. Airflow's `TaskGroup` and Dagster's nested `GraphDefinition`
  showed nested boundaries are inspectable via public APIs without expanding
  them (P3, P4), which already narrows F3 to a target-format gap rather than
  a universal source-side one. ASL narrows it further: a `Parallel` branch or
  a `Map` `ItemProcessor` is not reached through any API at all — it is
  ordinary nested JSON (`Branches[i].States`, `ItemProcessor.States`), fully
  present in the same document, with zero execution. There is no
  "documented-public accessor" gap to record here, because there is no
  accessor; the nested structure is the document. A producer that fails to
  mark a `Parallel`/`Map` node's subgraph membership at the target format's
  `depth: 0` is discarding information that was maximally available at the
  source, not information that was hard to reach.
- **Convergence.** `RunBoth`'s `Next: "Converge"` and both branches
  terminating (`End: true`) is a declared convergence point after a declared
  fan-out — structurally the shape F1 says the format already models well.
  This probe does not execute, so it does not show what happens if a branch
  fails before reaching convergence; ASL's own documented failure semantics
  (a failed branch fails the whole `Parallel` state, subject to `Catch`/`Retry`,
  neither used in this fixture) are cited, not measured, per the issue's
  explicit scope.

## Common question matrix (M1)

See [the matrix](../../probes/README.md#common-question-matrix-m1) for the
full per-framework table; this section is the ASL-specific backing for that
row.

| Q | Answer | Basis |
| --- | --- | --- |
| Q1 | **support** | The whole document parses with `json.loads` alone — no decorator execution, no SDK import, stronger than Airflow/Dagster's "no scheduler call" support, since there is no framework runtime to import at all. |
| Q2 | **support** | State names and `Next`/`Default`/`Choices[].Next` targets are explicit JSON keys, never inferred from naming convention or side channel. |
| Q3 | **partial** | `Choice`'s ordered-rule-plus-Default *mechanism* is a static, declared exclusive-selection structure — stronger than Airflow's symmetric declared downstream set. Which rule a given input actually selects is unevaluated here (no expression evaluator; explicit non-goal), so selection-cardinality-for-an-input remains untested, same separation as Airflow P1/Dagster P2. |
| Q4 | **partial** | `Parallel`'s declared semantics (all branches run, state converges/fails as a unit) are cited from the spec, not executed or measured; no local engine exists to execute against, so this is documentation-class evidence only, not the execution-confirmed partial Airflow/Dagster recorded. |
| Q5 | **support** | `Branches`/`ItemProcessor` nested boundaries are visible as ordinary JSON, with no API-coverage gap analogous to Dagster P4's undocumented-`@public` finding — there is no API layer between the document and this probe. |
| Q6 | **partial** | No fixture here constructs an interrupt/HITL case (out of this issue's scope). Per the issue's own framing, ASL's `.waitForTaskToken` service-integration suffix on a `Task` state's `Resource` field is a structurally nameable callback-task pattern in the spec itself, citable without invoking any service; this probe does not add a `Task` state or exercise it, so this remains a documented-only, not fixture-backed, partial answer. |
| Q7 | **partial** | State names are definition-level, scope-qualified identifiers (`root/RunBoth/branch0/Step` distinct from `root/RunBoth/branch1/Step`), and each pair of runs above is byte-identical — showing the identifier did not change between those two runs, not that it is stable across arbitrary future edits. ASL has no execution here and thus no generated execution ID to separate from it in this probe; the issue frames Q7 for ASL as about scoped definition names specifically, not execution IDs, which this probe answers on those terms only. |

## Negative checks

Six deliberate failure-path checks, all under `python -O`, none writing an
output file (see [`test_asl_probe.py`](../../probes/step-functions/test_asl_probe.py)):

- `invalid_missing_target.json`: `Start`'s `Next` names `"Nonexistent"`,
  absent from the document's only scope. Exited nonzero with
  `ASLReferenceError`.
- `invalid_cross_boundary.json`: a `Parallel` branch's own `Step` state's
  `Next` names `"Converge"`, which exists only in the parent scope, not in
  the branch's own `States`. Exited nonzero with `ASLReferenceError` —
  the same general containment check that rejects
  `invalid_missing_target.json` catches this without any special-cased
  cross-scope logic: a branch is validated against only its own `States`
  dict.
- Reordered `choice`'s expected `ordered_targets` to `["Rejected",
  "Approved"]` (the reverse of the fixture's actual declared order): exited
  nonzero with an `AssertionError` observation mismatch.
- Renamed one `parallel` branch's expected `scope_id` to collide with the
  other's: exited nonzero with an `AssertionError` observation mismatch.
- Changed `map`'s expected `max_concurrency` to `5` against the fixture's
  actual `1`: exited nonzero with an `AssertionError` observation mismatch.
- Monkeypatched `choice.json`'s loaded document to set `CheckStatus`'s
  `Type` to `"Bogus"`: exited nonzero with `ASLStructureError`, before any
  `EXPECTED_FACTS` comparison ran.

## Normalization and limitations

JSON sorts state names, terminal-state lists, and scope lists by `scope_id`;
it does not deduplicate. Declared `Choices` order, `Default` as a separate
field, branch/item-processor scope identity, and `MaxConcurrency` are
retained verbatim. There is no wall time, run ID, or process ID to exclude —
this probe never executes anything.

**What this does and does not show.** This shows that three small, hand-built
ASL documents parse and structurally check under Python's standard-library
JSON parser with the checks this probe implements — not a comprehensive ASL
validator (no `Parameters`/`ResultPath`/`OutputPath`/`Retry`/`Catch` checking,
no JSONPath validation, no `Payload` template checking), not an expression
evaluator (no `Choice` rule is ever evaluated against an input), not an AWS
Step Functions execution or simulator, and not a claim about what any real
Step Functions deployment would schedule, retry, or run concurrently. No
`agent-topology` document is produced, no schema or wire-format extension is
proposed, and no upstream or producer decision is made.

## Provenance and reproduction

See [exact setup/run commands](../../probes/README.md#reproduce-s1). No
package install, lock file, or virtual environment is required — the probe
uses only Python's standard library. Verified with CPython 3.14.7 on macOS
arm64 on 2026-09-11 (America/New_York); the script itself only requires
Python 3.8 or newer (checked explicitly, see `asl_probe.py`). Each JSON
record carries the probe source's own SHA-256 and the fixture's SHA-256 at
run time.

- [states-language.net spec](https://states-language.net/spec.html) —
  retrieved 2026-09-11; no dated revision tag published.
- [AWS Step Functions: Parallel state](https://docs.aws.amazon.com/step-functions/latest/dg/state-parallel.html)
- [AWS Step Functions: inline Map state](https://docs.aws.amazon.com/step-functions/latest/dg/state-map-inline.html)

## Claim disposition

The [completed-cohort ledger](../../findings/completed-cohort-dispositions.md#s1)
classifies this observation’s material claims, their finding links or reasons for
non-promotion, and any specific minimal follow-up. Raw evidence remains unchanged.

**Correction (2026-09-12, #29):** The ledger explicitly narrows the historical
comparison above: P4 does not establish documented-public-only enumeration,
P3 grouping does not prove compiled-child identity, and available ASL declarations
do not themselves reproduce target-format loss. F1/#28 and F7/#27 now own the
fan-out and convergence arguments; see the [S1 dispositions](../../findings/completed-cohort-dispositions.md#s1).
