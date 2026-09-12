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
