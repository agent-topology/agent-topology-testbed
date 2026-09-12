# P4: nested invocation boundaries and two-input convergence

Question: which nested invocation identities and input/output boundaries are
visible through Dagster's APIs, and what does a two-input dependency establish
about execution?

This is new evidence for [issue #6](https://github.com/agent-topology/agent-topology-testbed/issues/6)
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1),
building on [P2](../P2/README.md) and comparing with [P3](../P3/README.md).
The beta.2 baseline `571e881e6d509b6e26ff8bf14b98e207d12e7ce9`, historical
findings, transcripts, and gallery remain unchanged.

## Minimal input and independent predictions

The measurement is boundary/identity visibility and observed consumer values.
The input is one parent graph `p4_nested`, two aliases (`left`, `right`) of
the **same** child `GraphDefinition`, and one two-input op `consume`. Each
child contains `seed(value) = value + 1` followed by
`finish(value) = value * 10`. Both aliases reuse those exact local names.
Top-level inputs are `left_seed=1`, `right_seed=2`; there are five executable
op invocations, with no extra source or reporting ops.

Literal `EXPECTED_STATIC` and `EXPECTED_EXECUTION` constants precede graph
construction and extraction in [nested.py](../../probes/dagster/nested.py).
They are not calculated from the observed definitions:

- Seven invocation paths: `consume`, `left`, `left.finish`, `left.seed`,
  `right`, `right.finish`, `right.seed`. Both graph invocations refer to
  definition `child`; the four internal op invocations remain distinct.
- Parent membership is `consume`, `left`, `right`; each child has its own
  scoped `seed` and `finish`. Each internal edge connects that invocation's
  `seed.result` to `finish.value`.
- Parent inputs map `left_seed` to `left.value` and `right_seed` to
  `right.value`. Each child's `value` maps to its own `seed.value`, and its
  graph `result` maps from its own `finish.result`.
- Two parent dependencies connect `left.result` to `consume.left` and
  `right.result` to `consume.right`. The parent's `result` maps from
  `consume.result`.
- Execution produces intermediate values `2` and `3`, child outputs `20`
  and `30`, and consumer output `{"left": 20, "right": 30, "sum": 50}`.
  The consumer echoes its received arguments, independently of the expected
  values or supplied top-level inputs. All five op steps succeed; none skips
  or fails.

## API coverage and bounded unsupported inspection

This probe distinguishes documented public APIs from non-underscore,
source-visible accessors. **It does not establish complete extraction using
only documented public APIs.** The latter accessors are supplemental evidence,
not a private-API adapter or an assertion of compatibility guarantees. No
`dagster._*` imports or underscore data attributes are used by the probe.

| Requested fact | Attempted readback | Result and limitation |
| --- | --- | --- |
| Invocation paths, internal membership, definition reuse | `GraphDefinition.nodes`, `Node.name`, `Node.definition`, definition `name` | Observed using non-underscore source-visible accessors; documented-public enumeration remains unsupported by this attempt. `nodes` lacks `@public` in the installed source. |
| Parent and internal dependencies | `GraphDefinition.dependencies`, `NodeInvocation.name/alias`, `DependencyDefinition.node/output` | Observed with all ports and scopes; the getter lacks `@public`. Documented-public-only dependency readback remains unsupported by this attempt. |
| Input/output boundary mappings | `GraphDefinition.input_mappings/output_mappings` and `InputMapping`/`OutputMapping` fields | Observed through documented public mapping APIs. Local endpoints are qualified with the invocation scope obtained above; this is derived scoping, not a native fully qualified mapping field. |
| Scoped execution identity and results | `execute_in_process`, `ExecuteInProcessResult.all_events`, `output_for_node`, `output_value` | Observed in execution mode. Step keys come from framework events; both graph aliases and each internal op can be addressed for output retrieval. |
| Consumer's two actual input values | Consumer echoes its arguments in its framework-managed output | Both values observed twice. This does not establish universal barrier or concurrency semantics. |

The record's `api_coverage` preserves these attempts and limitations. A missing
accessor or API exception fails the command; it cannot silently substitute
constructor inputs or predictions as extracted facts. Public-only enumeration
is a bounded unknown here, not proof that no other API could answer it.
The implementation inspects exactly two levels, not arbitrary recursive graphs.

## Results and evidence classes

| Evidence | Run 1 | Run 2 | Pair comparison |
| --- | --- | --- | --- |
| Static definition inspection | [static 1](nested-static-1.json) | [static 2](nested-static-2.json) | Byte-identical |
| Ephemeral framework execution, with separate static section | [execution 1](nested-1.json) | [execution 2](nested-2.json) | Byte-identical |

