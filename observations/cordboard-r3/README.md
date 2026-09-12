# Cordboard R3 — conditional selection is not a document-policy fact

**Eight records; four repeated pairs agree.** The literal ADR-0007 Action-4
model rejects direct fan-out with static interrupts. It does not reject either
conditional recipe, although their directly evaluated routers return different
destination counts. Both conditional documents have identical graphs and
structure hashes. This supports [F1](../../findings/F1-fan-out-semantics/README.md),
with **no new finding ID** and no runtime safety conclusion.

## Question, inputs and authority

What can the proposed consumer rule distinguish from a topology document?
The rule is owned by Cordboard, not by the topology specification. At Cordboard
`67a46b43317ffc8474d46dc9b893d88d598f8d86`,
[ADR-0007 Action 4](sources/docs/decisions/0007-catalog-rejection.md#action-items)
counts at least two ordinary `direct` edges from a source and rejects if an
immediate target has `nodes[].interrupts`. Its separate override changes the
decision but retains the match and evidence. The
[architecture](sources/ARCHITECTURE.md#status-and-source-of-truth) says remaining
platform/lifecycle functionality is planned; this is an ADR model, not execution
of Cordboard's catalog. Dynamic author declarations and persistent UI disclosure
are outside this model.

The [recipes](../../probes/cordboard-r3/cases.json) contain literal expected
matches and callback results authored before extraction. All have the same three
user nodes (`router`, `a`, `b`), START/END, depth zero and compiled name. Only
routing form and static interrupt declarations vary. No fixture names are read
by the model. [Source hashes and commands](run/manifest.json) were saved before
measurement; input bytes are retained alongside each record. The verifier checks
node sets, edge endpoints/kinds, interrupt sites, boundaries and completeness
before checking rule outputs and evidence locators. Expected safety is deliberately
absent: neither the ADR nor these inputs establish it.

## Measured results

| Recipe | Static router edges | Static interrupt sites | Direct callback result | Default model | Explicit override |
| --- | --- | --- | --- | --- | --- |
| direct-interrupt | direct to a,b | a,b: before | Not evaluated | reject | not-rejected, match retained |
| conditional-single | conditional to a,b | a,b: before | `"a"` | not-rejected | not-rejected, no match |
| conditional-list | conditional to a,b | a,b: before | `["a","b"]` | not-rejected | not-rejected, no match |
| direct-no-interrupt | direct to a,b | None | Not evaluated | not-rejected | not-rejected, no match |

Every extraction passed the published core validator. Node bodies and callbacks
during extraction were guarded to raise; all recorded counts are zero. The two
conditional callbacks were evaluated once each **after** extraction, separately
from any framework invocation. The record distinguishes static extraction,
callable policy evaluation and direct router evaluation.

The [comparison](run/comparison.json) checks whole-record equality between
repeats after removing only `/document/provenance/generatedAt`. Both conditional
graphs and hash tuples match, with SHA-256 algorithm version 1 value
`8ff15427b74b9cd5eb75f58891ae72a1e5d085dad93a30f7151f9fadb51fe65b`.
The installed spec independently recomputed all eight hashes in
[verification](verification/receipt.json). Graph names retain `r3-minimal`, a
bounded counterexample to treating the AT-5 default name as unavoidable.

Raw stdout documents, stderr files and exit codes are in [run](run/manifest.json).
Empty stderr is retained. Nothing was regenerated through a renderer, and neither
consumer implementation nor callback output supplies the policy oracle.

## Environment and reproducibility

The [probe instructions](../../probes/cordboard-r3/README.md) provide commands.
This run uses Python **3.14.7**, published `agent-topology-langgraph==0.1.0b2`,
`agent-topology-spec==0.1.0b2`, and LangGraph **1.2.11**. The unchanged
[D1 Python lock](../../probes/published-producer/locks/requirements.txt) was installed
into a new venv using hash-checked PyPI wheels. [Setup receipt](setup/receipt.json)
and [pip report](setup/install.json) preserve dependency identities, artifact
URLs/digests and commands; each raw measurement retains installed versions and
module import paths. Eight subprocesses share that isolated installation.
Cordboard's AT log reports Python **3.12**: this is a new controlled experiment,
not an exact replay of its unarchived input/environment.

[Nine focused tests](verification/receipt.json) cover the four expected cases,
override, nonmutation, immediate-target scope, missing interrupts, invalid
validation results, corrupt evidence and strict repeat normalization. Additional
failure controls retain nonzero worker exits for an invalid recipe and a
schema-invalid producer document. Setup/API/validation failures do not become
policy nonmatches. Source snapshots have [SHA-256 receipts](sources/manifest.json).
Archived Cordboard documents retain original relative links; they are source
evidence, not a standalone documentation site.

## Disposition and limits

R3's stated rationale needs information its structural predicate does not
establish. The test measures that boundary, not a false negative against a
validated runtime-danger oracle. `not-rejected` does not mean safe; a direct
match does not prove concurrent scheduling or an unrecoverable run either.

The ADR cites [LangGraph #6626](https://github.com/langchain-ai/langgraph/issues/6626).
The issue was **closed** when checked on 2026-09-12; the
[status receipt](sources/langgraph-6626.json) records dates and source URL.
Its reproduction concerns dynamic interrupts in multiple tools within one
ToolNode/checkpoint namespace. This experiment uses compile-time interrupts in
distinct graph nodes. Applicability to these cases, the fixing version, scheduler
behavior, checkpoint collisions and resume failure were not tested. Permanent
data loss or universal protection cannot be inferred from either record.

Current upstream experimental interpretation remains a separate version boundary:
`all-declared` is a declaration assertion, and conditional selection remains
unknown. This evidence does not revive the superseded core `branches[]` proposal
or require an exclusive/concurrent field. Review Cordboard's policy and the
external failure's scope before prescribing either a consumer fix or a contract
change. See the [consumer reconciliation](../../findings/consumer-reconciliation.md)
for R1/R2, AT-1–AT-6, existing evidence and minimal follow-ups.
