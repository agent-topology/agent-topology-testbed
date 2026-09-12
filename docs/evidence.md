# Evidence conventions

These are internal observation records, not a topology schema or producer API.
Preserve each framework's identities and native facts without forcing a common
classification. Historical beta.2 evidence is frozen at
`571e881e6d509b6e26ff8bf14b98e207d12e7ce9`: keep `findings/`, `gallery/`, and
the original Airflow transcripts and trial outputs intact. Add new records under
`observations/` and link corrections explicitly when supported; P0 does not
settle historical F1/F3 claims. The one exception is a probe's own unsupported
classification code: P1 removed the operator-class `exclusive`/`concurrent`
conclusion from `probes/airflow/airflow_probe.py` and its example comments once
a counterexample invalidated it, per its explicit correction linked from
[F1](../findings/F1-fan-out-semantics/README.md). `OUTPUT.txt` still reflects the
pre-correction script and is kept as the frozen beta.2 transcript, not as current
script output.

Each record needs:

- Case ID and measured question, separate from minimal graph/execution inputs.
- Evidence class: **static** (inspect a constructed definition), **callable**
  (invoke user code directly), or **execution** (framework-managed run).
  Execution records may include a separately named static section. Callable
  results alone do not prove scheduling; operator names do not prove semantics.
- Observed facts and independent literal assertions written before extraction.
- Framework and Python patch versions, locked dependencies, exact setup/run
  commands, source hashes or commit, and version-appropriate API/source links.
- Two runs and a comparison of normalized semantic observations, with explicit
  normalization rules, limitations, and what remains unresolved.

Sort unordered identity/dependency collections but never deduplicate them to hide
unexpected instances. Retain task/step IDs, ports, mapping indices, cardinalities,
states, and measured values. Separate wall time, generated run IDs, durations,
process IDs, and temporary paths from comparisons. Keep meaningful event order
when the question depends on order. P0 measures final success, not event timing.

Inspect inputs and constraints before installation or expensive execution. Use
independent framework environments. Assert with explicit exceptions/nonzero exits
(including under Python `-O`). Missing packages, unsupported versions, API errors,
or setup failures are blocked evidence, never passes or silent substitutions.
Record what failed and what evidence is missing. Read command exit status before
using output files; an older successful file is not proof that a new run passed.

Airflow local execution uses temporary home/SQLite state and `dag.test()` with no
scheduler/webserver. Dagster uses `execute_in_process()` with an ephemeral instance.
Run each command in its own process; do not import CLI probes into a long-lived
application. Context-managed temporary directories clean up on normal exit and
exceptions. Forced process termination is outside this guarantee; leftover state
is never reused by a later case. Neither method demonstrates concurrency,
production scheduling, or a universal framework guarantee.

See [P0 records](../observations/P0/README.md) and
[reproduction commands](../probes/README.md).

## Cross-framework matrix conventions

[The common question matrix](../probes/README.md#common-question-matrix-m1)
(M1, issue [#12](https://github.com/agent-topology/agent-topology-testbed/issues/12))
indexes every probe's evidence by seven stable question IDs. These conventions
apply wherever a probe answers one of those questions:

- Separate **native capability** from **public static extractability**: a fact
  read through a non-underscore, source-visible accessor is evidence the
  framework exposes it, not evidence that a documented-public-only extractor
  can reach it. Record both, and the gap between them, rather than collapsing
  one into the other — see
  [P4's `api_coverage`](../observations/P4/README.md#api-coverage-and-bounded-unsupported-inspection).
- Separate **declared fan-out** (a static, symmetric shape true regardless of
  which branch a run takes) from **selection cardinality** (what a callback or
  op config actually chose) and from **scheduled/executed work** (what a
  scheduler or execution engine actually ran, skipped, or mapped). A declared
  shape is necessary but never sufficient evidence for the other two — see
  P1's and P2's evidence-class separation.
- Separate **structural identifiers** (definition-level IDs, invocation
  scopes, mapping keys) from **generated run UUIDs** and from
  **mapped-instance IDs** (`map_index`, dynamic mapping keys). Two runs
  comparing equal on a structural identifier show it did not change between
  those two runs; they do not establish that identifier is stable across
  arbitrary future runs, code changes, or framework versions. Never claim
  universal identity stability from a byte-identical `cmp` pair alone.
- Treat a hypothesis label (such as `F7`, reserved for CrewAI's AND/OR
  investigation) as exactly that — a name for an unresolved claim, not a
  finding or a confirmed gap. A missing join-mode property in one framework's
  API does not by itself prove an information gap; check the framework's own
  normative join semantics before recommending a change.
  F7's investigation now has a [published local disposition](../findings/F7-or-firing-policy/README.md):
  the original no-semantics hypothesis stays withdrawn, while the narrower OR
  firing-policy limitation is supported. The ID is retained and must not be reused.
