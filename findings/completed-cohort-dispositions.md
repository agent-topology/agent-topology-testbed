# Completed-cohort claim dispositions

Disposition ledger for [testbed #29](https://github.com/agent-topology/agent-topology-testbed/issues/29),
reviewed 2026-09-12. [Back to findings](README.md).

The frozen input cohort is **P0–P6, C1, S1 and T1** (ten observation groups),
from evidence baseline `2dda397a6f0675f4fdbf0a1cedb52257de1c52de`.
Later corrections are linked explicitly. P8/AutoGen and final P7 reconciliation
are separate increments, not prerequisites. This ledger classifies material
claims, not probe success or one finding per framework.

## Disposition and contract rules

- **Reinforcement/correction** links an existing F1–F6 claim; it does not
  revalidate that finding's historical reproduction or its current upstream status.
- **Rejected hypothesis** retains a contradicted or unsupported inference and why.
- **Bounded limitation** includes successful baseline/control observations and
  native framework/API limits that establish no distinct target-format defect.
- **Insufficient evidence** names the smallest decision-changing follow-up.
  These are candidates, not scheduled work or blockers for this ledger.
- **New finding** requires a separate target-contract argument and reproduction.
  The cohort's distinct OR-policy consequence is already published as **F7** by
  [#27](https://github.com/agent-topology/agent-topology-testbed/issues/27).
  [F1](F1-fan-out-semantics/README.md) is already rewritten by
  [#28](https://github.com/agent-topology/agent-topology-testbed/issues/28).
  These are completed local dispositions, not pending investigation placeholders
  and not upstream filings. No additional independent reproduced claim warrants
  F8 here; no ID is allocated or reserved. F7 must not be reused.

Target comparison is fixed to upstream
[`eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`](https://github.com/agent-topology/agent-topology/tree/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe),
the source pin used by F1/F7, rather than an assertion about a released package.
The [0.1 contract](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/0.1-contract.md#candidate-contract)
records structure, provenance and uncertainty. Its
[concepts guide](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/guides/concepts.md)
explicitly declines to derive runtime fan-out count from conditional edges.
The separate [interpretation revision 1](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/experimental/interpretation-v1.schema.json)
has branch, subgraph, sentinel and entry facts; it has no mapped-instance or
runtime-cardinality contract. [ADR 0008](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md)
requires structural proof for known facts: an observed root is separate from a
confirmed entry, and TaskGroup analogy cannot prove a compiled child. Thus native
runtime differences below are not automatically format defects. A lossy producer
mapping must also show that the discarded distinction belongs to the claimed
contract; none of these probes emits a topology document.

**Historical scope:** F1–F6 began at beta.2/testbed `571e881e6d509b6e26ff8bf14b98e207d12e7ce9`.
This ledger does not rewrite those artifacts or reconcile all current upstream
statuses; the separate [D4 upstream status review](upstream-status.md) now records
that reconciliation for [#30](https://github.com/agent-topology/agent-topology-testbed/issues/30).
F7 records beta.2, C1's upstream `3715dd3`, and the pin above separately.

## Reading the inventory

Each group heading supplies the version for every row beneath it. **S** = static
inspection; **C** = direct callable evaluation; **E** = framework execution;
**D** = source/documentation reasoning, never a substitute for execution.
JSON field paths are exact record sections. A linked run 1's run 2 and standalone
modes are linked in that group's results table; the verification below checks
all pairs, not just the examples linked in rows. Claim IDs are local to this ledger.
[Q1–Q7](../probes/README.md#common-question-matrix-m1) mean static extractability,
explicit nodes/edges, fan-out, convergence, nested boundaries, interrupts/HITL,
and identity respectively. The decision column states the consequence for a
prospective producer or consumer, not a new wire recommendation.

## P0

Airflow **2.10.5**, Dagster **1.13.22**, CPython **3.11.16**.
[Cases, assertions and pairs](../observations/P0/README.md#cases-and-independent-assertions).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| P0-a: the two-node dependency is inspectable and both steps succeed locally | S/E: [Airflow](../observations/P0/airflow-1.json) `static.dependencies`, `execution.task_instances`; [Dagster](../observations/P0/dagster-1.json) `static.dependencies`, `execution.step_success_keys`, `second_output=2` | Q1, Q2 | **Bounded limitation — baseline-only.** Establishes viable isolated probe inputs; passing linear extraction/execution is no defect and does not reproduce F1/F3. |
| P0-b: normalized structural/step identities repeat | S/E: same records' task IDs, port tuples and step keys; [normalization](../observations/P0/README.md#normalization-and-limitations) | Q7 | **Bounded limitation.** Producers can retain these identities for these two runs. Generated IDs were excluded; universal stability, production ordering and concurrency are not measured. |

## P1

Airflow **2.10.5**, CPython **3.11.16**.
[All single/multiple/none records](../observations/P1/README.md#observed-results).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| P1-a: operator class or declared edges imply exactly-one selection | S/C/E: [multiple](../observations/P1/branch-multiple-1.json) `static.router_downstream_declared`, `callable.selected_targets_normalized`, `execution.task_instances` | Q1, Q2, Q3 | **Correction of [F1](F1-fan-out-semantics/README.md#correction-p1).** Two selected targets both succeed. Withdraw the exclusive inference; preserve declaration, selection and execution separately. No duplicate F1 finding. |
| P1-b: equal declared shape permits zero, one or two successful destinations | S/C/E: [none](../observations/P1/branch-none-1.json), [single](../observations/P1/branch-single-1.json), multiple above; `static`, `callable`, `execution` | Q3 | **Reinforcement of F1.** Callback evaluation alone cannot certify downstream work; the saved execution supplies that evidence only for these inputs. |
| P1-c: identical incoming edges determine a join's eligibility | S/E: single above, `static.join_trigger_rules` and `execution.task_instances`: all-success join skips, none-failed/min-one succeeds | Q4 | **Rejected hypothesis.** Native state-sensitive trigger rules matter. Consumer must not infer a universal policy from adjacency. F1 records this distinction; [F7](F7-or-firing-policy/README.md#contract-versions-and-authority) owns convergence interpretation. This does not prove an independently supported mapping of every Airflow rule into the target AND contract. |
| P1-d: other trigger rules, mapped/group branch targets or actual concurrency follow | E/D: [limitations](../observations/P1/README.md#normalization-and-limitations) | Q3, Q4, Q7 | **Bounded limitation.** Only the fixed router and two rules were exercised with serial local execution; no new defect or universal scheduling/identity claim. |

## P2

Dagster **1.13.22**, CPython **3.11.16**.
[Claim record](../observations/P2/README.md#claim-record) and
[all none/single/multiple pairs](../observations/P2/README.md#observed-results).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| P2-a: optional-output declarations predict which outputs a run emits | S/E: [none](../observations/P2/conditional-none-1.json), [single](../observations/P2/conditional-single-1.json), [multiple](../observations/P2/conditional-multiple-1.json); `static.output_is_required`, `execution.emitted_outputs` | Q1, Q2, Q3 | **Reinforcement of [F1](F1-fan-out-semantics/README.md#measured-distinctions).** Static sections agree while emission differs. Preserve optionality without predicting selection. |
| P2-b: events distinguish executed consumers from missing-output skips | E: same records, `execution.step_success_keys`, `step_skipped_keys`, `consumer_outputs` | Q3, Q7 | **Bounded limitation — positive runtime observation.** Event identities support this observer subset, not a static producer's scheduling prediction. No separate format defect. |
| P2-c: the required-output fan-out proves concurrency | E: same records, both `consumer_fanout_*` outputs are 100 in every case; [control discussion](../observations/P2/README.md#the-fan-out-control-did-not-vary-with-the-case) | Q3 | **Rejected hypothesis.** Completion of both consumers in an in-process executor measures participation, not simultaneous execution. |
| P2-d: optionality determines multi-input convergence generally | S/E: [claim record](../observations/P2/README.md#claim-record), no two-input consumer in this fixture | Q4 | **Insufficient evidence.** If a producer needs optional-input join meaning, use one two-input consumer, one required and one omitted optional output, and compare with the both-present control. P4's successful required inputs do not answer this. |

## P3

Airflow **2.10.5**, CPython **3.11.16**.
[Results and pairs](../observations/P3/README.md#observed-results).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| P3-a: TaskGroup membership is an opaque executable subgraph node | S/E: [grouping](../observations/P3/grouping-1.json) `static.top_level_children`, `group_membership`, `group_boundary`, `group_internal_roots_leaves`, `task_ids`; `execution.task_instances` has no `g` task | Q1, Q2, Q5, Q7 | **Correction of [F3](F3-opaque-subgraph/README.md#correction-p3).** Qualified member tasks remain enumerable; membership/boundary metadata is not compiled-child identity. A producer cannot justify an opaque-child marker merely by analogy. |
| P3-b: the root is a confirmed execution entry or identifies an external cause | S: same record, `static.roots=["before"]`, `leaves=["after"]`; [root discussion](../observations/P3/README.md#roots-as-a-structural-fact-not-confirmed-entry-semantics) | Q2 | **Reinforcement of [F2](README.md#f2--entrynodeids-conflates-a-graph-entry-with-a-node-that-lost-its-predecessor).** Only zero observed incoming edges is established. No orphan-by-gap case, sensor, external trigger or multi-root order was tested; this is not a new F2 reproduction. |
| P3-c: crossing the group boundary changes convergence for two successful members | S/E: same record, `static.dependencies`, `join_trigger_rule`, all five `execution.task_instances` succeed | Q4, Q5 | **Rejected hypothesis for this case.** P1's successful two-source outcome is retained across the group boundary. Do not generalize to missing/failed members or equate this rule with every AND/OR policy; convergence is routed to #27/F7. |
| P3-d: non-underscore source-visible membership/root accessors establish documented-public-only extraction | D: [Public-API gaps](../observations/P3/README.md#public-api-gaps) | Q1, Q5 | **Bounded limitation.** Distinguish API visibility from prose documentation coverage. This is an extractor support question, not a target-format defect. Nested groups and chained internal members remain untested. |
| P3-e: the saved source hash identifies the checked-in reproduction script | Saved-record audit: grouping records' `source_sha256`; [provenance limits](#provenance-limits) | Q1, Q5 | **Insufficient evidence.** The hash differs although literal observations match. Recover the source bytes with the recorded digest, or, only if a new reproduction is needed, rerun this one static/execution case twice as separately dated evidence. Do not rewrite the saved hash or upgrade P3 to a fresh F3 reproduction. |

## P4

Dagster **1.13.22**, CPython **3.11.16**.
[Comparison claims](../observations/P4/README.md#comparison-and-claim-record),
[paired results](../observations/P4/README.md#results-and-evidence-classes).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| P4-a: one reused definition needs only one set of local invocation IDs | S/E: [nested](../observations/P4/nested-1.json) `static.same_child_definition`, `invocations`, `membership`; `execution.step_success_keys` | Q2, Q5, Q7 | **Rejected hypothesis.** `left.seed` and `right.seed` are distinct invocations of reused definitions. Retain scope. The format allows IDs; no target collision was reproduced. Two runs do not prove stability after arbitrary edits. |
| P4-b: nested boundaries are completely opaque at the source | S: same record, `static.input_mappings`, `output_mappings`, `dependencies`, `api_coverage` | Q1, Q5 | **Reinforcement/correction of F3's source analogy.** Local mapping endpoints are visible and scoped paths are derived. This narrows a universal opacity claim, but does not reproduce depth-0 target loss or establish equivalence with P3's TaskGroup. |
| P4-c: documented public APIs suffice for complete enumeration | S/D: same `api_coverage`: mapping APIs observed public; invocation/dependency getters `source_visible_only`; [API attempts](../observations/P4/README.md#api-coverage-and-bounded-unsupported-inspection) | Q1, Q2, Q5 | **Insufficient evidence.** Before promising a public-only producer, identify a documented enumeration API for just the existing two aliases and dependencies and compare with the saved literals. If none is supported, explicitly restrict that producer's API contract. No format defect follows from the accessor gap. |
| P4-d: both child values reach the consumer | E: nested above, `execution.graph_output={left:20,right:30,sum:50}`, five successful op steps; no graph-alias success steps | Q4, Q5 | **Bounded limitation — positive execution.** Preserve boundary ports/values when investigating a producer; successful required inputs do not prove a universal barrier, failure policy or concurrency. Optional-input follow-up is P2-d, not a duplicate task. |
| P4-e: Dagster graph invocations and Airflow groups are equivalent | S/E: [comparison](../observations/P4/README.md#comparison-and-claim-record), P3-a and P4-a/d | Q5 | **Rejected as an established equivalence.** Definition reuse, data-port mappings and retrievable graph outputs differ from grouping task IDs. No new opaque-subgraph finding without a target mapping and contract argument. |

## P5

Airflow **2.10.5**, CPython **3.11.16**.
[All cardinality pairs](../observations/P5/README.md#observed-results).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| P5-a: a mapped-task definition supplies runtime cardinality/instance IDs | S/E: [zero](../observations/P5/mapped-0-1.json), [one](../observations/P5/mapped-1-1.json), [two](../observations/P5/mapped-2-1.json); identical `static.task_ids`, `dependencies`, `mapped_task_is_mapped_operator`; differing `execution.task_instances` | Q1, Q2, Q3, Q7 | **Rejected hypothesis.** One definition yields zero/one/two expanded instances. The current structural contract does not promise runtime cardinality. Keep definition IDs separate from `(task_id,map_index)` in an observer; no new format defect. |
| P5-b: zero mapping and two mapping have the same instance shape | E: same `task_instances`: zero retains `mapped,-1,skipped`; two has successful indexes 0 and 1 | Q3, Q7 | **Bounded limitation — native runtime distinction.** Do not erase the representative skipped row or merge indexed instances. These are paired local identities, not future-run stability or an execution-instance wire contract. |
| P5-c: the two aggregation trigger rules are generally equivalent under mapping | S/E: same `static.aggregate_trigger_rules`, `execution.task_instances`: both skip at zero and succeed at one/two | Q4 | **Insufficient evidence.** No mixed mapped success/skip/failure case exists. If rule discrimination changes a producer decision, use two mapped instances, one success and one deliberate skip, with the existing two aggregations. The agreement here is no new join finding; P1 already distinguishes rules on fixed sources. |
| P5-d: source-visible mapped type and observed map index are documented guarantees | D/E: [API gaps](../observations/P5/README.md#public-api-gaps) and zero record | Q1, Q7 | **Bounded limitation.** The concept page's empty-map skip statement does not specify index -1 or this readback API. Record the pinned observation without turning documentation coverage into a format defect. |

## P6

Dagster **1.13.22**, CPython **3.11.16**.
[Claims](../observations/P6/README.md#claim-record),
[all cardinality pairs](../observations/P6/README.md#observed-results).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| P6-a: dynamic output/collect declarations predict emitted cardinality | S/E: [zero](../observations/P6/dynamic-0-1.json), [one](../observations/P6/dynamic-1-1.json), [two](../observations/P6/dynamic-2-1.json); `static.output_is_dynamic`, `dependencies`; `execution.emitted_mapping_keys`, `mapped_step_keys` | Q1, Q2, Q3 | **Rejected hypothesis.** Static wiring agrees in all cases; runtime keys differ. As for P5-a, runtime cardinality is outside the inspected structural promise, so this is no new format defect. |
| P6-b: zero output means the mapped op ran and returned an empty container | E: zero above, `execution.step_success_keys=[collect,dynamic_source]`, `step_skipped_keys=[]`, `mapped_output.status=error`, `collect_output=[]` | Q3, Q4 | **Rejected hypothesis.** No mapped step exists in the recorded events; collect still succeeds. Preserve this difference from P5's skipped representative instance. Native zero-case behavior is not evidence either framework violates agent-topology. |
| P6-c: mapped identities are keys; flat collect preserves their association | E: two above, `execution.mapped_step_keys`, `mapped_output.value`, `collect_output` | Q4, Q7 | **Bounded limitation.** `mapped[k0]`/`mapped[k1]` and per-key output dictionaries retain association; the sorted collect list `[100,200]` does not encode keys. An observer must retain the keyed evidence separately. No universal identity guarantee or distinct target loss was demonstrated. |
| P6-d: flat map/collect results generalize through nested boundaries | S/E: [limitations](../observations/P6/README.md#normalization-and-limitations) | Q5, Q7 | **Insufficient evidence.** If nested dynamic extraction is needed, put this single map/collect chain inside one child invocation with two keys and compare scoped static ports and event identities. P4's non-dynamic nesting cannot substitute. Larger cardinalities/assets/other executors remain outside this cohort. |
| P6-e: the saved source hash identifies the checked-in reproduction script | Saved-record audit: dynamic records' `source_sha256`; [provenance limits](#provenance-limits) | Q1, Q3, Q7 | **Insufficient evidence.** The hash differs although all cardinality assertions match. Recover the recorded source bytes first; if unavailable and a new claim needs reproduction, rerun only its required cardinality/control pair twice with fresh provenance. No new finding is promoted from these records here. |

## C1

CrewAI **1.15.21**, CPython **3.11.16**; SDK tag commit
`4ed3dc929d0ee6b6981be452b2094c56fbbe7457`.
[All six cases and three evidence classes](../observations/C1/README.md#observed-results).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| C1-a: one selected router label means one listener invocation | S/C/E: [route-a static](../observations/C1/c1-router-route_a-static-1.json) `static`; [route-a execution](../observations/C1/c1-router-route_a-execution-1.json), [route-b execution](../observations/C1/c1-router-route_b-execution-1.json) `callable.callback_result`, `execution.log` | Q1, Q2, Q3 | **Reinforcement of F1.** One label reaches two listeners or none. Use [#28's completed argument](F1-fan-out-semantics/README.md#measured-distinctions), not another finding. |
| C1-b: AND/OR native distinction disappears on inspection, or missing join mode means no target semantics | S/E/D: [AND static](../observations/C1/c1-and-both-static-1.json), [OR static](../observations/C1/c1-or-both-static-1.json) `static.nodes`, `static.edges`; [contract audit](F7-or-firing-policy/README.md#contract-versions-and-authority) | Q1, Q2, Q4 | **Rejected hypothesis.** Literal condition types survive; target joins already mean implicit AND. [F7](F7-or-firing-policy/README.md) preserves the withdrawal and supplies the contract argument. This is consistent with F4's distinct join connectivity, not a new F4 reproduction. |
| C1-c: ordinary edges preserve the full observed OR firing policy | E/D: [or-both](../observations/C1/c1-or-both-execution-1.json) `execution.log=[a,route,join,b]`, `join_count=1`; [or-only_a](../observations/C1/c1-or-only_a-execution-1.json) `join_count=1`; [AND control](../observations/C1/c1-and-only_a-execution-1.json) `join_count=0` | Q4 | **New supported cohort finding, already published as [F7 by #27](F7-or-firing-policy/README.md#smallest-mapping-and-counterexample).** Correct C1's blanket edge-equivalence/no-loss claim: connectivity does not specify first-trigger/once-only suppression. F7 is bounded contract inspection, not a new scheduler run, universal CrewAI guarantee or upstream filing. |
| C1-d: version-pinned OR docs' two logger calls match the installed example | D/reported E: [docs mismatch section](../observations/C1/README.md#the-pinned-docs-own-or-example-does-not-reproduce-on-11521); not a separate paired JSON example | Q4 | **Bounded limitation — framework documentation mismatch.** Retain the reported one-call result separately from F7's paired six-case evidence. No target consequence follows from the docs error itself; do not promote it as another agent-topology defect. |
| C1-e: reachable structural accessors guarantee documented-public extraction; route labels are always enumerable | S/D: [API review](../observations/C1/README.md#what-public-definition-inspection-exposes-without-kickoff); paired static cases use explicit `emit=` | Q1, Q2, Q3 | **Bounded limitation.** `flow_definition()` and exported `build_flow_structure()` are source-visible but absent from the pinned guide. The no-emit/annotation visibility asymmetry is reported exploration, not a separately paired no-emit case. A producer must state its declared-label subset; missing inference is not a format defect. |
| C1-f: subclass behavior, single-trigger projection and first-run bookkeeping are target defects | D/reported exploration: [minimal input](../observations/C1/README.md#minimal-input), [side effect](../observations/C1/README.md#a-framework-level-side-effect-controlled-and-documented), [limitations](../observations/C1/README.md#normalization-and-limitations) | Q1, Q2, Q4 | **Bounded limitation.** Lost inherited methods affected fixture construction; bare-string/single-OR projection simplifies native structure; storage/telemetry settings concern reproduction. None proves distinct target information loss, and none has its own paired cohort JSON. |
| C1-g: chain OR behavior proves racing/cyclic/nested-condition policies | E/D: same [limitations](../observations/C1/README.md#normalization-and-limitations) | Q4 | **Insufficient evidence.** For a decision about OR rearming, use one listener and a router emitting the same signal twice, retaining invocation order/count. Racing cancellation instead needs two same-batch sibling triggers; do not infer it from the chain. Neither candidate blocks F7's bounded disposition. |

## S1

ASL specification **retrieved 2026-09-11**, no published dated revision;
CPython **3.14.7**, standard library only. **All records are static**;
semantics cited from documentation remain documentary.
[All pairs](../observations/S1/README.md#observed-results).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| S1-a: Choice order and Default are visible independently of selection | S/D: [choice](../observations/S1/choice-1.json) `scopes[0].choice_rules.CheckStatus`: ordered Approved/Rejected, separate Pending default | Q1, Q2, Q3 | **Reinforcement of F1 as a source-side control.** Source declarations are available; no expression was evaluated and no lossless target mapping was tested. [F1's current disposition](F1-fan-out-semantics/README.md#declarative-control-and-static-inspection-boundary) supersedes the historical no-divergence framing. |
| S1-b: Parallel/Map children are inspectable and repeated local names remain scoped | S: [parallel](../observations/S1/parallel-1.json) `scopes`, `parallel_branch_counts`; [map](../observations/S1/map-1.json) item-processor scope | Q1, Q2, Q5, Q7 | **Reinforcement/correction of F3's source analogy.** Nested JSON is a positive boundary control. No depth-0 topology was emitted; revision 1's compiled-child evidence requirement is not automatically satisfied by a TaskGroup, GraphDefinition or ASL state-type analogy. Not a new target-loss finding. |
| S1-c: Parallel's declared convergence demonstrates scheduling/failure behavior | S/D: parallel above, root `next_edges.RunBoth=Converge`, branch `terminal_states`; [comparison](../observations/S1/README.md#comparison-against-the-current-topology-contract) | Q3, Q4 | **Rejected as execution evidence.** All-branch convergence is documented meaning, not a measured run or failure/retry experiment. Use #27/F7 for the target join contract; ordinary adjacency alone is not a universal convergence explanation. |
| S1-d: MaxConcurrency 1 implies cardinality 1 or an ordinary invocation | S/D: map above, `scopes[0].map_config.ProcessItems`: `max_concurrency=1`, `array_length_known=false`, `mode=INLINE` | Q3, Q7 | **Rejected hypothesis.** A concurrency bound is separate from runtime array length and the item template. Like P5/P6, this does not violate a structural contract that promises no runtime count. |
| S1-e: local scoped references and StartAt establish authoritative validation or resolve F2 | S: choice/parallel/map `scopes[].start_at`, `json_parsed`, `probe_disclaimer`; [negative checks](../observations/S1/README.md#negative-checks) | Q1, Q2, Q5 | **Bounded limitation.** Explicit StartAt is a source declaration, distinct from P3's calculated roots, but there is no orphan-by-gap target reproduction. Local missing-target/cross-boundary rejection is not AWS validation or execution. |
| S1-f: callback-task syntax proves structural HITL placement | D only: [matrix Q6](../observations/S1/README.md#common-question-matrix-m1), no Task fixture | Q6 | **Insufficient evidence.** If placement affects a producer decision, add one `.waitForTaskToken` Task declaration and compare its documented callback semantics with a specific target before/after interrupt claim. A suffix alone does not validate that equivalence; no cloud run is needed to inspect the declaration. |

**Explicit correction to S1's historical comparison:** its statement that P3/P4
showed full boundary inspection through public APIs is too broad: P4-c retains
undocumented enumeration, and P3-a does not establish executable-subgraph
identity. Available ASL declarations do not themselves prove loss in a produced
topology document. The historical F1 claim is now bounded by #28/current revision
1, and convergence by #27/F7. Original prose and JSON remain preserved.

## T1

Temporal Python SDK **1.18.0**, source
`3fe7e422b008bcb8cd94e985f18ebec2de70e8e6`, CPython **3.11.16**.
[Paired observations](../observations/T1/README.md#observations) and
[source-review record](../observations/T1/source-review.json).

| Claim | Evidence and exact section | Q | Decision impact and disposition |
| --- | --- | --- | --- |
| T1-a: decorators, registration or Python signatures export invocation topology | S/D: [inspection](../observations/T1/inspection-1.json) `observed.workflows`, `activities`, `registration_parameter_names`, `bodies_entered=[]`; [bounded API search](../observations/T1/README.md#public-api-and-graphexport-search) | Q1, Q2 | **Rejected hypothesis for the inspected surface.** Equal run signatures do not distinguish linear from choice edges. Public authoring is not a public graph export; no static producer is certified. No target-format defect follows from unavailable source extraction. |
| T1-b: Temporal universally cannot support a static producer | D: same bounded search and [decision boundary](../observations/T1/README.md#decision-and-execution-boundary) | Q1, Q2, Q3 | **Rejected generalization.** Only this SDK/model/surface was searched. A restricted source/DSL analyzer remains possible; [F1](F1-fan-out-semantics/README.md#declarative-control-and-static-inspection-boundary) incorporates this limit. Do not use T1 to disqualify a core field or the whole framework. |
| T1-c: history export is a validated runtime observer | D: [history API review](../observations/T1/README.md#public-api-and-graphexport-search), no history events in the inspection record | Q2, Q3, Q7 | **Insufficient evidence.** Use the existing linear control plus choice inputs `a`/`b` with a disposable SDK test environment, then retain scheduled/completed activity identities and ordering plus workflow ID separately. No server was installed here; public history serialization only identifies a candidate path. |
| T1-d: Python names or Info field schemas establish Temporal invocation IDs and stability | S/D: inspection above, `observed.runtime_identity_field_names`, Python names/signatures; [Q7](../observations/T1/README.md#seven-question-matrix-answers) | Q7 | **Bounded limitation.** Authored type names differ from Python names; Info lists schema fields, not generated runtime values. Two imports prove repeatability only. An observer needs distinct workflow/run/activity identities. |
| T1-e: named signal/update handlers establish before/after interrupt placement | D only: [Q6 discussion](../observations/T1/README.md#seven-question-matrix-answers) | Q6 | **Insufficient evidence.** For a static-placement claim, first define one wait/handler workflow and a specific invocation anchor, then verify a supported structural relation; a runtime handler accessor alone cannot supply it. No HITL, child workflow or multi-source convergence was measured. |

## Shared exclusions and finding coverage

Q6 is **untested in P0–P6 and C1**, not an omitted finding. S1-f and T1-e retain
their documentary partial answers. Likewise untested production concurrency,
arbitrary nesting, larger cardinalities, alternative versions and universal ID
stability are bounded limits of these inputs, not implicit claims awaiting
promotion. No broader experiment is required merely to close a disposition.

| Existing finding | Cohort disposition coverage |
| --- | --- |
| F1 | P1-a/b, P2-a/c, C1-a, S1-a and T1-a/b feed #28's completed rewrite. |
| F2 | P3-b and S1-e distinguish calculated roots from declarations; neither adds a gap-orphan reproduction. |
| F3 | P3-a/d, P4-b/c/e and S1-b narrow grouping/boundary analogies. The beta.2 reproduction stays historical; no new cross-framework depth-0 mapping is claimed. |
| F4 | C1-b/F7 retains implicit AND and separate join identity. Native probe edges do not test an edges-only topology consumer; no new F4 reproduction. |
| F5 | No sentinel-role extraction/consumer comparison in the cohort. Names such as `first`, `begin` or `StartAt` do not prove framework sentinel ownership. No reinforcement or new finding. |
| F6 | Probes deliberately have no agent-topology package dependency and do not exercise CommonJS/ESM loading. No packaging evidence or new finding; historical/current reconciliation belongs to #30. |
| F7 | C1-c links the existing independently supported narrow OR-policy finding; C1-b preserves its withdrawn original hypothesis. No duplicate ID. |

## Verification

This is saved-record/contract review, not fresh framework execution. The audit
compares all cohort JSON run pairs byte-for-byte, checks their saved sections
against the probes' independent literal expectations without importing a
framework, and checks recorded source/lock/fixture hashes. T1 additionally uses
its independently authored `expected.json` and source-review record. C1's prose-only
explorations remain marked as such; they are not silently counted as paired data.

Local Markdown targets/anchors, group backlinks and claim coverage are checked;
original observation prose is preserved with additive disposition links and S1's
explicit correction. No gallery, transcript, probe source, lock or raw JSON is
changed. Only relevant documentation and evidence-integrity checks are needed;
no framework installation, renderer build or combined framework CI applies.

### Audit results

The 2026-09-12 review found **57 byte-identical pairs (114 records)**:
P0 4, P1 9, P2 6, P3 2, P4 2, P5 6, P6 6, C1 18, S1 3, T1 1.
All **85 run-1 measured sections** matched literal expectations read with
`ast.parse`/`ast.literal_eval`: `EXPECTED_STATIC`, `EXPECTED_CALLABLE`,
`EXPECTED_EXECUTION`, S1's `EXPECTED_FACTS`, or T1's `expected.json`.
Run 2 equality carries the same comparison to the paired records. This checks
agreement with saved assertions, not their historical authoring order or a fresh
run of the framework. C1's README explicitly describes empirical confirmation
before encoding its literal expectations.

All recorded dependency-lock and ASL fixture hashes matched the current files;
T1's three local source hashes matched, and its recorded SDK activity/workflow
hashes agreed with `source-review.json`. Other probe source hashes matched
except the two cases below. Their semantic assertions still matched. No
unsupported claim of complete source provenance follows from that agreement.

The document review accounts for every group's results/claim sections, API gaps,
identity limits and documentary-only claims in **47 unique claim rows**. All
**309 local targets/anchors** passed, including all ten observation backlinks;
`git diff --check` passed. All **115 raw JSON files** (including T1's source-review
record) match the cohort baseline; **22 historical SVG/transcript/JSON artifacts**
match the beta.2 baseline. All ten observation documents retain their full prior
text with additions only. A short
independent pair check, runnable without installing any framework, is:

```sh
python3 - <<'PY'
from pathlib import Path
groups = ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'C1', 'S1', 'T1']
counts = [4, 9, 6, 2, 2, 6, 6, 18, 3, 1]
for group, expected in zip(groups, counts):
    paths = sorted(Path('observations', group).glob('*-1.json'))
    if len(paths) != expected:
        raise RuntimeError(f'{group}: expected {expected} pairs, got {len(paths)}')
    for first in paths:
        second = first.with_name(first.name[:-6] + '2.json')
        if first.read_bytes() != second.read_bytes():
            raise RuntimeError(f'pair differs: {first}, {second}')
print('57 saved pairs match; no framework execution')
PY
```

### Provenance limits

| Claim | Recorded source SHA-256 | Checked-in source SHA-256 |
| --- | --- | --- |
| P3-e, `probes/airflow/grouping.py` | `3b27f1f95ae0a72f1394f9ab17ff0235ef349bd8231a21c76eec6e4527ed09af` | `44b87ea3107e9b2eaa76a37b836479fe2863d59243475569907b429a42352740` |
| P6-e, `probes/dagster/dynamic.py` | `c8d8ecb452d1a1471da068b845377af18fbe57ecee5761fab5d4b1d1fd7dd92f` | `5e2e011a5d060dc59104628dbbf072cb37d4513b4e6454d230f92510a57d5e91` |

The available committed history for each script contains only the checked-in
digest above. The cause of the mismatch is not established; do not assume it was
a comment-only change. These are pre-existing reproducibility limits, not failed
framework setup and not agent-topology defects. P3/P6's observation links now
reach this explicit qualification. The narrow source-recovery/reproduction
follow-ups in P3-e/P6-e are sufficient to disposition the limits without running
every framework or modifying historical evidence.
