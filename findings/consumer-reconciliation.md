# Consumer evidence reconciliation

**Disposition: retain F1–F8; attach consumer impact and missing-evidence tasks,
not one finding per AT entry.** Observation count measures collected evidence,
not independent contract defects. A new finding needs a distinct bounded claim,
minimal reproduction and a contract question that existing findings do not own.

This 2026-09-12 reconciliation reads Cordboard at
`67a46b43317ffc8474d46dc9b893d88d598f8d86`. The
[source snapshot and hashes](../observations/cordboard-r3/sources/manifest.json)
retain its architecture and relevant ADR/AT documents. They are consumer decision
evidence, not topology contract authority. Current upstream interpretation was
audited separately at `eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`; the
[new R3 extraction](../observations/cordboard-r3/README.md) uses published beta.2.
Those version boundaries must not be collapsed.

## Actual consumer decisions

Cordboard already has executable runtime/archive integrations. Its catalog,
topology/trace viewer and `cord` lifecycle remain planned at this pin
([architecture status](../observations/cordboard-r3/sources/ARCHITECTURE.md#status-and-source-of-truth)).
R1/R2/R3 are accepted policy decisions, not three deployed implementations we
have tested. AT prose reporting experience is retained as reported evidence until
the corresponding inputs, commands and outputs are available.

| Consumer decision | Required input facts | Evidence and disposition | Smallest remaining evidence |
| --- | --- | --- | --- |
| Catalog R1: refuse missing derived topology | Authoritative wire shape, presence/validity, distinction from incompleteness | ADR-0007; architecture warns older `derived`/`declared` words are ownership terms, not literal keys. CQ3 preserves gaps/limitations. | Define actual document-presence boundary before an adapter; missing document, invalid document and valid incomplete document controls. Do not implement a fictitious `derived` key check. |
| Startup R2: refuse structural drift; explicit sync | Fresh and published hash tuples, algorithm/version, successful derivation; metadata is separate | ADR-0011. Existing [V1](../observations/V1/README.md), [D1](../observations/D1/README.md), [E1](../observations/E1/README.md), [K1](../observations/K1/README.md) already cover bounded hash/version/determinism boundaries. AT's beta.1→beta.2 anecdote adds consumer relevance, not another raw replay. | Later adapter checks unchanged/changed structure, failed derivation and unsupported algorithm separately. No new broad epic-37/hash campaign is needed here. |
| Catalog R3: interrupt-in-parallel rule and explicit override | Declared edges, static interrupt sites, and separately justified selection/execution meaning | AT-3 + F1. [Eight fresh-process records](../observations/cordboard-r3/run/comparison.json) show the literal Action-4 model cannot distinguish single/list conditional selection. | Review policy scope and external failure applicability before claiming false positives/negatives about resume safety. No core-field requirement follows automatically. |
| Topology/trace correlation | Retained parent identity across depth, trace node identifiers and matching policy | AT-1; CQ4/F3 cover opacity, not runtime correlation. | One nested graph at depth 0 and 1, actual parent/child spans and minimal matching decisions. Do not invent spans or infer parentage by splitting IDs. |
| Catalog identity and display name | Registration identity vs display label, name ownership and hash scope | AT-5 + ADR-0011. New extraction retains `compile(name="r3-minimal")` as graph name; [D1](../observations/D1/README.md) already has named inputs. Lack of a `describe(name=...)` parameter does not imply names cannot be supplied. | Two explicitly named compiled graphs and one default-named control, then inspect the actual registration requirement. A forced document-mutation claim is not established. |
| Viewer entries, connectivity, uncertainty and grouping | Confirmed vs candidate entry, edges plus joins with provenance, gaps, roles and nesting facts | CQ1–CQ5 are reusable prerequisites. AT-2/F5, AT-4/F4, F3 and F7 remain distinct. | Implement questions demanded by these decisions when the real adapter exists; do not make the renderer the expected-value authority. |
| Independently deployed graph dependencies | Producer-supported framework range and failure behavior | AT-6 + ADR-0001. Separate processes permit different dependencies but do not promise arbitrary extractor compatibility. | Supported-boundary and immediately-outside-range controls with public producer errors; only then decide whether a contract claim or support-policy request exists. |

## AT/F dispositions

| Testbed | Cordboard | Reconciled claim |
| --- | --- | --- |
| F1 | AT-3 | Consumer impact is now concrete: Action 4 uses a structural predicate where its rationale needs an execution fact. New evidence supports existing F1; it does not prove a hazardous run was admitted. |
| F4, separately F7 | AT-4 | Empty joins on ordinary converging edges and join-only fixture connections are not inherently contradictory. Current guidance distinguishes ordinary edges from explicit AND joins and provides derived links with join provenance. Obtain AT-4's original builder calls before alleging producer inconsistency. F7 owns the narrower first-trigger/once-only OR limitation, not missing AND semantics. |
| F5 | AT-2 | Same sentinel-display requirement. Current experimental roles improve it; published beta.2/core-only and vendor-neutrality boundaries remain. No duplicate finding. |
| F3 | — | Depth-0 opaque-child knowledge matters to Cordboard's default, but is not AT-1's expanded-parent correlation problem. |
| — | AT-1 | Retain as a consumer observation requiring a topology-plus-trace replay; no F9 without it. |
| — | AT-5 | Preserve reported naming workaround, qualify the claimed necessity with actual compiled-name extraction. Establish identity requirements before promotion. |
| — | AT-6 | Retain support-policy concern, not a proven contradiction of process isolation. |
| F2, F6, F8 | — | Existing scopes remain. AT coverage is not required to retain them. F8 differs in full canonical bytes while tested structure hashes agree; do not label it R2 drift. |

The [current upstream disposition](upstream-status.md) remains authoritative for
the local review of F1–F8. Historical beta.2 findings and artifacts are unchanged.
The new experiment neither reopens fixed affordances nor claims current-source
experimental changes are available in published beta.2.

## Updated consumer work order

1. Start with the decisions above and their source-derived obligations. Preserve
   the [CQ audit](../observations/consumer-contract-audit/README.md) as a reusable
   fact layer; it is complete for its pinned population, not obsolete.
2. Measure one bounded policy-information boundary first: the R3 Action-4 model
   and conditional single/list counterexample. This step is now recorded. The
   oracle is authored from the ADR and recipe, not computed by either consumer.
3. Next collect the minimal missing evidence for correlation and naming. R1/R2
   adapters require actual integration boundaries; existing hash evidence can
   supply their test inputs. A second generic structural interpreter is no longer
   the immediate prerequisite, and hash consumption is a real R2 use case.
4. Add independent adapters and generated valid documents only for questions
   needed by those consumers. Compare both to cited obligations and to each other;
   keep unknown, unsupported, invalid and implementation failure distinct. For any
   mismatch ask whether the contract determines the answer before changing code.
5. Framework probes supply native observations, not topology documents. Feeding
   them into this device still needs a second producer. No producer is fabricated
   here to meet that milestone.

No upstream issue is posted, no Cordboard code or policy is changed, and no
release gate or new core contract is introduced. Further AT entries become
findings only when their distinct claim survives the same reproduction standard.
