# Cross-framework reconciliation and local upstream handoff

Final synthesis for [P7 / #9](https://github.com/agent-topology/agent-topology-testbed/issues/9),
reviewed 2026-09-12. [Findings index](README.md) ·
[verification and input snapshot](../observations/P7/README.md).

The expanded evidence supports **programming-model-specific extraction**, not a
framework-wide yes/no answer. Declaration, selection, execution and invocation
identity remain separate. F1/F3 corrections survive; F7 remains the distinct,
bounded OR firing-policy finding. P8/A1 add explicit non-findings and candidate
boundaries, not F8. No probe here emits an agent-topology document.

## Evidence inventory and verdict rules

The [47-claim completed-cohort ledger](completed-cohort-dispositions.md) remains
the authoritative inventory for P0–P6/C1/S1/T1, including exact record sections,
versions, reasons and smallest follow-ups. This review incorporates all its rows
without rewriting that frozen cohort. The P8/A1 inventory below completes the
later increment. Each input link supplies minimal native fixtures, independent
assertions, source/lock hashes, both saved runs, normalization and exact commands.

| Input | Native question and reproduction | Evidence / pin |
| --- | --- | --- |
| P0 | [Two-task/op baselines, assertions and records](../observations/P0/README.md); [commands](../probes/README.md#airflow-run) | Static/execution; Airflow 2.10.5, Dagster 1.13.22 |
| P1 | [Branch single/multiple/none](../observations/P1/README.md) | Static/callable/execution; Airflow 2.10.5 |
| P2 | [Optional outputs and required-output control](../observations/P2/README.md) | Static/execution; Dagster 1.13.22 |
| P3 | [Two grouped members between before/after tasks](../observations/P3/README.md) | Static/execution; Airflow 2.10.5; source provenance unresolved |
| P4 | [Two aliases of one child and two-input consumer](../observations/P4/README.md) | Static/execution; Dagster 1.13.22 |
| P5 | [Mapped task with 0/1/2 values and aggregations](../observations/P5/README.md) | Static/execution; Airflow 2.10.5 |
| P6 | [Dynamic map/collect with 0/1/2 keys](../observations/P6/README.md) | Static/execution; Dagster 1.13.22; source provenance unresolved |
| C1 | [Router/listener and four AND/OR cases](../observations/C1/README.md) | Static/callable/execution; CrewAI 1.15.21 |
| S1 | [Choice, Parallel, Map JSON and invalid-reference controls](../observations/S1/README.md) | Static plus documentary semantics; ASL retrieved 2026-09-11, CPython 3.14.7, stdlib only |
| T1 | [Two workflow/two activity definitions and API review](../observations/T1/README.md) | Static/documentary only; temporalio 1.18.0 |
| P8 | [Two tasks, linear and loop 0/2; setup/run commands](../observations/P8/README.md#reproduction-and-state-isolation) | Static/execution plus documentary review; Prefect 3.6.22 |
| A1 | [Two agents, two models, forward/reverse inputs; commands](../observations/A1/README.md#reproduction) | Static/execution plus documentary review; AgentChat/Core/Ext 0.7.5 |

All SDK records use CPython **3.11.16** and separate hash locks. S1 has no SDK
lock or dated spec revision; its retrieval date is the recorded boundary.
Documentary API conclusions do not acquire execution status from sharing a
README with executed cases. In particular, P8 visualization and A1 HITL remain
documentary; C1's additional explorations are not separately paired experiments.

**Supported** means the bounded observed fact or recorded limitation survives;
**contradicted** means the stated inference fails a counterexample or normative
rule; **unresolved** means the necessary evidence is absent. These verdicts do
not mean a new format defect, framework equivalence or upstream acceptance.
The cohort's correction/reinforcement/non-finding categories retain their reasons.
This explicit verdict crosswalk covers every original claim ID exactly once:

| Cohort link | Supported bounded observations/limits | Contradicted inference | Unresolved claim |
| --- | --- | --- | --- |
| [P0](completed-cohort-dispositions.md#p0) | P0-a, P0-b | — | — |
| [P1](completed-cohort-dispositions.md#p1) | P1-b, P1-d | P1-a, P1-c | — |
| [P2](completed-cohort-dispositions.md#p2) | P2-b | P2-a, P2-c | P2-d |
| [P3](completed-cohort-dispositions.md#p3) | P3-d | P3-a, P3-b, P3-c | P3-e |
| [P4](completed-cohort-dispositions.md#p4) | P4-d | P4-a, P4-b, P4-e | P4-c |
| [P5](completed-cohort-dispositions.md#p5) | P5-b, P5-d | P5-a | P5-c |
| [P6](completed-cohort-dispositions.md#p6) | P6-c | P6-a, P6-b | P6-d, P6-e |
| [C1](completed-cohort-dispositions.md#c1) | C1-d, C1-e, C1-f | C1-a, C1-b, C1-c | C1-g |
| [S1](completed-cohort-dispositions.md#s1) | S1-a, S1-b, S1-e | S1-c, S1-d | S1-f |
| [T1](completed-cohort-dispositions.md#t1) | T1-d | T1-a, T1-b | T1-c, T1-e |

Read verdicts with the linked row's scope: C1-c contradicts **full OR policy
preservation by ordinary edges**, hence supports F7's narrower gap; P3-b rejects
promotion of an observed root into a confirmed entry, without reproducing a new
gap-caused orphan. P4-e rejects an asserted equivalence, not the possibility of
a future explicit mapping. Supported limitation rows retain their untested
scope; they do not affirm the overbroad hypothesis in a row title.

## P8 disposition

Prefect **3.6.22**, CPython **3.11.16**, direct synchronous calls only.
[Minimal fixtures](../probes/boundaries/prefect/fixtures.py),
[literal assertions](../probes/boundaries/prefect/expected.json),
[lock](../probes/boundaries/prefect/requirements.lock),
[run 1](../observations/P8/run-1.json), [run 2](../observations/P8/run-2.json),
[native 1](../observations/P8/run-1.raw.json), [native 2](../observations/P8/run-2.raw.json),
[source review](../observations/P8/source-review.json),
[commands and normalization](../observations/P8/README.md#reproduction-and-state-isolation)
apply to every row. S = static, E = execution, D = documentary source inspection.

| Claim | Q / evidence section and result | Verdict, decision and remaining evidence |
| --- | --- | --- |
| P8-a: public metadata enumerates a selected flow's invocation graph | Q1/Q2, S: `static.flows/tasks`, `bodies_entered=[]`; supplied definitions have names/versions/keys but no invocation membership or edges | **Contradicted for this inspected surface; non-finding.** Metadata inventory cannot stand in for a dependency producer. A public no-body-execution graph API or validated restricted DSL/analyzer could change that assessment. |
| P8-b: visualization is extraction without evaluating user code | Q1, D: source review of `Flow.visualize()` calls `self.fn`; run-graph routes instead require a flow-run UUID | **Contradicted; non-finding.** Visualization is a positive path-evaluation candidate before task execution, not static extraction. No visualization was run. Validate safe input-specific evaluation separately only if that candidate is pursued. |
| P8-c: runtime APIs retain repeated invocations and their input edges | Q2/Q3, E: `execution.linear/loop-0/loop-2`, `task_runs`, `dependencies`, body order/results; counts 2/0/4 and edges 1/0/2 | **Supported; non-finding.** Public task-run observation works for this fixture. Two definitions cannot replace four instances. This is no declaration, branch-choice or parallelism result; `.map()`, `.submit()` and distributed runners are untested. None needed to settle this case. |
| P8-d: dynamic keys are structural ordinal IDs | Q7, E/D: native `task_run.dynamic_key` values are distinct UUID4, explained by pinned direct-call source | **Contradicted; non-finding.** Preserve native UUIDs separately from definition task keys and comparison-local positions. The original ordinal hypothesis remains rejected, not normalized into a pass. |
| P8-e: repeatability and lifecycle evidence are bounded | Q7, S/E: names, `p8-v1`, task keys repeat; UUIDs differ; `PENDING/RUNNING/COMPLETED`, `run_count=1`, input ports and order survive comparison | **Supported; non-finding.** Runtime observer must preserve identity/multiplicity/state. No universal key stability across edits/versions and no retries were tested; none needed for this verdict. |
| P8-f: pauses imply statically placed resumable interrupts | Q6, D: `pause_flow_run`, typed input/resume documented; no pause fixture | **Unresolved; non-finding.** Native capability is not placement evidence. If a consumer needs it, first choose one pause with a specific task anchor and an explicit target relation, then test that relation. |
| P8-g: these linear/loop results settle joins or nested flow boundaries | Q4/Q5: no multi-source or child-flow input | **Unresolved; non-finding.** A one-source B input is no join test. Only if required, add two sources/one consumer for convergence, or one parent/child invocation for boundary visibility; run-graph documentation alone cannot settle either. |

P8's failed FastAPI/Starlette combination was repaired with compatibility pins
before accepted runs; it is not negative framework capability evidence. A failed
source URL likewise supplied no observation. Local completed runs establish the
measured outcome; no Prefect 2 or universal Prefect 3 conclusion follows.

## A1 disposition

AutoGen AgentChat/Core/Ext **0.7.5**, CPython **3.11.16**.
[Two-agent input](../probes/boundaries/autogen/probe.py),
[literal message oracle](../probes/boundaries/autogen/expected.json),
[lock](../probes/boundaries/autogen/requirements.lock),
[static record](../observations/A1/static.json),
[run 1](../observations/A1/run-1.json), [run 2](../observations/A1/run-2.json),
[tagged source review](../observations/A1/source-review.json), and
[commands/normalization](../observations/A1/README.md#reproduction) apply to every row.
No separate callable evaluation; selector choices were recorded inside `team.run()`.

| Claim | Q / evidence section and result | Verdict, decision and remaining evidence |
| --- | --- | --- |
| A1-a: SelectorGroupChat participant configuration declares execution dependencies | Q1/Q2, S: `cases.selector-*.static.component.config`, participants alpha/beta, no graph, selector callable omitted | **Contradicted for this surface; non-finding.** Participant inventory is supported; static dependencies require additional declarations or independently validated restricted source analysis. This says nothing about every AutoGen model. |
| A1-b: GraphFlow exposes an explicit static execution graph | Q1/Q2, S: `cases.graph-*.static`, alpha → beta, root alpha/leaf beta, serialized graph and activation defaults; model/selector call counts zero | **Supported; non-finding.** Positive static-producer candidate for this declared subset. Public experimental API needs version handling; callable predicates are omitted from serialization. No lossless exporter for arbitrary GraphFlow is established. |
| A1-c: input state changes speaker selection while the declared chain stays fixed | Q3, E: `cases.*.messages`, `selector_calls`, `model_calls`, `stop_reason`; selector forward/reverse changes order, both graph inputs remain alpha/beta | **Supported; non-finding.** The positive and negative controls change applicability by model. One reply per agent, zero selector-model fallback; no live LLM, fan-out, concurrency or message-routing equivalence was measured. |
| A1-d: exposed all/any controls establish multi-source join equivalence | Q4, S/D: GraphFlow activation/group/condition defaults and tagged guide; only a chain executed | **Unresolved; non-finding.** SelectorGroupChat has no join input either. A two-source/one-target GraphFlow control with a missing source and explicit normative mapping is the minimum before comparing firing policy with F7. Do not allocate another finding from API names. |
| A1-e: team or graph nesting is established | Q5: neither model contains a nested boundary/ports fixture | **Unresolved; non-finding.** If needed, inspect one supported nested invocation and retain parent/child identities before a target mapping. The two-agent graph is no F3 reproduction. |
| A1-f: stopping equals durable resumable HITL or a structural interrupt | Q6, S/E/D: configured cap, observed max-turn/graph-complete stops; documented UserProxy, handoff termination, save/load and experimental pause/resume | **Unresolved beyond observed stopping; non-finding.** These are distinct APIs and no human interaction was run. For a needed claim, choose one specific human-input/continuation API and node anchor, then test its documented resume boundary. |
| A1-g: structural names and generated message identities can be conflated | Q7, S/E: alpha/beta and endpoints repeat; 12 native UUID4 message IDs per run are unique/disjoint; only IDs/timestamps excluded from equality | **Contradicted; non-finding.** Retain names and ordered native messages separately. No public run UUID was collected or fabricated; no stability claim beyond the two processes. |
| A1-h: one negative model establishes framework-wide static impossibility | Q1/Q2, S/E: A1-a versus A1-b/c | **Contradicted; non-finding.** GraphFlow revises that candidate assessment directly. No further affirmative chain, field promotion or vendor-neutrality claim is warranted by this result. |

The documented null-field serialization and generated timestamp corrections
remain in A1's provenance. They do not weaken agent order/count assertions.
No new finding ID is warranted: these observations concern extraction surfaces,
execution and untested scope, without a new target-contract counterexample.

## Integrated comparison and changed decisions

The [canonical M1 matrix](../probes/README.md#answer-matrix) covers **eight
programming-model rows × seven questions = 56 cells**. Every cell links to its
question's scoped evidence or explicit untested limitation. Its capability
labels deliberately differ from the claim verdicts above. Roots are compared
under Q2; runtime definitions/instances under Q3/Q7. No shared branch-mode enum
is imposed on native observations.

| Question | Surviving result and decision impact | Contradicted or unresolved boundary |
| --- | --- | --- |
| Q1 static access | Airflow declarations, Dagster native graphs, CrewAI exported inspection, ASL JSON and GraphFlow each expose a bounded structural surface. | T1/P8/Selector inventories cannot certify dependency extraction. GraphFlow defeats framework-brand exclusion. Dagster/CrewAI source-visible access is not a documented-public guarantee. |
| Q2 nodes, edges, roots | Airflow tasks, Dagster invocation/port tuples, CrewAI methods/listeners, ASL scoped states and GraphFlow execution nodes retain native identities. ASL `StartAt` is authored; P3/GraphFlow roots are observed structural roots. | Neither roots nor participant membership imply confirmed execution entry or orphan cause. P8 instances come from runtime records; T1 has no invocation graph. F2 remains improved upstream, causality unknown. |
| Q3 branch and dynamic count | P1 callback returns, P2 output emissions and C1 selected labels measure different things. P8 loops and A1 speakers add model-specific execution controls. P5/P6 keep declarations fixed for 0/1/2. | Operator-class exclusivity, label-count = listener-count, cardinality = concurrency and static declaration = execution are contradicted. ASL Choice is declared/documentary, not an evaluated AWS selection. |
| Q4 convergence | Airflow trigger rules depend on states; Dagster required inputs and empty collect differ from skipped Airflow mapping; CrewAI exposes AND/OR. Target joins have normative AND meaning. | Missing mode ≠ missing semantics. C1 once-only OR is F7; GraphFlow defaults, ASL Parallel declarations and successful Dagster inputs do not establish universal equivalence, reset or failure policy. |
| Q5 grouping/nesting | P3 membership, P4 reusable scoped invocations/ports and S1 nested JSON narrow F3's analogy. | TaskGroup is not an opaque executable node; these probes do not emit a depth-0 topology. P4 public enumeration, dynamic nesting and other models' untested children remain bounded questions. |
| Q6 interrupts/HITL | S1/T1/P8/A1 document different callback, handler, pause, input and continuation concepts; A1 observes termination only. | No structural before/after HITL mapping is established. Untested Airflow/Dagster/CrewAI cells are explicit, not evidence of absent capability. |
| Q7 identity | Dagster alias/key scopes, Airflow `(task_id,map_index)`, ASL local scope and P8/A1 native UUID separation survive comparison. | Repeated definitions are not repeated-instance IDs; two runs cannot prove stability after edits. CrewAI has no dedicated identity-stability experiment. P3/P6 source provenance remains unresolved. |

**Candidate decisions changed:** use the specific model and supported API as the
unit of applicability. GraphFlow is a positive explicit-graph candidate; the
Selector model supports inventory/input-specific observation. Prefect's tested
runtime path is supported while its visualization/source-analysis paths need
separate validation. Temporal remains a bounded static limit with untested
history/source-analysis candidates. Dagster ops/graphs remain a plausible
candidate, conditional on documented enumeration or an explicit supported API
scope; assets/partitions and any delivery milestone remain unverified.

**Prior conclusions retained or corrected:** F1 now concerns declarations versus
selection/execution, F3 retains its historical depth-0 issue with a narrower
source analogy, F4 joins remain authoritative AND relationships, and F7 retains
only its OR-policy gap. Core promotion still needs independent producer and
consumer evidence under ADR 0008. Neither a failed negative hypothesis nor a
positive local control changes that accepted contract by itself.

**Experiments that would add no decision evidence now:** another passing linear
chain, larger map cardinalities, a full framework rerun to refresh prose, or more
OR repetitions cannot supply a missing normative reset rule. P8 visualization
execution cannot prove zero-body-execution extraction. A1's chain cannot answer
multi-source joins. Recover P3/P6 source bytes before a targeted new reproduction;
do not erase their hashes. Only pursue the minimal follow-ups in the ledgers if
their stronger claims become necessary; no new work is silently scheduled.

## Upstream handoff dispositions

Live issue state and HEAD were checked in the [input snapshot](../observations/P7/review-inputs.json).
HEAD remains **eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe**. The
[accepted ADR 0008](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md)
and [producer-to-consumer acceptance record](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/consumer/README.md)
were read at that exact pin. The latter reports LangGraph Python 1.2.11 and
LangGraph.js 1.4.14; it is upstream-recorded verification, not a new testbed run.
The [existing status review](upstream-status.md) retains dedicated PRs, release
boundaries and F5/F6 dispositions; those edits are not duplicated here.

| Upstream issue | Local evidence ready for consideration | Disposition and acceptance boundary |
| --- | --- | --- |
| [#95](https://github.com/agent-topology/agent-topology/issues/95) | [F1 history](F1-fan-out-semantics/HISTORY.md), [F3 qualification](F3-opaque-subgraph/README.md), [cohort ledger](completed-cohort-dispositions.md) | Closed reproduction work preserves beta.2. New native probes supplement reasoning; they do not revalidate original injected trials as extraction. |
| [#96](https://github.com/agent-topology/agent-topology/issues/96) | F1/F3/F7 and P8/A1 model boundaries above | Accepted experimental revision 1 remains the decision. Known structural facts need proof; no runtime-cardinality or OR-reset fact is added. Promotion requires a separate ADR and producer/consumer evidence. |
| [#97](https://github.com/agent-topology/agent-topology/issues/97) | [F1](F1-fan-out-semantics/README.md), P1/P2/C1, ASL declaration control | Improved `all-declared`; router selection remains unknown. Integrated direct/single/list controls support this, not exclusive/concurrent modes. Reuse existing F1 work; no duplicate filing. |
| [#98](https://github.com/agent-topology/agent-topology/issues/98) | P3/P4/S1 through [F3](F3-opaque-subgraph/README.md) | Improved opaque-child interpretation; ordinary callable stays unknown. Upstream child/ordinary controls supply the equal-ID/core-hash test absent from the historical gallery. No second producer or guaranteed expansion follows. |
| [#100](https://github.com/agent-topology/agent-topology/issues/100) | P3-b/S1-e, A1 graph roots | Improved confirmed-entry distinction; observed roots and unresolved causality remain. No native probe reproduces a new gap-orphan target mapping. |
| [#101](https://github.com/agent-topology/agent-topology/issues/101) | C1-b/c, [F7](F7-or-firing-policy/README.md) | Join helper affordance fixed in source; join identity/AND remain distinct from edges. This does not resolve once-only OR firing. |
| [#103](https://github.com/agent-topology/agent-topology/issues/103) | All local claim dispositions as contextual evidence | Closed integrated acceptance uses real LangGraph producer output and independent consumer expectations. Our framework-native records do not satisfy another producer's conformance, release qualification or public-registry verification. |

[F7's unposted draft](F7-or-firing-policy/ISSUE.md) is the distinct local handoff:
ordinary connections do not establish early-fire/suppress-later behavior with a
reset boundary. #96/#101 supply related context, not a dedicated F7 resolution.
The smallest next evidence is a normative mapping checked against the same four
C1 records. No upstream issue/comment, contract change or publication occurs here.

## Delegated outputs and epic outcome review

All listed #9 dependencies were closed at review time; that is provenance, not
the success criterion. The five disposition outputs were inspected directly:

| Task | Verified delivered output and consistency |
| --- | --- |
| [#27](https://github.com/agent-topology/agent-topology-testbed/issues/27) | [F7](F7-or-firing-policy/README.md), mapping, saved audit, draft and C1 correction distinguish implicit AND from once-only OR. No-semantics and complete-edge-equivalence hypotheses remain withdrawn. |
| [#28](https://github.com/agent-topology/agent-topology-testbed/issues/28) | [Active F1 and history](F1-fan-out-semantics/README.md) preserve injected trials, reject operator exclusivity and use current revision 1; no stale core-branch recommendation is reinstated. |
| [#29](https://github.com/agent-topology/agent-topology-testbed/issues/29) | All 47 [cohort rows](completed-cohort-dispositions.md) retained with evidence/backlinks; source mismatches P3-e/P6-e remain visible. No duplicate F7/F8. |
| [#30](https://github.com/agent-topology/agent-topology-testbed/issues/30) | [Index](README.md) and [upstream review](upstream-status.md) separate historical versions, merged improvements and consumer/release evidence. Live HEAD agrees with its pin. |
| [#31](https://github.com/agent-topology/agent-topology-testbed/issues/31) | [Closure checklist](../docs/issue-planning.md#probe-closure-disposition) and [promotion layers/examples](../docs/evidence.md#promotion-from-observation-to-finding) are present. P8/A1 now have claim dispositions, index links, observation backlinks, decision impact and minimal follow-ups here. |

Review of **each epic #1 success item** against actual evidence:

| Epic success evidence | Disposition |
| --- | --- |
| Separate reproducible Airflow/Dagster environments and minimal executable examples | **Supported:** P0 locks and paired baseline records; no combined environment or CI. |
| Every claim links question/input/assertions/class/commands/limits | **Satisfied with explicit provenance limits:** inventory links and both ledgers cover 62 claims. P3/P6 assertions match saved records, but exact producing source bytes are unresolved; neither is certified as freshly reproduced. |
| Selection distinct from execution/concurrency | **Satisfied:** P1/P2/C1 counterexamples plus P8/A1 controls; no concurrency measurement inferred. |
| Grouping, nesting, roots and convergence compared without equivalence | **Satisfied:** P3/P4/S1 and F2/F3/F7 dispositions, including public-API and contract limits. |
| Dynamic definitions/instances recorded for 0/1/2 | **Supported within provenance limits:** P5/P6 paired cardinalities; skipped representative versus no mapped step/empty collect preserved. P8 loop 0/2 is separate and does not replace the 0/1/2 experiment. |
| F1/F3 corrected; beta.2 intact | **Satisfied:** linked corrections/history and unchanged raw artifacts; no gallery regeneration. |
| Final supported/contradicted/unresolved comparison with upstream relevance | **Satisfied locally:** complete M1, 47-row crosswalk, 15 later claims and seven upstream mappings above; no release or neutrality conclusion. |

The epic's six **expanded acceptance criteria** also receive explicit review:

| Expanded criterion | Disposition |
| --- | --- |
| Seven questions by version/model, preserving reproduction instructions | **Satisfied:** all eight rows and 56 linked cells remain; only matrix navigation/qualifications changed, not setup/run commands. |
| CrewAI compared to normative joins before promoting F7 | **Satisfied:** #27's pinned contract audit establishes implicit AND and the narrow OR-policy counterexample; the original hypothesis is withdrawn. |
| ASL static/documentary, no AWS validation/execution claim | **Satisfied:** S1 declarations and local invalid-reference controls retain that boundary throughout the synthesis. |
| Temporal/Prefect/AutoGen bounded by SDK/model/API, GraphFlow positive control | **Satisfied:** T1, P8-a/b and A1-a/b/h distinguish metadata, body evaluation, explicit declarations and runtime observation. |
| Candidate suitability separated from core eligibility/vendor neutrality | **Satisfied:** the candidate assessment is conditional on a supported subset and independent producer/consumer validation; Dagster has no promised milestone. |
| Questionnaire backfilled without expanding every unanswered question | **Satisfied:** both ledgers and M1 retain untested convergence/nesting/HITL/identity scope and minimal optional follow-ups; no new probe or task is scheduled. |

**Outcome disposition:** the bounded decision-oriented investigation is satisfied
locally, including explicitly unresolved source provenance, unsupported APIs and
untested stronger semantics. These are dispositioned limits, not failed setup
counted as a successful measurement. The evidence supports distinguishing what
is statically observable, execution-specific and unresolved; it does not support
an unqualified “all probes fully reproducible from current bytes” claim.
Epic closure can be considered after this synthesis is reviewed and merged,
on this outcome assessment rather than child counts. This work leaves epic #1
open and makes no GitHub state change; its PR should close only leaf #9.
