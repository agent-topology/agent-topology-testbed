# Findings upstream status review

For [testbed #30](https://github.com/agent-topology/agent-topology-testbed/issues/30).
[Findings index](README.md) · [Completed-cohort dispositions](completed-cohort-dispositions.md).

## Review boundary

Live GitHub issue, PR, HEAD and release metadata were checked on **2026-09-12,
12:20 UTC**, against upstream
[`eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`](https://github.com/agent-topology/agent-topology/tree/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe).
The compact [metadata snapshot](evidence/upstream-status-2026-09-12.json) records
the endpoints, states, merge commits and published release. Issue bodies were
read to establish finding relationships; status alone is not evidence of a fix.

Local input is testbed `dc6e9a39fd62f66c091d677e0a04ed629e3428bd`, containing
the completed [#27](https://github.com/agent-topology/agent-topology-testbed/issues/27),
[#28](https://github.com/agent-topology/agent-topology-testbed/issues/28) and
[#29](https://github.com/agent-topology/agent-topology-testbed/issues/29) dispositions.
Compare the six original entries at the issue's
[frozen source baseline `2dda397`](https://github.com/agent-topology/agent-topology-testbed/blob/2dda397a6f0675f4fdbf0a1cedb52257de1c52de/findings/README.md)
and the historical beta.2 artifacts at
[`571e881`](https://github.com/agent-topology/agent-topology-testbed/tree/571e881e6d509b6e26ff8bf14b98e207d12e7ce9).
The 47-row completed-cohort ledger supplies the finer claim inventory; no claim
row is removed or reclassified by this status refresh.

Two upstream evidence records serve different purposes:

- [Frozen F1–F6 reproduction](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/research/f1-f6-reproduction/README.md): npm beta.2 at `cbd2f404a36834fb9ba318500b7832f03ba610da` versus then-main `668bf46c88c37f3c14a4e143eb60c8695df74c6f`, Node 22.16.0 / LangGraph.js 1.4.14. It preserves corrections and saved producer documents; it does not reproduce Python beta.2 behavior.
- [Integrated consumer disposition](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/consumer/README.md#finding-disposition): producer-generated minimal cases and independent consumer expectations after the implementation changes, integrated by [PR #116](https://github.com/agent-topology/agent-topology/pull/116), closing [#103](https://github.com/agent-topology/agent-topology/issues/103). The recorded integration base is `23eea4276ba3d196b09cb7dd0878ad588073271c`; Python LangGraph 1.2.11 and LangGraph.js 1.4.14 are tested. This is upstream-recorded verification, not a new testbed execution.

## Upstream relationships

All issue numbers in this section refer to **agent-topology/agent-topology**.
The index links each dedicated issue and merged PR. The common
[#94 epic](https://github.com/agent-topology/agent-topology/issues/94) remains open;
it supplies context, not a substitute dedicated filing. Reproduction
[#95](https://github.com/agent-topology/agent-topology/issues/95) / [PR #108](https://github.com/agent-topology/agent-topology/pull/108),
contract [#96](https://github.com/agent-topology/agent-topology/issues/96) / [PR #109](https://github.com/agent-topology/agent-topology/pull/109),
and integration #103 / PR #116 are closed/merged cross-cutting work.

### F1

Dedicated #97 / PR #110 implements evidence-backed branch declarations. Current
revision 1 supports `all-declared` under bounded structural evidence and keeps
routers `unknown/selection-not-observable`. The integrated `direct`, `single`
and `list` cases support that improvement, not exclusive/concurrent execution.
[Active F1](F1-fan-out-semantics/README.md) and its unposted draft already make
this distinction; [history](F1-fan-out-semantics/HISTORY.md) retains the injected
trial and rejected operator-class inference. Existing work addresses F1; a
duplicate upstream filing is unnecessary. The unresolved selection distinction
is still indexed rather than hidden by issue closure.

### F2

Dedicated #100 / PR #113 adds entry interpretation. The integrated `orphan`
case leaves START and target as observed roots, confirms START only, and retains
the routing gap on the router. Actual target/causal attribution remains unknown.
The [historical F2 report](README.md#f2--entrynodeids-conflates-a-graph-entry-with-a-node-that-lost-its-predecessor)
is retained, but its suggested entry-array removal or inferred target gap is
not the accepted implementation. P3-b/S1-e in the ledger reinforce the
root/entry distinction without a new orphan-by-gap reproduction.

### F3

Dedicated #98 / PR #111 adds experimental `opaque-child` facts. Integrated
`child`/`ordinary` cases use equal IDs and core hashes but different
interpretation; ordinary callables remain unknown, not proven non-children.
This narrows [F3](F3-opaque-subgraph/README.md)'s original absolute language and
supersedes its core-marker proposal. The original gallery is qualitative (its
linear and nested fixtures have different ordinary-node counts). P3 grouping,
P4 nested ports and S1 declared scopes do not certify another producer or
complete expansion. The historical draft remains historical, not a new filing.

### F4

Dedicated #101 / PR #114 and the integrated `join`/`independent` cases establish
the fixed consumer affordance: Python `derived_join_edges` and TypeScript
`derivedJoinEdges` return drawing connections with `joinId` provenance. The
[consuming guide](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/guides/consuming-documents.md#join-connections)
now explains implicit AND. Joins remain authoritative and separate from ordinary
edges; an edges-only consumer can still omit them. This fixes the guide/helper
gap in source, not F7's separate first-trigger/once-only policy question.

### F5

Dedicated #99 / PR #112 and integrated sentinel-name controls provide
experimental framework-role facts without ID matching or reading `x-langgraph`.
Absent, invalid and unsupported extensions must not authorize hiding. The
core-only/legacy boundary remains. Two LangGraph implementations do not prove
framework neutrality; no cohort sentinel experiment supplies independent proof.

### F6

Dedicated #102 / PR #115 improves installation and recovery guidance. The
[frozen package reproduction](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/research/f1-f6-reproduction/README.md#f2-f4-f5-and-f6-retain-the-narrow-claims)
withdraws absent-ESM-docs and zero-runtime-dependency claims: a beta.2 notice
already existed; Ajv 8.20.0 and ajv-formats 3.0.1 were installed. Framework-free
consumption survives that correction. Current
[quickstart](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/getting-started/typescript.md#use-it-from-commonjs)
shows ESM and awaited CommonJS `import()`. Upstream integration records
clean-install/snippet checks and its `.mjs` consumer. Synchronous `require()`
remains unsupported; the error text/package export boundary was not replaced.
“Fixed guidance” is not a claim of a CommonJS bundle or newly published artifact.

### F7

[F7](F7-or-firing-policy/README.md) retains the supported OR-policy limitation
and both rejected blanket hypotheses. The reviewed upstream issue inventory
contains no dedicated F7/once-only OR issue; #94/#96 are context, not its filing
or resolution. The [draft](F7-or-firing-policy/ISSUE.md) is unposted. F7's
three-contract audit already includes this same `eb0e2d8` pin. C1's correction,
ledger C1-b/c and the corrected Q4 matrix agree: source capability is supported,
target AND meaning is established, and ordinary edges alone do not specify the
observed suppression/reset policy.

## Publication boundary

At the check time, the GitHub release list contains
[v0.1.0-beta.2](https://github.com/agent-topology/agent-topology/releases/tag/v0.1.0-beta.2),
published 2026-09-11 17:49:49 UTC; no beta.3 release is listed. Upstream
[#104 preparation](https://github.com/agent-topology/agent-topology/issues/104),
[#105 qualification](https://github.com/agent-topology/agent-topology/issues/105),
[#106 publication/registry verification](https://github.com/agent-topology/agent-topology/issues/106),
and [#107 release epic](https://github.com/agent-topology/agent-topology/issues/107)
are open. Source package metadata still saying beta.2 does not make those source
changes part of published beta.2. Registry installation was not repeated here;
this review establishes no new published fix or consumer-resolution receipt.
Neither upstream #94 nor testbed #1 is completed by this documentation refresh.

## Remaining evidence and follow-ups

| Gap | Precise reason and smallest decision-changing next evidence | Route |
| --- | --- | --- |
| F1 selection / F2 causality | Structural declarations do not establish callback selection or which missing relation caused an orphan. Require independently observable source evidence and a contract decision before a stronger fact. | [F1 remedy](F1-fan-out-semantics/README.md#current-upstream-decision-not-the-historical-proposed-shape), [F2](#f2); upstream #97/#100 remain implementation history, not open promises. |
| F3 producer applicability | TaskGroup membership is not compiled-child identity; P4 lacks fully documented enumeration; expanded/wrapped child support is bounded. Identify a supported API for the existing aliases before promising a public-only producer. | [P3/P4 ledger](completed-cohort-dispositions.md#p4), [F3](#f3). |
| F7 OR policy | Early firing plus suppression after `b` needs a normative mapping with reset scope. Reuse the four C1 records; a larger suite cannot supply a missing contract rule. | [F7 decision boundary](F7-or-firing-policy/README.md#decision-impact-and-remaining-boundary), [draft](F7-or-firing-policy/ISSUE.md). |
| P3/P6 source provenance | Saved source hashes differ from checked-in bytes despite matching assertions. Recover those source bytes first; rerun only a required case/control if a new claim needs reproduction. | [P3-e/P6-e hashes and reasons](completed-cohort-dispositions.md#provenance-limits). |
| Optional/mapped/nested convergence | P2 has no optional two-input consumer, P5 no mixed mapped state, P6 no nested dynamic chain. Preserve the ledger's minimal controls; none is a proven format defect. | [P2-d](completed-cohort-dispositions.md#p2), [P5-c](completed-cohort-dispositions.md#p5), [P6-d](completed-cohort-dispositions.md#p6). |
| Boundary/runtime/HITL | T1 inspected definitions, not history execution or anchored interrupt placement; Q6 is largely untested. C1 documentation mismatch is separate from F7. | [T1-c/e](completed-cohort-dispositions.md#t1), [shared exclusions](completed-cohort-dispositions.md#shared-exclusions-and-finding-coverage), [C1-d/e](completed-cohort-dispositions.md#c1). |
| Later cohort and final synthesis | P8/A1 exist but are outside D3's frozen ten-group inventory. Final integration must include their model-specific dispositions and remaining questions. | [P8](../observations/P8/README.md), [A1](../observations/A1/README.md), [P7/#9](https://github.com/agent-topology/agent-topology-testbed/issues/9), [incremental practice/#31](https://github.com/agent-topology/agent-topology-testbed/issues/31). |
| Published consumer resolution | Merged code and upstream local verification are not frozen-RC artifact receipts or clean public-registry verification. | Upstream [#105](https://github.com/agent-topology/agent-topology/issues/105) and [#106](https://github.com/agent-topology/agent-topology/issues/106). |

These are bounded follow-up candidates or existing issue links, not newly
scheduled work, release gates imposed by this testbed, or upstream posts.

## Verification

Review all relative targets/anchors across the findings, cohort observation
documents and matrix; verify GitHub issue/PR relationships and pinned evidence
links. Compare all six baseline finding IDs and all 47 ledger claim rows, retain
the original inline reports and raw evidence, and inspect F1/F7/C1/S1/Q4 for
agreement. Only documentation and saved-evidence integrity checks apply; no
framework installation, full probe run, renderer build or release test is needed.

D4 verification results (2026-09-12): **496 local targets/anchors** and **84
project GitHub references** passed (including pinned document anchors and live
issue/PR/release endpoints). All six frozen index IDs remain discoverable; all
**47 ledger claim rows** and all four original inline reports are unchanged.
All **163 tracked raw observation/finding/gallery artifacts** match the local
input commit, and all **57 cohort run pairs** remain byte-identical. Every
completed-cohort observation retains its ledger backlink. F3's README/draft
receive explicit historical qualifications; F7's draft now uses the merged
input commit instead of a temporary branch link. F1/F7, C1/S1 corrections and
Q1/Q3/Q4 were checked for consistent capability/contract/execution boundaries.
`git diff --check` passed. These are reference and saved-evidence checks, not
new framework executions or reruns of upstream's reported consumer tests.

## P7 integration addendum

The [final reconciliation](cross-framework-reconciliation.md) now supplies the
P8/A1 increment excluded from this review’s frozen cohort and reviews epic #1
against actual evidence. Its live HEAD recheck still matches `eb0e2d8`; the
source-versus-release dispositions above are unchanged. This addendum supersedes
the pending-integration wording above without rewriting the D4 review.
