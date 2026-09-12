# Evidence conventions

These are internal observation records, not a topology schema or producer API.
Preserve each framework's identities and native facts without forcing a common
classification. Historical beta.2 evidence is frozen at
`571e881e6d509b6e26ff8bf14b98e207d12e7ce9`: keep `findings/`, `gallery/`, and
the original Airflow files intact. Add new records under `observations/` and link
corrections explicitly when supported; P0 does not settle historical F1/F3 claims.

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
