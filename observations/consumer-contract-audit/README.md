# Consumer contract audit — stages 0 and 1

**31 documents × two profiles × five question groups reviewed.** The 310 groups
contain 1,302 separately judged answers: **900 determined, 402 underdetermined,
zero contradictory, zero unreviewed**. Every underdetermined answer omits its
expected value. A determined unknown assertion is not knowledge of its underlying
fact. These counts describe this question decomposition, not format quality or
consumer pass rates.

This is a **document/contract inspection**, dated 2026-09-12, against upstream
`eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`. It is neither callable consumer evidence
nor framework execution. The source pin includes an experimental interpretation
contract; it is not a claim that published beta.2 contains those changes.

## Read the record

1. [Question definitions](questions.md): CQ1 entries, CQ2 connections/reachability,
   CQ3 recorded uncertainty, CQ4 nesting, CQ5 outgoing relationships. Local graph
   calculations are explicitly distinguished from contract obligations.
2. [Readable matrix](matrix.md): all 62 input/profile combinations, their partial
   judgments and the concrete observations that distinguish the inputs.
3. [Complete judgments](matrix.jsonl): one JSON line per question group, with
   per-answer scope, input pointers, citations, derivation and expected values
   only where determined. [Core facts](core-facts.json) hold the referenced literal
   path tables and structural records. [Prerequisites](prerequisites.json) keep
   core validity separate from extension interpretation.
4. [Source ledger](sources.json) and [input manifest](manifest.json): exact
   quotations, upstream commit/path/line links, source hashes and local input
   digests. The archived `sources/` files retain original bytes and upstream
   relative links; they are excerpts of a repository, not a standalone docs site.
5. [Rereview](review/semantic-review.md), [post-freeze comparison](review/upstream-labels.json),
   [verification](review/verification.md), and [dispositions](dispositions.md).

## Inputs and authority

F00–F07 are exact byte copies of the pin's eight
`conformance/fixtures/*/expected.json` documents. X00–X22 are the 23 complete
`document` objects extracted from `spec/experimental/interpretation-cases.json`.
Those are explicitly **authored contract examples**, not captured producer
output. Extracted copies use the serialization documented in the manifest; their
SHA-256 values are not upstream canonical digests. Both profiles use identical
input bytes. No fixture or input was regenerated through a producer.

The core shape authority, contract prose, applicable fixture meanings, extension
schema and ADR 0008 are inspected at the same commit. Fixture recipes are retained
as context for their declared graph meanings; they cannot inject facts absent
from the JSON that a consumer receives. In particular, a nested recipe is not a
license to infer child presence from a document's name. Existing renderer output,
producer code and reference-test verdicts are not expectation authority.

`core-only` reads core fields and leaves extensions uninterpreted. `opt-in`
recognizes graph-level `x-topology-interpretation` revision 1. The prereview
dispositions are **9 absent, 10 supported-valid, 1 unsupported-revision, 11 invalid**;
all 31 core documents are valid by document/schema inspection. No package validator
ran and no stored structure hash was recomputed. A supported-valid fact remains a
producer assertion, not proof that its evidence locator tells the truth.

## Results and limits

- F2 is not preclassified as a contract contradiction. The legacy routing fixture
  provides candidates and a router-local gap; it does not identify an execution
  entry or the missing edge. X06 adds a confirmed entry and X08 shows confirmation
  with an incoming cycle. X22 preserves candidate uncertainty without a gap.
- Core structure determines join connections with provenance and the locally
  defined path relation. It does not determine actual execution reachability.
- X01/X02 distinguish not-child from opaque-child despite identical core fields.
  Unknown and absent facts remain distinct, and neither means not-child.
- X04 establishes an all-declared assertion, not selection or concurrent execution.
  Invalid, unsupported and absent metadata supply no trusted interpretation.
- No new finding is promoted. The [disposition ledger](dispositions.md) links
  recurring limits to existing findings, distinguishes input-information limits
  from missing contract guarantees, and retains review corrections.

The assistant authored the literal judgments from documents and rereviewed
input-only cards and citations with expected values hidden. This was a same-session
review, not an independent human/model or a claim of memory-blindness. Temporary
standard-library editing scripts copied sources, transcribed fields, expanded the
literal editorial tables and checked their integrity. No graph traversal routine,
consumer implementation or upstream expected-label extraction supplied the initial
semantic judgments. The only substantive rereview correction was the applicability
of expansion to X01's explicitly not-child node; the old row is retained.

After semantic records were frozen, the 23 upstream extension-status labels
agreed with the independently authored dispositions. That is agreement with saved
example labels, **not execution of two consumers**. The separate object-shape
comparison agrees on all 21 applicable revision-1 objects; absence and unsupported
revision remain explicit non-comparisons. No semantic expected values were changed
to match those labels.

No nonempty producer-limitation case, materialized subgraph link, three-level
nesting, multi-graph traversal, Unicode boundary, runtime trace or generated input
is covered by this population. Empty arrays alone do not establish those cases.
Schema validity does not establish producer truth, hash integrity or full behavior.
Historical beta.2 artifacts, findings, gallery and probe evidence remain unchanged.

## Handoff

Stages 0 and 1 are complete for this pinned population: there are no unreviewed
cells, and unsupported factual expectations remain blank. Stage 2 can now design
the comparative device and two consumer adapters using these records. Its runner
must preserve separate profile, support/error and uncertainty states; compare both
against the source-backed judgments and against each other; and investigate
disagreement by asking what the contract determines first.

No consumer API, comparator, generator, framework environment, issue, upstream
publication, topology contract change or release gate is added by this work.
The repository's [evidence conventions](../../docs/evidence.md) continue to apply.