All predictions matched without changing expected facts. Static mode constructs
definitions but does not execute compute functions or create a job. There is no
direct callable-evaluation evidence. Execution uses `parent.to_job()` and
`execute_in_process()` with an explicit ephemeral instance and in-memory
outputs, in its own process and fresh temporary home. Cleanup is asserted.

The two graph aliases have retrievable mapped outputs but do not appear as
additional `STEP_SUCCESS` op steps. Framework step keys retain both
`left.seed`/`right.seed` and `left.finish`/`right.finish`; local-name keys alone
would lose identities and values. Exact list equality also detects duplicates,
missing edges, and crossed boundary mappings.

## Comparison and claim record

| Claim / decision relevance | Evidence-backed conclusion |
| --- | --- |
| Reusing one child definition requires only one set of local node IDs. | **Contradicted for this case.** Definition identity is shared, invocation identity is not. Any future extraction must retain scope. |
| Nested graph boundaries are completely opaque to inspection. | **Contradicted for these mappings.** Public input/output mapping APIs expose local endpoints. Complete documented-public enumeration is still unresolved; a prospective producer would need to resolve that API gap. |
| Both declared inputs reached the consumer in this local run. | **Supported twice.** It received `20` and `30` and produced `50`; both child paths completed. |
| Two dependency edges prove concurrent execution or a universal barrier policy. | **Unsupported.** This successful in-process case tests neither concurrency nor missing, failed, optional, or skipped inputs. P2's optional-output results do not settle this two-input case. |
| Dagster nested graphs and Airflow TaskGroups are equivalent. | **Not established.** P3 records task containment and task-level boundary edges; P4 records reuse of a graph definition, separate invocation scopes, explicit data-port mappings, and returned values. |

Both P3 and P4 preserve qualified internal identities and distinguish static
structure from run states. P3's group wiring expands task dependencies and
records `none_failed_min_one_success`; P4's consumer has two required integer
inputs. P4 does not translate that input requirement into an Airflow trigger
rule or claim that either container is an opaque executable node. P3 did not
test repeated aliased graph definitions, and P4 does not retest Airflow.
These results inform a future supported extraction subset; they establish no
wire contract, upstream publication, producer implementation, or release gate.

## Provenance, reproduction, and verification

Verified on macOS arm64 with CPython **3.11.16**, Dagster **1.13.22**, and
uv **0.12.10**, using a fresh `.venvs/dagster` and the unchanged 48-distribution
[hashed lock](../../probes/dagster/requirements.lock). Direct pins and all
resolved package pins were inspected before setup. `uv pip sync --require-hashes`
installed all 48 packages; `uv pip check` reported all compatible.
Each JSON stores probe-source and dependency-lock SHA-256 hashes and versions.

Follow the [exact setup and P4 commands](../../probes/README.md#dagster-nested-boundariesconvergence-run-p4).
Both static commands and both execution commands exited 0; both `cmp` commands
exited 0. [test_nested.py](../../probes/dagster/test_nested.py) additionally
runs isolated subprocesses with Python `-O`: dropping an invocation, dropping
an internal edge, crossing an input mapping, changing the right-hand execution
input, and reporting an unsupported version each raise an observation mismatch
and exit nonzero without producing a record. A static-only check makes both
graph execution entry points fail if called and succeeds without calling them.

API references:

- [Graph APIs](https://docs.dagster.io/api/dagster/graphs) document mapping
  properties, mapping fields, graph composition, aliasing, and `to_job`.
- [Execution APIs](https://docs.dagster.io/api/dagster/execution) document
  in-process results and retrieval by dotted nested path.
- [GraphDefinition, pinned source reference](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/graph_definition.py):
  installed 1.13.22 source has `nodes` at lines 342–344, `input_mappings` at
  413–420, `output_mappings` at 422–429, and `dependencies` at 526–528.
  These exact installed properties were inspected via `inspect.getsource` on
  the top-level exported `GraphDefinition` class. The live docs reported
  1.13.21 during this investigation; the pinned remote source fetch failed,
  so version-specific accessor claims rely on the installed locked package,
  not an assumption that live docs match 1.13.22.

To repeat the installed-source check without importing a private module:

```sh
.venvs/dagster/bin/python - <<'PY'
import inspect
from dagster import GraphDefinition
for name in ('nodes', 'dependencies', 'input_mappings', 'output_mappings'):
    getter = getattr(GraphDefinition, name).fget
    print(name, inspect.getsourcelines(getter)[1])
    print(inspect.getsource(getter))
PY
```

Normalization sorts invocation, membership, dependency, mapping, and step-state
lists without deduplicating. It retains scopes, definition names, ports, fan-in
indices, dynamic-mapping flags, all observed output values, and step/run states.
Generated run IDs, timestamps, durations, PIDs, temporary paths, and raw logs
are excluded. No timing or sibling-order claim is made. Other versions,
executors, dynamic mapping, optional/failing inputs, assets, and deeper nesting
remain untested.
