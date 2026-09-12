# Testbed issue planning

Issue and milestone content is English. If ADRs are introduced, keep them Korean.
Use GitHub's native parent/sub-issue and blocked-by relationships, not labels
that encode workflow state. Every child has exactly one parent.

- **Epic**: a measurable outcome spanning coherent changes. Include scope,
  non-goals, success evidence, decisions, dependencies, and review points.
  Review the outcome explicitly before closing; closed child counts are not proof.
- **Feature**: one coherent, reviewable PR by default, directly under its epic.
  A bounded observation can be the outcome; application code is not required.
- **Task**: add only for a distinct implementation or verification boundary that
  needs separate delivery. Do not pre-create speculative Tasks or require an
  extra Feature wrapper for existing approved leaf issues (including P0/#2).

Leaf PRs close leaf issues, not their epic. Keep at most two issues in progress.
Before starting a wave, review prior evidence, refine upcoming issues, and record
why scope changed. New questions become follow-up candidates rather than silently
expanding the current issue. Contradicted claims and bounded unknowns may finish a
measurement issue; broken setup cannot.

## Leaf issue contents

State the change and measured question separately from the minimal input. Include
acceptance criteria, verification commands, limitations/non-goals, dependencies,
parent, baseline, and version/source references. Use only enough nodes and
execution input to answer that question. Write independent expected observations
before extraction logic. Follow [evidence conventions](evidence.md): two runs,
semantic comparison, explicit nonzero failures, and separately pinned environments.

## Probe closure disposition

Measurement completion and finding reconciliation are distinct. Before treating a
completed probe as reconciled, include this lightweight checklist in its issue
and fill it in the probe PR when the disposition fits that PR:

- [ ] **Measured claims:** list the material claims, evidence classes, pinned
  versions and limits; distinguish the question from the minimal input.
- [ ] **Finding disposition:** link an existing/new finding, correction, rejected
  hypothesis, or explicit non-finding with its reason. Not every probe yields a
  finding; use the [promotion criteria](evidence.md#promotion-from-observation-to-finding).
- [ ] **Evidence and index:** link saved records/reproduction and the findings
  index or an indexed disposition ledger, with a backlink from the observation.
- [ ] **Decision impact:** state what the evidence changes or leaves unchanged
  for a producer, consumer or upstream decision; do not imply upstream approval.
- [ ] **Unresolved evidence:** state what is missing and the smallest follow-up
  that could change the decision, or explicitly say none is needed for this
  bounded question. Keep untested scope distinct from broken setup.

If extraction needs a distinct delivery boundary, link a bounded Task **before
closing the probe issue**. That Task must name the deliverable (claim-level
finding/non-finding dispositions plus evidence/index links), minimal existing
inputs, acceptance/verification, parent and actual dependency on the probe's
records. Use the native dependency relationship for that input; do not add
unrelated probe blockers. The closed measurement remains **reconciliation
pending** until the linked Task publishes its disposition. A promise to “update
#9 later” without that deliverable and dependency is insufficient.

A bounded unresolved verdict can complete reconciliation when it states the
missing evidence and minimal follow-up. Follow-up candidates outside the measured
question need not become scheduled Tasks. A failed setup still cannot count as
an answered measurement. Keep at most two issues/Tasks in progress; this checklist
is a review practice, not automation, a new label, heavyweight CI or a release gate.

[P7/#9](https://github.com/agent-topology/agent-topology-testbed/issues/9) performs
final integrated review of accumulated dispositions, cross-framework limits and
decision impact. It is not the sole place discoveries become visible. Publish
each increment when ready without waiting for unrelated framework probes.
See the [three worked dispositions](evidence.md#three-closure-examples).

### Completed-cohort backfill and adoption

Do not reopen closed probes to enforce the new practice retroactively. The
completed P0–P6/C1/S1/T1 cohort is covered by the linked extraction work:
[#27 convergence](https://github.com/agent-topology/agent-topology-testbed/issues/27),
[#28 F1 correction](https://github.com/agent-topology/agent-topology-testbed/issues/28),
[#29 claim triage](https://github.com/agent-topology/agent-topology-testbed/issues/29),
and [#30 index/status reconciliation](https://github.com/agent-topology/agent-topology-testbed/issues/30).
Their [disposition ledger](../findings/completed-cohort-dispositions.md) and
[upstream status review](../findings/upstream-status.md) are published local
outputs, not open blockers for Prefect or AutoGen.

At #31 implementation on 2026-09-12, #16 Prefect and #17 AutoGen had already
closed. Their issue bodies receive the checklist as a retrospective reconciliation
addendum; their experiment checkboxes, scope, closed state and sole #12 dependency
remain unchanged. Unchecked disposition items do not retroactively reopen either
measurement or certify reconciliation. P8/A1 disposition delivery is a separate
increment from the frozen cohort; these backfill links do not claim to cover it.

## Approved framework investigation

[Epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1)
defines these evidence reviews:

1. P0–P2: setup and branch counterexamples.
2. P3–P4: grouping, nested boundaries, roots, convergence.
3. P5–P7: dynamic expansion and cross-framework reconciliation.

Dependencies: P0 → P1 → P3 → P5; P0 → P2 → P4 → P6. P7 accumulates
evidence immediately and completes after P1–P6. Do not add a release milestone,
combined heavy-framework CI, upstream publication, or local workflow automation
as a side effect of this investigation. Upstream owns contract decisions.

## Expanded investigation priority (M1, C1, S1, and boundary probes)

The [common question matrix](../probes/README.md#common-question-matrix-m1)
(#12) backfills existing evidence and defines the seven question IDs every
new probe answers. Priority after #12 lands: CrewAI (#13) → ASL (#14), then
the remaining reconciliation work (P7/#9, which accumulates from P1–P6 and
completes last) and the three boundary probes (#15 Temporal, #16 Prefect,
#17 AutoGen).

Priority is not a blocked-by relationship: the P0→P1→P3→P5 and P0→P2→P4→P6
chains above are unchanged, #14 does not depend on #13, and #15/#16/#17 do not
depend on one another. Completed #2/#3 evidence stays as recorded; the
expanded scope does not reopen it. Keep at most two issues in progress.
