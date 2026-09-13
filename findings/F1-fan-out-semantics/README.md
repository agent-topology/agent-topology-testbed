# F1 — Declared fan-out does not establish selection or execution

**Disposition: supported, bounded; upstream interpretation improved.** The beta.2
consumer trial is historical. Current source provides experimental declaration
facts, while router selection remains unknown. This rewrite for
[testbed #28](https://github.com/agent-topology/agent-topology-testbed/issues/28) uses completed observations and upstream commit
`848b179aee32789a6f8b0ad4552a3a1262a05d55` (beta.3 source checked 2026-09-12).
[X1 now observes](../../observations/X1/README.md#f1--branch-interpretation) the
bounded declaration facts in registry beta.3; selection remains unknown.
See the [upstream integrated disposition](https://github.com/agent-topology/agent-topology/blob/848b179aee32789a6f8b0ad4552a3a1262a05d55/conformance/consumer/README.md#finding-disposition).
[ISSUE.md](ISSUE.md) is an unposted evidence draft for existing upstream work.
[Exact historical text and beta.2 evidence](HISTORY.md) remain available.

## The supported argument

A declared set of possible destinations does not establish the targets selected
for an input, how many listeners share a selected label, or which work actually
executes. P1, P2 and C1 measure those separately below. A consumer should preserve
that uncertainty instead of deriving an exclusive or concurrent execution mode
from edge kinds, operator classes, fixture names or return annotations. This is
also the rule in [ADR 0008](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md#branch-destinations-selection-and-scheduling).

The upstream [beta.2 reproduction](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/research/f1-f6-reproduction/README.md#disposition-table)
compares real LangGraph.js extraction from single- and list-returning routers
with identical declared destinations: the graphs and structure hashes match.
It does not invoke those routers. That is producer extraction evidence of an
unresolved static distinction, not a measurement of their scheduling.

## Measured distinctions

### Consumer impact: Cordboard's proposed R3 rule

[The R3 observation](../../observations/cordboard-r3/README.md) adds eight fresh
Python beta.2 producer records with static interrupts on both declared targets.
Single- and list-returning conditional routers yield identical graphs and hashes;
separate direct callback evaluations return `"a"` and `["a", "b"]`. A literal
model of Cordboard ADR-0007 Action 4 rejects the direct-interrupt control and
matches neither conditional case. The no-interrupt direct control also does not
match. Explicit override retains the positive match while changing its decision.

This makes F1 relevant to a concrete registration policy: the structural predicate
does not establish the execution fact needed by its rationale. Cordboard's catalog
rule is planned at the inspected pin, not an implementation exercised here.
No framework execution, concurrency, checkpoint collision or resume failure was
measured; **not-rejected is not safe**. The ADR's cited #6626 concerns dynamic
tool interrupts, a different scope from these static node interrupts, and was
closed when checked. Neither permanent data loss nor a required core branch
field follows. The [reconciliation](../consumer-reconciliation.md) retains AT-3's
consumer need without reviving superseded remedies or duplicating F1.

### Framework observations

| Evidence | Declaration | Selection or emission | Actual execution and boundary |
| --- | --- | --- | --- |
| [P1, Airflow 2.10.5](../../observations/P1/README.md#observed-results) | Same router downstream set `a,b` and join trigger rules in all cases | Direct callback evaluation returns `a`, `[a,b]`, or `None` | `dag.test()` shows one, both, or neither target succeeds; the two joins differ on the single-target case. No concurrency measurement. |
| [P2, Dagster 1.13.22](../../observations/P2/README.md#observed-results) | Same two optional output definitions and dependencies | Execution events record zero, one or two emitted outputs; config alone is input, not observed output | Consumers of missing outputs skip; the required-output control completes both consumers in every case. In-process execution does not prove concurrency. |
| [C1, CrewAI 1.15.21](../../observations/C1/README.md#observed-results) | Two listeners share `route_a`; `emit=` declares `route_a,route_b` | Direct callable returns one label in either case | `kickoff()` logs both listeners for `route_a`, neither for `route_b`. One selected label is not one executed listener. |

### Correction (P1)

The historical operator-class inference is withdrawn in the active argument:
[P1's multiple-selection case](../../observations/P1/README.md#the-multiple-selection-counterexample)
returns `["a", "b"]` from a `BranchPythonOperator` callback and both task
instances succeed. The class identifies a branching mechanism, not exactly-one
selection. Even downstream eligibility is separate: with only `a` successful,
`all_success` skips while `none_failed_min_one_success` succeeds on the same
incoming edges. This heading retains existing correction links; it is not an
appendix needed to repair the main claim.

C1's [one-label/two-listener record](../../observations/C1/c1-router-route_a-execution-1.json)
contains `begin, route, listener_one, listener_two`; its
[paired run](../../observations/C1/c1-router-route_a-execution-2.json) agrees.
Thus counting selected labels cannot substitute for counting target invocations.
C1's non-underscore `flow_definition()` and exported `build_flow_structure()`
expose native structure, but neither is documented in C1's pinned Flows guide;
[API exposure](../../observations/C1/README.md#what-public-definition-inspection-exposes-without-kickoff)
does not by itself certify a supported public extractor or target-format mapping.

## Declarative control and static-inspection boundary

[S1](../../observations/S1/README.md#observed-results) parses ASL declarations:
`Choice` retains ordered targets and a separate `Default`; `Parallel` retains
two branch scopes and documented all-branch convergence; `Map` retains
`MaxConcurrency: 1` separately from unknown input-array length. These source
facts show that declared control meaning can be available. S1 evaluated no
Choice expression, called no AWS service and produced no topology document.
Its source is the ASL specification retrieved 2026-09-11, without a published
dated revision; its local checks are neither authoritative AWS validation nor
execution. It does not validate a lossless mapping into revision 1.

[T1](../../observations/T1/README.md#public-api-and-graphexport-search) inspected
Temporal Python SDK **1.18.0**, source commit
`3fe7e422b008bcb8cd94e985f18ebec2de70e8e6`, for two decorated workflows and two
activities. No documented public definition-to-topology export was found in
that reviewed SDK/model/API surface. Python names and signatures are not
invocation edges; source reasoning about workflow bodies is a separate mechanism.
There was no callable evaluation, worker, server or workflow execution.
Other SDKs, releases and application DSLs are unexamined. A restricted source
analyzer or execution-history observer remains an unvalidated candidate, so T1
does not justify excluding Temporal universally or deciding core eligibility.

## Convergence has its own contract

The old argument that convergence can simply be inferred from edges is withdrawn.
[F7, the disposition of #27](../F7-or-firing-policy/README.md#contract-versions-and-authority),
distinguishes historical beta.2 ADR/fixture meaning from later explicit consuming
guidance: `joins[]` has implicit AND semantics, requiring all sources. The absence
of a mode property does not remove that meaning. A join does not establish the
selection policy of the divergence that feeds it.

F7 supports a different, bounded limitation: ordinary edges preserve C1 OR
connectivity but do not communicate its observed first-trigger/once-only policy.
For `or-both`, `join` fires before `b` and does not fire again after `b`;
`or-only_a` also fires once. The inspected contract supplies no suppression/reset
rule selecting that interpretation. See [the saved records and mapping counterexample](../F7-or-firing-policy/README.md#smallest-mapping-and-counterexample)
and [testbed #27](https://github.com/agent-topology/agent-topology-testbed/issues/27). This is not a claim that an upstream scheduler
executes twice, a universal CrewAI guarantee, or a reason to invent join semantics.

## Current upstream decision, not the historical proposed shape

At the fixed upstream commit above, [ADR 0008](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md)
and the [separate schema](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/experimental/interpretation-v1.schema.json)
define graph-level `graphs[i]["x-topology-interpretation"]`, revision `"1"`,
with per-node branch facts. Known `all-declared` requires at least two ordinary
unconditional direct declarations, complete evidence at that scope, and no
conditional/dynamic/unresolved routing evidence. It promises neither simultaneous
scheduling nor success nor actual execution. Inspected conditional routers remain
`unknown` with `selection-not-observable`; uninspected scope uses
`scope-not-inspected`. Absence means no assertion.

The historical core `branches[]` proposal and structure-level `x-topology-branch`
with `exclusive | concurrent | unknown` are **superseded proposals**, not aliases
or current recommendations. Revision 1 has no known exclusive/concurrent value.
Core promotion requires a separate ADR and independent producer/consumer evidence;
these local framework-native probes emit no topology documents and do not meet
that requirement by themselves. See [compatibility and promotion](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md#compatibility-and-promotion).

Existing upstream work is [#94](https://github.com/agent-topology/agent-topology/issues/94)
(interpretation epic), [#95](https://github.com/agent-topology/agent-topology/issues/95)
(reproduction), [#96](https://github.com/agent-topology/agent-topology/issues/96)
(contract), [#97](https://github.com/agent-topology/agent-topology/issues/97)
(branch producers), and [#103](https://github.com/agent-topology/agent-topology/issues/103)
(integrated consumers). The [branch evidence](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/branch-evidence.md)
and [integration record](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/consumer/README.md) document real Python
and TypeScript LangGraph producer extraction; F1 is improved, selection remains
unknown. This is current-source evidence, not released beta.2 behavior or beta.3
qualification, and two LangGraph implementations do not prove vendor neutrality.

## What the historical trial actually measured

The [frozen trial](HISTORY.md) injected fixture-name-selected modes and rendered
core/extension views; all four reported cases validated and retained their
structure hashes. It demonstrates a consumer presentation experiment and hash
exclusion, not correct producer inference. The upstream [reproduction correction](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/research/f1-f6-reproduction/README.md#f1-consumer-injection-is-not-extraction)
independently confirms extension acceptance/hash exclusion without upgrading
those four original reports into new executions.

Equal structure hashes do not establish equal extension metadata or interpretation.
[ADR 0008's compatibility rule](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0008-experimental-consumer-interpretation.md#compatibility-and-promotion)
requires comparing extension revision and canonical content as well as core
identity when caching interpretation. Core validation is separate from extension
validation and producer truth. Unchanged hashes do not preserve qualification
receipts automatically or authorize deploying a changed producer.

## Rewrite verification

D2 review on 2026-09-12 checked material claims against the linked observations,
F7 disposition and fixed upstream sources. Reference checks passed for 39 local
links/anchors and 25 distinct GitHub references/anchors across the active pair,
history page and findings index. All 36 historical F1 trial/gallery/transcript
artifacts compared byte-identically with baseline `571e881`; all 37 saved
P1/P2/C1/S1/T1 record pairs compared byte-identically. These comparisons inspect
existing evidence, not fresh framework execution or a new contract audit.

A search of both active documents for `exclusive`, `concurrent`, `Temporal`,
`convergence`, `hash`, `receipt`, `branches[]` and `x-topology-branch` confirmed
that superseded claims appear only as bounded distinctions or explicit historical
corrections. `git diff --check` passed. Documentation/reference checks suffice
for this rewrite; no framework installation, renderer rebuild or probe rerun was
needed.
