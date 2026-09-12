**Title:** F1 evidence update: declared fan-out, selected targets and executed listeners

**Unposted draft for existing upstream work.** This evidence updates
[#94](https://github.com/agent-topology/agent-topology/issues/94),
[#95](https://github.com/agent-topology/agent-topology/issues/95),
[#96](https://github.com/agent-topology/agent-topology/issues/96),
[#97](https://github.com/agent-topology/agent-topology/issues/97), and
[#103](https://github.com/agent-topology/agent-topology/issues/103).
It does not request a duplicate F1 issue or a new core branch contract.
[Exact original text and beta.2 trial evidence](HISTORY.md) are preserved;
[the finding](README.md) provides the expanded evidence trail.

## Supported claim and current disposition

Declared possible destinations, selected labels/targets, listener multiplicity,
and actual execution are different facts. A consumer cannot infer one from the
other merely from edge kind, operator class, fixture name or return annotation.
The observations below support that boundary. Upstream's
[integrated F1 disposition](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/consumer/README.md#finding-disposition)
is **improved; selection remains unknown**, at fixed commit
`eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe` (main checked 2026-09-12).
This is current source, not a claim about released beta.2 or beta.3 qualification.

The [beta.2 producer reproduction](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/research/f1-f6-reproduction/README.md#disposition-table)
extracted identical graphs and structure hashes from single- and list-returning
LangGraph.js routers with identical declared destinations. Extraction did not
invoke either callback; this establishes a static distinction left unknown,
not runtime scheduling behavior.

## Completed branch evidence

| Pinned model | Static fact | Selection/emission and execution evidence |
| --- | --- | --- |
| [P1: Airflow 2.10.5](../../observations/P1/README.md#observed-results) | Same `BranchPythonOperator` and declared `a,b` destinations | Direct callback returns one target, two targets or none. `dag.test()` records one, both or neither succeeding. Operator class does not prove exclusivity. With only `a` successful, the same incoming edges give a skipped `all_success` join but a successful `none_failed_min_one_success` join. |
| [P2: Dagster 1.13.22](../../observations/P2/README.md#observed-results) | Same two optional outputs and dependencies | `execute_in_process()` events record zero/one/two emitted outputs and corresponding skipped/successful consumers; the ordinary required-output control completes both consumers in every case. Config is input, not measured emission. |
| [C1: CrewAI 1.15.21](../../observations/C1/README.md#observed-results) | Two listeners share `route_a`, with `route_a,route_b` declared via `emit=` | The callable selects one label. For `route_a`, kickoff logs `begin, route, listener_one, listener_two`; for `route_b`, neither listener runs. **One selected label can trigger two listeners.** |

Each linked observation includes paired saved records, reproduction and limits.
P1/P2 local execution does not measure wall-clock concurrency. C1's accessible
`flow_definition()` and exported `build_flow_structure()` expose native facts,
but neither appears in its pinned Flows guide; native exposure and documented
public API guarantees remain distinct. These probes are framework-native
observations, not topology producers or proof of a lossless target mapping.

[S1's ASL control](../../observations/S1/README.md#observed-results) preserves
ordered Choice rules and separate Default, Parallel branch scopes with documented
all-branch convergence, and Map's concurrency bound separately from runtime item
count. This is static/documentary evidence against the ASL spec retrieved
2026-09-11 (no dated revision published). No rule was evaluated or AWS service
called; local JSON/reference checks prove neither authoritative validation nor
execution or revision-1 producer conformance.

[T1](../../observations/T1/README.md#public-api-and-graphexport-search) found no
documented public definition-to-topology export in its reviewed Temporal Python
SDK **1.18.0** surface, source commit
`3fe7e422b008bcb8cd94e985f18ebec2de70e8e6`, for two decorated workflows and two
activities. It inspected definitions/signatures and SDK sources without entering
workflow/activity bodies, invoking callbacks, constructing a worker/server or
executing workflows. Source reasoning is separate from exported invocation
edges. Other SDKs, releases and application DSLs are unexamined; restricted
source analysis and history observation remain unvalidated candidates. This is
no universal Temporal exclusion or decision about core-field eligibility.

## Convergence disposition

[Testbed #27](https://github.com/agent-topology/agent-topology-testbed/issues/27) published
[F7](../F7-or-firing-policy/README.md): `joins[]` carries implicit AND/all-sources
semantics. F7 distinguishes beta.2's ADR/fixture evidence from later explicit
consuming guidance. No mode property does not mean no semantics, and a join
cannot establish its upstream divergence's selection policy.

The separate supported limitation is narrower: ordinary incoming edges preserve
C1 OR connectivity but do not establish first-trigger/once-only firing. In the
saved `or-both` run, `join` fires before `b` and never fires again after `b`;
`or-only_a` fires once too. [F7's counterexample](../F7-or-firing-policy/README.md#smallest-mapping-and-counterexample)
shows that the inspected contract does not supply the suppression/reset rule.
This is contract under-specification for those observations, not a universal
CrewAI promise or measured behavior of an upstream scheduler. F7 owns the OR
policy question; it does not revive the withdrawn convergence-asymmetry argument.

## Reconcile the proposed remedy

[Accepted ADR 0008](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md)
and its [schema](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/experimental/interpretation-v1.schema.json) define
graph-level `graphs[i]["x-topology-interpretation"]` revision `"1"`, with
per-node facts. Known branch `all-declared` requires at least two unconditional
ordinary direct declarations and complete scoped evidence excluding conditional,
dynamic or unresolved routing. It is not a promise of execution, success or
simultaneous scheduling. Inspected routers are `unknown` with
`selection-not-observable`; uninspected scopes use `scope-not-inspected`.
Absence means no assertion. Core validation alone does not validate these facts.

The former core `branches[]` and structure-level `x-topology-branch` trial using
`exclusive | concurrent | unknown` are **historical, superseded proposals**,
not aliases or current recommendations. Revision 1 contains no known
exclusive/concurrent value. [Real producer evidence](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/branch-evidence.md)
and [integrated consumers](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/consumer/README.md) now cover the
accepted experiment in Python and TypeScript LangGraph; two implementations
of one framework do not prove vendor neutrality. Core promotion requires a
separate ADR, independent evidence and an explicit migration/hash decision.

The [historical four-fixture trial](HISTORY.md) injected modes by fixture name;
its successful validation and unchanged hashes show extension acceptance/hash
exclusion, not producer knowledge. [The upstream correction](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/research/f1-f6-reproduction/README.md#f1-consumer-injection-is-not-extraction)
retains that limit. Equal structure hashes do not imply equal metadata or
interpretation; [ADR 0008](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md#compatibility-and-promotion)
requires comparing revision and canonical extension content for interpretation
caches. Hash equality does not automatically preserve qualification receipts.

The evidence supports retaining the accepted declaration/unknown distinction.
Any stronger selection claim needs a separately justified source and revision;
these completed probes do not authorize a schema change or upstream publication.
