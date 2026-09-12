# Contract-audit dispositions

This ledger is local document evidence at the pin in [manifest.json](manifest.json).
Rules below resolve through [sources.json](sources.json); exact affected
input/profile/question rows are in [matrix.jsonl](matrix.jsonl). A candidate is
not automatically a finding, and a question outside the contract is not
automatically a defect. No new F-number is assigned or upstream post made.

| Candidate | Evidence and disposition | What remains blank / smallest decision-changing evidence |
| --- | --- | --- |
| CA-ENTRY | CQ1 in all core-only rows; F07 in both profiles; X06/X08/X22 opt-in. R-MEANING describes entries recorded for the extracted structure, while R-ENTRY/R-ENTRY-GUIDE distinguish candidates from execution confirmation. No two incompatible obligations for the same concept were established. Reinforces the narrowed [F2](../../findings/README.md#f2--entrynodeids-conflates-a-graph-entry-with-a-node-that-lost-its-predecessor), not a new contradiction finding. | Execution-entry classification for the scoped nodes without trusted known entry facts. A document carrying a valid evidence-backed entry fact can resolve interpretation; source/framework evidence is separately necessary to establish its truth. |
| CA-CAUSE | CQ3 F07/X06/X19/X20, both profiles. R-COMPLETE locates the gap at router and R-ENTRY expressly excludes inferred cause/edge/target gaps. This is deliberately unasserted causality, not an implementation failure or a new gap merely because the consumer wants it. Related to F2. | Which missing relationship caused which observed candidate. More consumer agreement cannot establish it; independent source evidence and an upstream representation decision would be needed. |
| CA-CHILD | CQ4 F05 and X00–X03, with other missing/untrusted cases. R-NESTING does not turn absent subgraphId into no child; R-CHILD distinguishes admitted positive/negative/unknown assertions. Reinforces [F3](../../findings/F3-opaque-subgraph/README.md). The nested fixture recipe remains context, not hidden input to the consumer. | Child identity where no trusted known fact is present; expansion success/content even for opaque-child. Valid producer facts can settle assertion interpretation; expansion requires its own scoped evidence. |
| CA-BRANCH | CQ5 F00/F03/F04/F06/F07 and X04/X05/X06 plus invalid branch cases. R-BRANCH requires more than drawable direct edges and disclaims selection/scheduling. X04 opt-in adds all-declared but no execution meaning. Reinforces [F1](../../findings/F1-fan-out-semantics/README.md), not a fresh blanket no-semantics claim. | Unresolved declaration relationships are scoped per row; actual selection and execution have no expected value. A supported contract assertion may settle declaration meaning, but does not establish a run. |
| CA-JOIN | CQ2 F04 and X07, both profiles. R-JOIN explicitly defines provenance-preserving connections and AND convergence. The question's path closure is L-PATH, a local calculation. This is a bounded non-finding, consistent with the improved [F4 affordance](../../findings/README.md#f4--join-connections-exist-only-in-joins-never-in-edges). | Execution reachability remains blank. This audit does not test the separate [F7 OR firing-policy](../../findings/F7-or-firing-policy/README.md) counterexample or establish reset/once-only semantics. |
| CA-VALIDATION | X10–X21 opt-in. R-EXT-VALID/R-EXT-AUTH/R-EXT-SHAPE determine unsupported/invalid outcomes while preserving the valid core. X19 violates an explicit consistency rule; X17 violates the observed-root rule. Neither is a contradictory contract. Bounded non-finding from document review and post-freeze label agreement. | Producer truth and actual validator/consumer behavior remain unmeasured. Retained documents are suitable later inputs; no defect follows from authored invalid examples. |
| CA-COMPLETE | CQ3 throughout, especially X09/X22. R-LIMIT/R-PRESENT explicitly disclaim exhaustive blind-spot knowledge; R-SCOPE keeps unknown extension facts outside core gap cardinality. Bounded explicit contract limitation, not an automatically promoted ambiguity finding. | Exhaustive runtime blind spots. A trace/source inspection can add bounded facts, but cannot turn these static documents into universal guarantees. |
| CA-APPLICABILITY | X01 opt-in CQ4 rereview corrected an overbroad local expansion question. Known not-child leaves no applicable expansion subject. The [old row and correction](review/semantic-review.md#corrections-before-upstream-comparison) are retained. Local audit repair, not upstream evidence. | Nothing remains unresolved about the applicability correction. Producer truth is still outside the document audit. |

## Why zero contradictory judgments is bounded

We inspected core shape, core field meanings, completeness guidance, join guidance,
ADR 0008, its schema and its implementation criteria, for these five questions on
these 31 inputs. A vague word such as “entry” does not by itself establish a second
obligation that contradicts explicit candidate guidance. Similarly, producer
requirements to emit per-node entry facts do not make partial *authored validation
examples* contradictory: document validity and real producer conformance are
explicitly different layers (R-EXT-VALID).

This is not a proof that the entire specification is contradiction-free. It does
not audit packaging/version prose, hash serialization, all field combinations,
other releases or external source behavior. Every unresolved answer identifies
its reviewed rules and information limit; no blank cell is silently filled from
implementation behavior or from the agreement of two readers.

## Ownership boundary

Upstream owns whether a desired decision belongs in the contract and how it is
represented. The testbed records local calculations as local, missing information
as missing, and explicitly limited semantics as limited. Historical findings are
linked for reconciliation only; their prose and raw evidence were not rewritten.
Existing K1/E1 records informed the *evidence method*, not the semantic expected
values. This work does not repeat their callable comparisons or create a hash
consumer. Future implementation can reuse their measurement infrastructure only
after inspecting its fit to these structural questions.
