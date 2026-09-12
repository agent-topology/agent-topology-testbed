# P0: reproducible linear baselines

Question: can another maintainer inspect the smallest dependency relationship
and successfully execute it using only the recorded environment and commands?

Historical baseline: [571e881e6d509b6e26ff8bf14b98e207d12e7ce9](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
These are new internal observations for [issue #2](https://github.com/agent-topology/agent-topology-testbed/issues/2),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1).
Historical findings, transcripts, and gallery artifacts remain unchanged.

## Cases and independent assertions

| Case ID | Minimal input | Static facts asserted | Execution facts asserted |
| --- | --- | --- | --- |
| P0-airflow-linear | DAG `p0_linear`: two EmptyOperators, `first >> second`; no external input; fixed logical date 2024-01-02 UTC | Exactly `first`, `second`; exactly one directed dependency `first → second` | DAG state `success`; exactly both task instances at map index -1, state `success` |
| P0-dagster-linear | Job `p0_linear`: `first()` returns 1; `second(value)` adds 1; no run config/external input | Exactly `first`, `second`; `first.result → second.value` | Run success true; exactly two STEP_SUCCESS identities `first`, `second`; second output 2 |

Expectations are literal constants placed before extraction in each smoke script.
The execution assertions use returned framework run objects/events, not operator
classes, fixture names, return annotations, or direct invocation of callables.
Both cases have **static** and **execution** evidence; no standalone **callable**
evidence is claimed. Execution records retain their static section separately.

## Provenance and reproduction

See [exact setup/run commands](../../probes/README.md). Verified with CPython
3.11.16, uv 0.12.10, macOS arm64; Airflow 2.10.5 (137 locked distributions) and
Dagster 1.13.22 (48 locked distributions) in clean, separate virtual environments.
Each JSON records framework/Python versions and SHA-256 hashes of its smoke source
and dependency lock. This identifies the uncommitted source used during execution
without a circular dependency on the evidence commit itself.

- Airflow sources: [DAG API](https://airflow.apache.org/docs/apache-airflow/2.10.5/_api/airflow/models/dag/index.html),
  [dag.test guide](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/debug.html),
  [2.10.5 DAG source](https://github.com/apache/airflow/blob/2.10.5/airflow/models/dag.py).
- Dagster sources: [execution API](https://docs.dagster.io/api/dagster/execution),
  [graph API](https://docs.dagster.io/api/dagster/graphs),
  [1.13.22 GraphDefinition source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/graph_definition.py),
  [1.13.22 JobDefinition source](https://github.com/dagster-io/dagster/blob/1.13.22/python_modules/dagster/dagster/_core/definitions/job_definition.py).
  Live docs may drift; the versioned source and locked installed distribution
  anchor these observations. No private-module imports are used by the probe.

## Observed results

Both cases passed static inspection and successful execution twice. The two
normalized static records match, and the two normalized execution records match.
The static sections also match across inspection-only and execution modes.
All successful commands confirmed temporary state was removed before writing JSON.

Verification on 2026-09-11 (America/New_York): `uv pip check` reported all 137
Airflow and 48 Dagster packages compatible. Negative checks replaced the literal
static expectation with an empty dictionary via `runpy`, then invoked `main()`
in separate `python -O` processes: both exited 1 with an observation mismatch and
no success record. Replacing the reported installed framework version with
`unsupported` also exited 1 for each framework before importing it. These are
failure-path checks, not additional framework evidence. Local Markdown targets
and external documentation links were checked; historical files were compared
against the baseline with `git diff --exit-code`.

| Framework | Static evidence | Execution evidence |
| --- | --- | --- |
| Airflow | [run 1](airflow-static-1.json), [run 2](airflow-static-2.json) | [run 1](airflow-1.json), [run 2](airflow-2.json) |
| Dagster | [run 1](dagster-static-1.json), [run 2](dagster-static-2.json) | [run 1](dagster-1.json), [run 2](dagster-2.json) |

## Normalization and limitations

JSON sorts object keys, node identities, directed dependency tuples, task instance
identities and step-success keys. It does not deduplicate. Airflow retains native
map index and task/DAG states. Dagster retains output/input port names, step keys,
run success, and the computed output. Generated run IDs, wall timestamps,
durations, PIDs, log text, and temporary paths stay outside the comparison.
Logical execution date is fixed input, not inferred from wall time. No event
ordering or concurrency conclusion follows from sorted final observations.

This verifies one simple local run shape per framework, not semantic equivalence
between frameworks. EmptyOperator success is a framework task-state observation,
not evidence that arbitrary user work ran. Dagster's in-process executor does not
prove concurrency. Branches, groups, nested graphs, dynamic expansion, production
schedulers, other platforms/versions, and historical F1/F3 corrections are out of
scope. No topology document is emitted and no upstream decision is made.

An initial Dagster development run failed because a dependency key was a
NodeInvocation rather than a string; it exited nonzero. The extractor now reads
its alias/name and the final runs above passed. That failed attempt is not counted
as successful evidence.

## Claim disposition

The [completed-cohort ledger](../../findings/completed-cohort-dispositions.md#p0)
classifies this observation’s material claims, their finding links or reasons for
non-promotion, and any specific minimal follow-up. Raw evidence remains unchanged.
