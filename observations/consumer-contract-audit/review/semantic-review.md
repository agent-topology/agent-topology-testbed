# Expectation-hidden document rereview

Date: 2026-09-12. Evidence class: document/contract inspection. No framework,
consumer or reference test executed. This is a same-session rereview by the
authoring assistant, not an independent reviewer, second model, or a claim of
memory-blind evaluation. Independence here is from implementation results.

The draft was frozen in [draft-sha256.json](draft-sha256.json). The rereview
used complete input-only cards for **all 31 documents**, the five question
definitions and cited rules, with expected fields and outcome labels omitted.
The final reusable [question packet](questions-without-expectations.jsonl)
contains all 310 group IDs, subquestion IDs, pointers and rules, without
judgments, expected values, unresolved scopes or draft derivations. The source
fixture names had been seen during discovery; names were not semantic evidence.

## Re-established structural results

All reviewed inputs contain one graph `main`, no materialized subgraph links,
and no producer limitations. F01's static before-interrupt does not affect these
five questions; preserve it in the input rather than converting it into a gap.

| Inputs | Input-and-rule derivation, independently of the draft table |
| --- | --- |
| F00 | START reaches router, each conditional destination and END. Each destination reaches END; router reaches both destinations and END. Only START lacks a target occurrence. No branch selection policy is supplied. |
| F01 | START → write → END. Transitive START → END exists; no self-path. Only START is a root. Interrupt metadata is neither a child assertion nor incompleteness. |
| F02 | START → first → second → END; all forward suffixes are reachable, none backward. Only START is a root. |
| F03 | START → retry, retry → retry/END. Retry reaches itself by a positive-length edge; START does not. Only START is a root. |
| F04 | START → left/right, both are sources of the same join to joined, joined → END. Each source reaches joined and END structurally; START reaches every other node. The original join remains AND with one joinId; it is not two independently executable edges. |
| F05 | START → nested → END. No node has subgraphId or an interpretation fact. The fixture recipe's child is unavailable to a JSON-only consumer and cannot populate its answer. |
| F06 | START → fork → left/right → END. Only START is a root. Direct drawable edges do not prove a complete all-declared assertion or concurrency. |
| F07 | Separate START → router and target → END components. START and target are observed roots. Router gap does not supply a connecting edge or identify the cause of target's candidacy. |
| X00–X03, X10–X11, X14–X17, X21 | One isolated node, listed as both entry and exit. It is a root and has no positive-length self-path. Extension changes leave those structural answers intact. |
| X04, X13 | split → a/b, with no further paths. split is the only root. Interpretation is reviewed separately below. |
| X05, X12, X18 | router → a/b via conditional edges, with no further paths. router is the only root; no selected route is established. |
| X06, X19–X20 | Separate start → router and target → end components. Roots start/target; only two reachable pairs. Existing router gap remains on router under both profiles, including invalid extensions. |
| X07 | No ordinary edges; one AND join a/b → joined. a/b are roots; joined is not. Both sources structurally reach joined. |
| X08 | a → start → a. No roots and no listed entries. Both nodes reach both nodes including themselves; these facts do not preclude a confirmed entry. |
| X09 | Isolated child is a root but has no self-path. Requested depth 2 does not supply contents, identity or successful expansion. |
| X22 | Two isolated nodes, start and target. Both are roots, neither reaches anything. No gaps exist; execution-entry certainty is a separate question. |

The grouped review covers every topology instance. Shared core shapes were not
counted as independent consumer executions. Endpoint reachability is the local
L-PATH calculation; it has no scheduler semantics. The literal core table agreed
with this re-derivation; no graph traversal implementation supplied expectations.

## Re-established interpretation results

For **every core-only row**, extension content supplies no trusted assertion.
For opt-in, check the whole recognized extension before accepting any family.
Missing facts remain missing; no record is synthesized for a name or role.

| Inputs | Document/ADR result |
| --- | --- |
| F00–F07, X00 | Absent; no entry, child or branch assertions can be recovered from names. |
| X01 | Valid. node is unknown entry, ordinary sentinel, known not-child. This resolves child classification within the assertion, not producer truth. |
| X02 | Valid. node is unknown entry, ordinary sentinel, known opaque-child. Ordinary sentinel role is compatible with child presence. Expansion success/content remains unavailable. |
| X03 | Valid. Preserve entry-not-established and child/sentinel identity-unavailable; no negative child assertion. |
| X04 | Valid. split has known all-declared with unconditional-edges evidence and two direct destinations; entry/child assertions are absent. No selection/execution conclusion follows. |
| X05 | Valid. router has unknown selection-not-observable; other fact families remain absent. |
| X06 | Valid. start is confirmed, end is not-entry, router/target are unknown entries; router has unknown branch selection. Only start/target have observedRoot true. No child facts occur. |
| X07 | Valid. joined is unknown entry with observedRoot false; a/b have no entry assertion. Missing records are allowed in authored documents; producer emission requirements are a separate layer. |
| X08 | Valid. start is confirmed despite observedRoot false and an empty entry array. a has no entry assertion. |
| X09 | Valid. child has unknown scope-not-inspected entry and subgraph facts; observedRoot true. Depth does not authorize inferred contents. |
| X10 | Unsupported revision 2; do not apply revision 1 as a fallback or trust its familiar-looking values. |
| X11 | Invalid: known subgraph lacks evidence. Discard trusted interpretation for all families, not only subgraph. |
| X12 | Invalid: unknown branch has forbidden value. |
| X13 | Invalid: exclusive is outside the known branch value set. |
| X14 | Invalid: opaque-child is paired with ordinary-node evidence. |
| X15 | Invalid: missing is not a visible node. |
| X16 | Invalid: duplicate node records. Do not deduplicate to pass. |
| X17 | Invalid: observedRoot false contradicts the absence of any target occurrence. |
| X18 | Invalid: all-declared does not meet ordinary direct-edge preconditions. |
| X19 | Invalid: known end sentinel cannot also be confirmed entry. Two facts in an input violating one explicit rule are not two contradictory contract obligations. |
| X20 | Invalid: record order is reversed. Do not canonicalize the extension array to conceal the violation. |
| X21 | Invalid placement at document root, even though root x-* is core-legal. Its standalone revision 1 object shape is a separate fact. |
| X22 | Valid. start is confirmed; target remains unknown even though the document is complete. |

All four gap-bearing inputs (F07, X06, X19, X20) retain an unresolved causal
mapping. The other 27 have no *recorded* gap whose causal mapping could be filled;
none thereby has an exhaustive runtime-blind-spot expectation. All five question
groups were reviewed for both profiles; no contract contradiction was established.

## Corrections before upstream comparison

1. X01 opt-in CQ4 originally treated expansion success/content as underdetermined
   for the whole document. The sole node is explicitly not-child; the local
   expansion question has **no applicable node**. The corrected expected value
   is an empty applicable-node set, not an invented unknown child. The
   [original row](corrected-draft-row.json) is retained. This is a local question
   scoping correction, not an upstream defect.
2. Root JSON Pointers written as `/` were corrected to the empty string. `/`
   denotes an empty property name, not the whole document. The final redacted
   packet uses the corrected pointers.
3. Exact family-field pointers were added alongside collection-level absence
   checks. These change traceability, not substantive judgments.

[pre-comparison-sha256.json](pre-comparison-sha256.json) freezes the resulting
semantic records before looking at the upstream `extensionStatus`/`shapeValid`
labels. Later comparison may expose a problem but is not allowed to overwrite
this table merely to match a reference implementation or example answer.
