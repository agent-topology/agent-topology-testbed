# Consumer questions, revision 1

This is a testbed measurement definition, not a topology contract, public API,
or consumer implementation. The [source ledger](sources.json) binds contract
rules to exact quotations, line spans and the pinned upstream commit.

## Population and profiles

The [manifest](manifest.json) identifies 31 complete JSON inputs: eight core
conformance documents (F00–F07) and 23 authored extension examples (X00–X22).
Only the document is consumer input. Fixture recipes, names, provenance labels,
reference tests and upstream outcome fields cannot supply missing node facts.
All graphs in this population have ID `main`; identities remain graph-scoped.

<a id="l-profile"></a>
**L-PROFILE (local measurement rule).** Evaluate the identical document twice:
`core-only` ignores extension content; `opt-in` recognizes only graph-level
`x-topology-interpretation` revision `1` according to ADR 0008. Do not strip,
repair, reorder or re-finalize the document to make it acceptable. Compare
consumers within a profile; differences between profiles measure added information.
Core-only may use core-related guidance in the pinned documents, but never reads
an extension fact. Reading ADR guidance is not itself opting into its wire data.

The prerequisite ledger records core validity and the opt-in extension status
separately. The core-only status is `not-interpreted`, not `absent`. The opt-in
statuses are `absent`, `supported-valid`, `unsupported-revision`, and `invalid`.
Invalid or unsupported extensions supply no trusted facts, including facts that
look individually valid elsewhere in that extension. Keep the valid core visible.
An invalid example is not evidence of a contradiction between contract rules.
Core validity does not verify the stored hash or prove producer assertions true.

## Judgments and uncertainty

Each matrix row is one input × profile × question group. Each answer within it
has its own judgment; do not collapse partially determined groups to one boolean.

| Judgment | Expected-value rule | Required reasoning |
| --- | --- | --- |
| `determined` | `expected` is present, including empty collections or explicit uncertainty states | Input pointers, rule IDs, and a derivation |
| `underdetermined` | `expected` is absent, never an empty set or guessed value | Reviewed sources, unresolved scope, and the missing information/rule |
| `contradictory` | `expected` is absent | Two incompatible obligations for the same question and scope |

`unreviewed` is a workflow state and is not a final judgment. A documented
`unknown` assertion has a determined interpretation; the underlying fact may
remain underdetermined. `no-assertion` is not `not-entry` or `not-child`.
`no-trusted-assertion` means a fact was not admitted by the selected profile.
None of these are implementation errors, unsupported consumer features, or test
passes. A future runner must record its own errors and support separately.

Every `unresolved_*` answer lists exactly the nodes or subject for which a
factual expectation is absent. An empty list of trusted positive assertions is
never an assertion that no positive nodes exist in the actual workflow.
Reasons distinguish input-information limits, profile limits, and explicit
contract non-guarantees. A failed search alone does not establish underspecification.

## CQ1 — Entries

Record `listed_candidates` exactly from `entryNodeIds`; retain a separate list
of `observed_roots`. For every visible node record its trusted entry assertion
and the nodes whose execution-entry meaning remains unresolved. A known fact
means the document asserts that classification with required evidence; this audit
does not verify the framework evidence source.

<a id="l-root"></a>
**L-ROOT (local calculation, grounded in R-ROOT).** Observed roots are visible
nodes with no incoming ordinary edge and no join targeting them. Compute this
also in core-only as an explicitly local structural question, without asserting
that the core contract requires a consumer to compute it. Never substitute this
list for `entryNodeIds`, even if they coincide. An incoming cycle permits a
confirmed entry; an incoming connection does not prove `not-entry`.

## CQ2 — Connections and structural reachability

Record ordinary edges with their original `id`, `source`, `target`, and `kind`.
Record one separate `(joinId, source, target)` connection per join source, retaining
the complete original join and its AND meaning (R-JOIN). Do not merge parallel
relations, erase provenance, or turn a join into independently executable edges.

<a id="l-path"></a>
**L-PATH (local calculation).** Within each graph, a node reaches another if a
directed path of length at least one exists through ordinary edges or join-source
connections. A positive-length cycle includes self-reachability; an isolated node
does not reach itself. Conditional edges count as structural connections, without
proving selection. Never traverse between graphs merely because `subgraphId`
exists. The relation is a set of endpoint pairs; connection records are not sets
to be deduplicated. JSON tables list every source, including empty destination lists.

This relation is an audit-defined graph calculation over contract-defined
connections, not a normative execution/coverage API. Actual execution reachability
remains a separate underdetermined answer. Failure to find an emitted path is
not proof that a routing gap hides no path.

## CQ3 — Recorded uncertainty

Record completeness, every gap (including code, message and full element scope),
and producer limitations separately. R-COMPLETE and R-PRESENT determine what
uncertainty is available to present, not visual styling or severity. Do not infer
a new gap from an unknown extension or from a disconnected node.

Record gap causality separately: which missing relationship produced which other
affected element is not supplied by a routing gap on a router. For documents
without recorded gaps, the causal mapping of *recorded* gaps is an empty map;
this does not assert exhaustive completeness of real behavior (R-LIMIT).

## CQ4 — Nesting

Record materialized `subgraphId` links and per-node trusted child assertions
separately. Missing links do not imply `not-child`. Known `opaque-child` permits
an expansion attempt, not successful expansion or knowledge of internals.
Known `not-child` requires the matching positive evidence. Preserve unknown
reasons and missing facts without substituting names, node types, sentinels,
fixture recipes or producer implementation details (R-CHILD, R-ABSENCE).

List nodes whose child identity remains unresolved. Successful expansion and
complete child contents receive no expectation from these documents, including
those containing a valid known opaque-child assertion.
Exclude admitted known not-child nodes from the child-expansion subject set;
when that leaves no subject, record an empty applicable-node set rather than
inventing an unknown child to expand.

## CQ5 — Outgoing branch relationships

Record the structural connections from CQ2 and each visible node's trusted branch
assertion. `all-declared` is a supported unconditional declaration assertion, not
exclusive selection or simultaneous execution. Preserve explicit unknown reasons;
missing facts are no assertion. Direct edges alone do not establish a complete
inspected declaration surface; joins do not establish divergence policy.

Identify unresolved declaration relationships only at nodes with at least two
ordinary outgoing destinations or a recorded routing gap, unless a trusted
all-declared fact answers that question. This is the local question's applicable
scope, not a new producer emission rule. A node outside that scope has no declared
multi-destination relationship to classify; that is not a claim about hidden
routing. Selection and execution remain separate, underdetermined questions for
the workflow, including valid all-declared and linear cases (R-BRANCH, R-LIMIT).

## Citation and presentation conventions

Matrix `rules` refer to [sources.json](sources.json) or L-PROFILE/L-ROOT/L-PATH
above. `input_pointers` are JSON Pointers into the manifest's complete input;
`scope` names graph/node identities. A pointer to a node collection covers an
explicit absence check over that collection. Core facts are factored into
[core-facts.json](core-facts.json); `expected_ref` under an expected value is a
local document reference to a literal reviewed value, not an instruction to run
a consumer. Resolve the fragment as a JSON Pointer.

Connection and reachability values are preserved separately. Identity lists in
the editorial record use Unicode code point ordering without normalization;
all current IDs are ASCII. This does not measure cross-language Unicode behavior.
No API, validator, comparator, or serialization protocol is introduced here.
