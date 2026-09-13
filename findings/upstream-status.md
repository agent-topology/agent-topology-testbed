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

## Beta.3 review boundary (2026-09-12)

This is a new, dated review; the `eb0e2d8` review above remains the prior review
boundary and its claims are not rewritten. At 20:09 UTC, tag
[`v0.1.0-beta.3`](https://github.com/agent-topology/agent-topology/tree/v0.1.0-beta.3)
resolved to `848b179aee32789a6f8b0ad4552a3a1262a05d55`. The dated
[live-metadata snapshot](evidence/upstream-status-2026-09-12-beta.3.json) retains
the tag response, npm SLSA source ref/commit, PyPI GitHub publisher, dist-tags,
artifact digests/integrities, release-list result, and #106 checklist state.

The source range contains 19 commits and 46 files. It adds numeric canonical
form/domain decisions, document-local graph IDs, beta.3 candidate notes and
package changes. `docs/0.1-contract.md`, `docs/guides/consuming-documents.md`,
and `spec/README.md` changed; the schema, experimental interpretation schema,
ADR 0002, ADR 0008, ADR 0008 criteria, and concepts guide did not. The release
notes and CHANGELOG still call beta.3 a candidate/unpublished even though the
four registry versions are available. There is no beta.3 GitHub Release.

Thus **closed issue**, **merged source**, **registry-published**, and
**registry-verified release** remain separate: #106 is closed, the tag names
the source commit, and registries expose the versions, but #106 still has no
checked receipt/digest-review, clean-install, final-release-record, or published
documentation checkbox. This review makes no verification claim.

### Finding relationships and pending re-observation

F7 now relates to [#119](https://github.com/agent-topology/agent-topology/issues/119),
closed source documentation of the first-trigger/once-only boundary. F8 relates
to [#117](https://github.com/agent-topology/agent-topology/issues/117),
[#118](https://github.com/agent-topology/agent-topology/issues/118),
[#124](https://github.com/agent-topology/agent-topology/issues/124), and
[#125](https://github.com/agent-topology/agent-topology/issues/125), all closed
source work. None is a registry-artifact result: V2 (#53), E2 (#54), and X1
(#55) are pending re-observation, not resolved dispositions.

### Impact trace

Every `eb0e2d8` reference found after this review is classified below. A saved
observation/source ledger is a historical record even where its cited upstream
file later changed; it is not silently repinned.

| Testbed references | Classification | Disposition |
| --- | --- | --- |
| `findings/upstream-status.md`, `findings/evidence/upstream-status-2026-09-12.json` | historical record | keep as the prior boundary |
| `observations/V1/{README.md,source-references.json}`, `observations/D1/{README.md,source-references.json}`, `observations/Q1/{README.md,source-references.json,inputs.json,run-1/inputs-before-install.json,run-1/provenance.json,run-2/inputs-before-install.json,harness-failure/inputs-before-install.json}`, `observations/E1/{README.md,source-references.json}`, `observations/K1/README.md` | historical record | keep beta.1/beta.2 inputs and receipts |
| `observations/consumer-contract-audit/{README.md,manifest.json,sources.json,review/citation-correction.json,review/upstream-labels.json}` | historical record; cited source changed | keep frozen audit; defer **Audit/R3 re-judgment** candidate because contract/consumer-guide citations changed |
| `observations/P7/{README.md,review-inputs.json}` | historical review input | keep; P7 does not become a beta.3 artifact observation |
| `findings/F7-or-firing-policy/{verify.py,evidence/audit.json}` | historical audit record | keep reproducible 2026-09-12 audit; do not overwrite its source hashes |
| `findings/F1-fan-out-semantics/{README.md,ISSUE.md}`, `findings/F3-opaque-subgraph/README.md`, `findings/F7-or-firing-policy/{README.md,ISSUE.md}`, `findings/F8-extension-number-canonicalization/README.md`, `findings/completed-cohort-dispositions.md`, `findings/consumer-reconciliation.md`, `findings/cross-framework-reconciliation.md`, `findings/README.md` | current pointer or mixed current/historical prose | current beta.3 disposition is this review; V2/E2/X1 or the deferred Audit/R3 re-judgment supply the needed re-observation, while historical citations remain pinned |

The consumer-contract audit cites these upstream paths: `docs/0.1-contract.md`,
`docs/decisions/0002-record-what-could-not-be-observed.md`,
`docs/decisions/0008-experimental-consumer-interpretation.md`,
`docs/decisions/0008-implementation-criteria.md`, `docs/guides/concepts.md`,
`docs/guides/consuming-documents.md`, `spec/README.md`,
`spec/agent-topology.schema.json`, and
`spec/experimental/interpretation-v1.schema.json`. Only the contract, consumer
guide and spec README changed in the range, so the audit's frozen citations stay
valid history but need the named deferred re-judgment for a current verdict.
Cordboard R3 cites no `eb0e2d8` source path; its captured beta.2 package metadata
contains moving `main` documentation URLs. Those raw installation records remain
historical and are not source evidence for beta.3.

### X1 registry-observation addendum

The pending language above records the beta.3 review boundary before testbed #55
ran; it is preserved as dated history. [X1](../observations/X1/README.md) now adds
the separate registry-artifact result for F1–F6: 32 successful producer captures
across two fresh processes per language, two matching Python API/CLI custom graph-ID
captures, two expected synchronous CommonJS failures, verified registry artifact
digests and a deliberately wrong expectation that fails nonzero.

Per affordance, registry beta.3 exposes direct `all-declared` and conditional
unknown branch facts (F1), confirmed START plus an unconfirmed orphan and unchanged
router gap (F2), an opaque-child fact while the ordinary callable stays unknown
(F3), provenance-preserving join helpers (F4), experimental sentinel roles (F5),
and async ESM guidance alongside the unchanged synchronous `require` boundary
(F6). F1 selection, F2 causality, F3 ordinary-callable scope and F5 vendor
neutrality remain unresolved. X1 does not re-judge F7, qualify beta.3, replace the
historical beta.2 artifacts, or turn source/registry publication into upstream
release verification.

## Epic #51 outcome review

This review closes the local evidence loop requested by
[#51](https://github.com/agent-topology/agent-topology-testbed/issues/51). It
assesses the delivered records rather than treating closed child issues as
proof. The review boundary remains upstream `848b179aee32789a6f8b0ad4552a3a1262a05d55`
and the registry artifacts identified in the dated snapshot; no live source,
registry or release claim is advanced beyond that boundary.

| Epic success evidence | Reviewed disposition |
| --- | --- |
| S2 dated status snapshot and complete `eb0e2d8` impact trace | **Satisfied with a corrected planning count.** #52 expected eight artifact filenames, but the two npm tarballs plus four PyPI distributions make six; the snapshot records that contradiction and all six digests/integrities. It also retains the tag, provenance, publisher, dist-tags, absent GitHub Release, #106 state and candidate wording. The impact trace above classifies every retained `eb0e2d8` reference and every consumer-audit/R3 source dependency without rewriting historical records. |
| V2 same-input beta.2/beta.3 comparison | **Satisfied with corpus bounds.** [V2](../observations/V2/README.md) records 72/72 zero-exit fresh-process calls in each of two captures over V1's nine unchanged documents. All 27 transition/cross-language comparisons retain acceptance, canonical bytes and complete hash tuples; the corpus contains no numeric extension. |
| E2 replay of F8 | **Satisfied with population bounds.** [E2](../observations/E2/README.md) reuses, rather than regenerates, E1's 600 saved inputs and 16 minima in two lock-only captures. Beta.3 has full byte parity and unchanged hash tuples throughout; the two unsafe-integer cases remain a separately classified narrowing compatibility transition. The beta.2 F8 evidence is preserved. |
| X1 registry observation of F1–F6 | **Satisfied per affordance.** [X1](../observations/X1/README.md) records 32/32 producer captures, matching fresh-process/language comparisons, graph-ID API/CLI agreement, two expected CommonJS failures, artifact identities and a failing wrong-expectation control. F1 selection, F2 causality, F3 ordinary-callable scope and F5 vendor neutrality remain unresolved; no whole finding is marked resolved. |
| Child closure dispositions | **Satisfied.** S2 records a bounded static/source and registry-metadata review; V2 and E2 record callable non-finding/finding dispositions; X1 records static producer-extraction and callable helper/module-boundary dispositions. Each links evidence/index, decision impact, limits and the smallest remaining evidence. |
| Review actual outcomes and deferred candidates | **Satisfied here.** The disposition inventory and candidate decisions below are based on those records, not on child count or expected passing outcomes. |

The resulting current-versus-historical inventory is:

| Prior dependency | Beta.3 disposition |
| --- | --- |
| F1–F6 affordances previously attributed only to source `eb0e2d8` | Re-observed per affordance in registry beta.3 by X1, with the named residual unknowns unchanged. Historical beta.2 findings, reproduction and gallery artifacts remain historical. |
| V1's nine beta.1/beta.2 spec documents | Re-observed for the beta.2→beta.3 transition by V2. V1 remains the immutable earlier comparison. |
| F8/E1 numeric-extension population and minima | Re-observed by E2 and resolved only within that saved population on beta.3. F8 remains a supported beta.2 finding. |
| F7/C1 OR-policy evidence and the current-source contract audit | Retained with their original evidence classes and pins. S2 relates the current-source boundary to upstream #119; neither X1 nor registry publication re-executes C1 or resolves reset policy. |
| Q1 quickstarts, D1 producer determinism and K1 compatibility boundaries | Explicitly retained as bounded published beta.2 observations. Q1 remains the documented beta.2 path at the reviewed tag; D1's determinism question and K1's mutation matrix were not silently promoted to beta.3. |
| Consumer-contract audit, Cordboard R3, P7 inputs and the committed gallery | Explicitly retained as frozen source/package or beta.2 history. Changed audit citations require a new judgment; R3 cites no pinned `eb0e2d8` source path, and the gallery is not regenerated in place. |

Deferred candidates are refined as follows; none is scheduled by this review:

| Candidate | Decision and reason |
| --- | --- |
| D2 | **Retain and refine.** X1 satisfies the prerequisite by observing interpretation facts and caller-supplied graph IDs in beta.3 artifacts. A beta.3 producer-determinism study is now independently scopeable, but X1's static extraction does not answer it and #51 does not require it. |
| Q2 | **Retain.** At the reviewed tag the getting-started commands still select beta.2, so Q1 remains the documented path. Reconsider only after the documentation selects beta.3. |
| K2 | **Drop from this re-baseline.** S2 found no changed compatibility obligation requiring K1's full mutation matrix beyond the numeric-domain transition directly exercised by E2. A future contract change may justify a newly scoped check; K1 remains historical. |
| Audit/R3 re-judgment | **Refine to the consumer-contract audit only.** Its contract, consumer-guide and spec-README citations changed and need a new pinned judgment for a current verdict. R3 cites no pinned `eb0e2d8` source and remains a beta.2 package trial; no R3 rerun follows from S2. |
| G1 | **Retain behind a location decision.** The committed gallery is historical beta.2 evidence and must not be overwritten. A beta.3 rendering belongs in a separate location if later approved. |

**Outcome disposition:** the registry beta.3 re-baseline is satisfied locally at
the recorded boundary. It yields a bounded V2 non-finding, a bounded beta.3 F8
resolution, registry observations for F1–F6 with unchanged residual unknowns,
and explicit historical retention for evidence not rerun. It does not qualify a
release, verify upstream publication, alter a topology contract, regenerate the
historical gallery, file upstream work or gate a release.
