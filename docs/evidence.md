# Evidence conventions

These are internal observation records, not a topology schema or producer API.
Preserve each framework's identities and native facts without forcing a common
classification.

## Historical preservation and corrections

Raw evidence is immutable: retain saved observation JSON, transcripts, gallery
artifacts and trial outputs. Historical beta.2 claims and artifacts remain
available at `571e881e6d509b6e26ff8bf14b98e207d12e7ce9`; do not silently
rewrite them as current evidence. Add new records under `observations/`.
Active finding prose, observation interpretations and unposted `ISSUE.md` drafts
may be corrected with provenance: state the old claim, correction and reason,
link the supporting records and exact baseline/version, and date the disposition.
Preserve rejected hypotheses visibly in the findings index or a linked ledger;
do not delete them or recycle their IDs as unrelated confirmed findings.

Corrections do not regenerate historical outputs. For example, P1 removed the
unsupported operator-class `exclusive`/`concurrent` inference from the original
Airflow probe, with a correction linked from
[F1](../findings/F1-fan-out-semantics/README.md#correction-p1).
`OUTPUT.txt` remains the frozen pre-correction beta.2 transcript, not current
script output. P0 alone does not settle historical F1/F3 claims.

## Record requirements

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
- A hypothesis is not a confirmed gap. F7 was the convergence investigation's
  hypothesis label; [#27](https://github.com/agent-topology/agent-topology-testbed/issues/27)
  has now published [F7's local disposition](../findings/F7-or-firing-policy/README.md).
  The no-semantics hypothesis is withdrawn and the narrower OR firing-policy
  limitation is supported within its recorded bounds. F7 is neither reserved
  pending investigation nor available for reuse. C1's older “available” wording
  remains explicitly superseded historical prose. Future hypotheses require
  evidence-based disposition, regardless of their working label.

## Promotion from observation to finding

A completed probe needs the [closure disposition](issue-planning.md#probe-closure-disposition)
before it is considered reconciled. Matrix support alone is not finding support.
For each proposed format claim, distinguish these five questions:

| Layer | Required distinction |
| --- | --- |
| Schema shape | What fields and relationships are allowed at the exact target version? Absence of a property alone does not prove a semantic gap. |
| Normative semantics | What meaning do the contract, normative guidance and conformance evidence assign at that commit? Separate historical releases from later source guidance; joins can mean AND without a mode field. |
| Framework capability | What does the pinned framework/programming model declare or actually do? Keep static, callable and execution evidence separate and bounded. |
| Static API accessibility | Can that fact be read without execution through documented public APIs, merely exported/source-visible accessors, or unsupported inspection? Native capability does not establish a supported static producer. |
| Consumer information loss | Under an explicit target mapping, what decision-relevant distinction can the consumer no longer recover from the contract? Supply a minimal mapping/counterexample, label authored trials, and state scope and uncertainty. |

Promote a reproduced, contract-grounded gap to a new finding only when it is
independent of existing findings; otherwise reinforce or correct the existing
record. Supported framework behavior, rejected hypotheses and API limitations may
be explicit non-findings. Missing decisive evidence gets a bounded unresolved
disposition and the smallest follow-up that could change the decision, not an
assumed defect or a forced new ID. Local publication does not authorize upstream
filing, alter a contract, or qualify a release.

## Three closure examples

These apply the checklist to saved evidence; they require no new framework run.

| Example / measured claims | Finding or explicit non-finding and evidence/index link | Decision impact | Unresolved evidence / minimal follow-up |
| --- | --- | --- | --- |
| New reproduced gap: C1 on CrewAI 1.15.21 fires OR before b and only once, unlike AND's all-required behavior. Static exposure and runtime counts are separate facts. | Supported, bounded [F7](../findings/F7-or-firing-policy/README.md#smallest-mapping-and-counterexample); [indexed C1-c](../findings/completed-cohort-dispositions.md#c1) links the saved pairs and the target-contract comparison. Ordinary edges preserve connectivity but supply no latch/reset rule. | A consumer must not infer once-only OR firing from ordinary edges; a schema change is not predetermined. #27 delivered this disposition locally. | For a stronger lossless claim, obtain a normative early-fire/suppress-later mapping with reset scope and check the same four records. Cycles/races stay untested; no broad rerun is required to reconcile this bounded finding. |
| Rejected hypothesis: absence of a join mode means absence of AND semantics. | Withdrawn premise retained in [F7](../findings/F7-or-firing-policy/README.md#contract-versions-and-authority) and [C1-b](../findings/completed-cohort-dispositions.md#c1). Normative AND meaning defeats the schema-only inference; the narrower OR finding is separate. | Withdraw the no-semantics argument and retain the ID/provenance. This records #27's outcome, not a policy that assumed its verdict. | None for rejecting that premise at the audited commits. A changed contract would require a new pinned comparison, not reopening the old probe. |
| Supported behavior, no new finding: P0's two-node Airflow 2.10.5 and Dagster 1.13.22 definitions expose a dependency and both steps succeed locally. | Explicit baseline-only non-finding [P0-a/b](../findings/completed-cohort-dispositions.md#p0), with [static/execution pairs](../observations/P0/README.md#observed-results). | Establishes viable minimal probe inputs; neither a format defect nor revalidation of F1/F3. #29 delivered the indexed disposition. | None for the baseline question. Production concurrency and universal identity stability remain outside scope; do not schedule speculative tasks to force a finding. |
