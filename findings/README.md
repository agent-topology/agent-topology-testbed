# Findings

A finding is a claim about the `agent-topology` format with a reproduction
attached. This file is the index.

The [completed-cohort disposition ledger](completed-cohort-dispositions.md) inventories
P0–P6, C1, S1 and T1 claim by claim, including explicit non-findings and minimal
follow-up candidates. It links the completed F1/#28 and F7/#27 dispositions.

## Index

**Observed version is not current disposition.** F1–F6 originated against npm
`@agent-topology/spec@0.1.0-beta.2` (Python baseline `0.1.0b2` is a separate
package identity). Historical claims and artifacts remain at
[testbed `571e881`](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9/findings).
The [upstream status review](upstream-status.md) records the 2026-09-12 check,
exact commits, dedicated issues, merged PRs, release boundary and remaining gaps.
All current-source dispositions below refer to upstream `eb0e2d8`, not a newly
published package or a fresh local consumer run.

| ID | Bounded claim and evidence | Observed against | Local disposition / current upstream disposition | Dedicated upstream relationship |
| --- | --- | --- | --- | --- |
| [F1](F1-fan-out-semantics/README.md) | Declaration does not establish selection, listener count or execution; [P1/P2/C1 evidence](F1-fan-out-semantics/README.md#measured-distinctions) | beta.2 trial; Airflow 2.10.5, Dagster 1.13.22, CrewAI 1.15.21 | Supported with corrections / improved declaration interpretation; selection remains unknown | [#97](https://github.com/agent-topology/agent-topology/issues/97) closed, [PR #110](https://github.com/agent-topology/agent-topology/pull/110) merged; [unposted draft](F1-fan-out-semantics/ISSUE.md) updates existing work |
| [F2](#f2--entrynodeids-conflates-a-graph-entry-with-a-node-that-lost-its-predecessor) | Observed roots do not establish entry or gap causality; [historical drawing](../gallery/unknown-routing-targets.svg) | beta.2 | Reproduced historically / improved entry facts; orphan cause remains unknown | [#100](https://github.com/agent-topology/agent-topology/issues/100) closed, [PR #113](https://github.com/agent-topology/agent-topology/pull/113) merged |
| [F3](F3-opaque-subgraph/README.md) | Core depth-0 nodes lack a child-presence contract; [historical evidence](F3-opaque-subgraph/README.md#reproduction) | beta.2 | Reproduced with narrowed grouping analogy / improved opaque-child facts; ordinary callable remains unknown | [#98](https://github.com/agent-topology/agent-topology/issues/98) closed, [PR #111](https://github.com/agent-topology/agent-topology/pull/111) merged |
| [F4](#f4--join-connections-exist-only-in-joins-never-in-edges) | Edges-only readers omit join connections; [historical drawing](../gallery/multi-source-join.svg) | beta.2 | Reproduced consumer trap / helper affordance fixed in source; joins remain distinct AND relationships | [#101](https://github.com/agent-topology/agent-topology/issues/101) closed, [PR #114](https://github.com/agent-topology/agent-topology/pull/114) merged |
| [F5](#f5--hiding-framework-sentinels-requires-vendor-coupling) | Core-only sentinel hiding requires framework knowledge; [historical gallery](../gallery/) | beta.2 | Reproduced / improved experimental roles; vendor neutrality remains unproven | [#99](https://github.com/agent-topology/agent-topology/issues/99) closed, [PR #112](https://github.com/agent-topology/agent-topology/pull/112) merged |
| [F6](#f6--agent-topologyspec-is-esm-only-and-the-failure-is-not-actionable) | CommonJS require failure lacks an ESM recovery hint; [package reproduction](upstream-status.md#f6) | beta.2; upstream recheck Node 22.16.0 | Failure reproduced; absent-docs/zero-dependencies claims withdrawn / guidance fixed, synchronous require unsupported | [#102](https://github.com/agent-topology/agent-topology/issues/102) closed, [PR #115](https://github.com/agent-topology/agent-topology/pull/115) merged |
| [F7](F7-or-firing-policy/README.md) | Ordinary edges do not specify C1's first-trigger/once-only OR policy; [counterexample](F7-or-firing-policy/README.md#smallest-mapping-and-counterexample) | CrewAI 1.15.21; beta.2, `3715dd3`, `eb0e2d8` contracts | Supported, bounded / stronger lossless OR mapping remains unresolved; no-semantics hypothesis withdrawn | [Unposted draft](F7-or-firing-policy/ISSUE.md); no dedicated upstream issue identified in this review |
| [F8](F8-extension-number-canonicalization/README.md) | Numeric extensions produce different full canonical bytes; [E1](../observations/E1/README.md) retains generated inputs and minimized replays | Published Python 0.1.0b2 / npm 0.1.0-beta.2 | Supported, bounded serialization gap; equal structure hashes / numeric policy remains upstream-owned | Local handoff candidate; not posted or graduated |

[#94](https://github.com/agent-topology/agent-topology/issues/94) is the open
interpretation **epic**, not a dedicated filing for each finding.
[#95](https://github.com/agent-topology/agent-topology/issues/95) preserves F1–F6
reproduction, [#96](https://github.com/agent-topology/agent-topology/issues/96)
owns the experimental contract, and
[#103](https://github.com/agent-topology/agent-topology/issues/103) supplies the
integrated consumer evidence. These cross-cutting relationships do not settle F7.

## Dispositions and unresolved evidence

The [47-claim ledger](completed-cohort-dispositions.md) routes all ten completed
P0–P6/C1/S1/T1 groups to findings, corrections, rejected hypotheses, bounded
limitations or precise follow-up candidates. F7 is the only distinct new finding
from that cohort; its withdrawn original hypothesis retains the ID. That cohort
allocated no F8; the separate published-contract investigation now records
[F8](F8-extension-number-canonicalization/README.md) from E1.
The [seven-question matrix](../probes/README.md#common-question-matrix-m1)
records source capability, not automatic target-format representability.

[Remaining gaps](upstream-status.md#remaining-evidence-and-follow-ups) include
F1 selection, F2 causality, F3 public extraction/child scope, F7 OR reset policy,
P3/P6 source-hash mismatches, and untested questions.
The [final P7 reconciliation](cross-framework-reconciliation.md) now integrates
15 P8/A1 claims, all 56 matrix cells and an explicit epic outcome review. Its
[P8](cross-framework-reconciliation.md#p8-disposition) and
[A1](cross-framework-reconciliation.md#a1-disposition) sections retain unresolved
joins, nesting and HITL alongside the supported model-specific boundaries.
No new finding ID or upstream publication follows; epic closure remains separate
from this local, reviewable synthesis.

## Status conventions

Local evidence uses **observed**, **reproduced**, **trialled**, **supported**
(bounded contract/observation support), **withdrawn** (reason retained), or
**unresolved** (missing decisive evidence stated). A withdrawn premise can coexist
with a narrower supported finding, as in F1/F7.

Upstream relationship is separate: an existing dedicated issue may address a
reproduced finding even though this repository's draft was never posted.
New upstream filings still require reproduced evidence.
An epic reference alone is not a filing. **Closed issue**, **merged source**,
**recorded consumer verification**, **qualified artifact**, and **published and
registry-verified release** are distinct claims requiring distinct evidence.
Do not mark an entire finding resolved merely because its issue closed. When a
specific affordance is fixed, state its source/version, verification and limits.
Withdrawn findings remain discoverable rather than being deleted.

## What a finding directory contains

A finding earns a directory when it has evidence to hold. Otherwise it stays
inline here.

```
F1-fan-out-semantics/
  README.md     the claim, the reproduction, what is and is not proven
  ISSUE.md      the upstream issue body, ready to paste
  evidence/     rendered output, probe transcripts
```

`ISSUE.md` is kept separate from `README.md` on purpose. The finding is written for
whoever maintains this repository and may say "not yet proven"; the issue is
written for whoever maintains the format and should not carry this repository's
internal bookkeeping.

---

## F2 — `entryNodeIds` conflates a graph entry with a node that lost its predecessor

> **Current disposition (2026-09-12).** Current source distinguishes confirmed entries
> from observed candidates through experimental entry facts; it preserves core entry
> arrays and the gap on the router. The original omission/extra-gap suggestion below is
> historical, not the accepted remedy. See [F2 status](upstream-status.md#f2).
>
> The original beta.2 report follows unchanged; present-tense statements and
> suggestions in that report describe the historical investigation.

**Status: reproduced.** `gallery/unknown-routing-targets.svg`.

In the `unknown-routing-targets` fixture the router's destinations could not be
determined, so `target` has no incoming edge. It therefore appears in
`entryNodeIds` alongside `__start__`, and any renderer draws it as a second entry
point to the graph.

That picture is wrong, and a consumer that surfaces `completeness` correctly still
draws it. The gap is recorded against `router`; the visible damage lands on
`target`; nothing connects the two.

This also blocks a useful affordance. A consumer would like to say *"this is where
the graph starts"*, and cannot, because membership in `entryNodeIds` may instead
mean *"the producer could not see what points here"*.

**Suggestion.** Either omit nodes orphaned by a recorded gap from `entryNodeIds`,
or emit a second gap against the orphaned node so the consequence is discoverable
at the element that shows it.

---

## F4 — Join connections exist only in `joins[]`, never in `edges[]`

> **Current disposition (2026-09-12).** The missing-guide/helper claim below is
> historical: current source documents implicit AND joins and exports
> provenance-preserving helpers in both packages. Ordinary edges still exclude join
> connections by design. See [F4 status](upstream-status.md#f4).
>
> The original beta.2 report follows unchanged; present-tense statements and
> suggestions in that report describe the historical investigation.

**Status: reproduced.** `gallery/multi-source-join.svg`.

There is no `left → joined` or `right → joined` edge in that fixture. The
connection appears only as a `joins[]` entry, so a consumer that iterates `edges[]`
to draw the graph — the obvious first implementation — produces a disconnected
picture with two dead ends and an orphan.

This is a reasonable modelling decision, not necessarily a defect. But it is a
silent trap, and the derivation rule is not stated in
`docs/guides/consuming-documents.md`.

**Suggestion.** Document the rule, and consider exporting a helper from the spec
packages (`derivedJoinEdges(structure)` or similar) so every consumer derives the
same connections the same way. Leaving each consumer to reimplement it is how
consumer dialects start — the thing `conformance/fixtures/` prevents among
producers, with no equivalent on the consuming side.

---

## F5 — Hiding framework sentinels requires vendor coupling

> **Current disposition (2026-09-12).** Current source provides experimental sentinel
> roles for the inspected LangGraph producers. The core-only and legacy boundary
> remains; two language implementations do not establish vendor neutrality. See [F5
> status](upstream-status.md#f5).
>
> The original beta.2 report follows unchanged; present-tense statements and
> suggestions in that report describe the historical investigation.

**Status: reproduced.** Visible in all eight drawings in `gallery/`.

`__start__` and `__end__` are ordinary entries in `nodes[]`. In every fixture, two
of the nodes are framework artifacts rather than author intent.

A framework-neutral consumer has no good option. Drawing them exposes LangGraph
internals in a picture meant to be neutral. Hiding them requires reading
`x-langgraph`, which couples the consumer to one producer. Matching the literal
strings is the same coupling with worse hygiene. `entryNodeIds` / `exitNodeIds` do
not help, both because of F2 and because membership does not imply the node is a
sentinel rather than a real first step.

The main README already lists this as a known limit. This is a note on its cost: it
is paid by every consumer, in every document, and there is currently no neutral way
to pay it.

---

## F6 — `@agent-topology/spec` is ESM-only, and the failure is not actionable

> **Current disposition (2026-09-12).** The error remains a supported-module-boundary
> issue, with current recovery guidance. The historical claims of absent ESM
> documentation and zero runtime dependencies below are explicitly withdrawn: beta.2
> already had an ESM notice and depends on Ajv and ajv-formats. Framework-free does not
> mean dependency-free. No require bundle was added. See [F6
> status](upstream-status.md#f6).
>
> The original beta.2 report follows unchanged; present-tense statements and
> suggestions in that report describe the historical investigation.

**Status: reproduced.** Hit while setting up `instrument/`.

A CommonJS consumer gets:

```
Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: No "exports" main defined in
.../node_modules/@agent-topology/spec/package.json
```

The `exports` map declares only `types` and `import` — no `require` condition and
no `default`. The error says nothing about ESM, so the reader's first guess is a
broken package rather than a module-format mismatch.

**Suggestion.** Ship a `require` condition, or state ESM-only prominently in
`docs/getting-started/typescript.md`. Given the pre-1.0 posture, documenting it is
probably enough.

**What worked.** Beyond this, the package holds up as a standalone dependency:
zero runtime dependencies, clean install, and `assertTopologyDocument` usable with
no framework runtime present. The claim that the spec package is independently
consumable checks out.
