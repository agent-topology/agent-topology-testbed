# P7: final comparison and evidence handoff

For [#9](https://github.com/agent-topology/agent-topology-testbed/issues/9),
under [epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1).
The deliverable is the [cross-framework reconciliation](../../findings/cross-framework-reconciliation.md),
indexed from [findings](../../findings/README.md) and the
[seven-question matrix](../../probes/README.md#answer-matrix).

## Question and minimal input

Which measured interpretation claims survive, fail, or remain unresolved across
all eight programming-model rows, and what do they change for upstream decisions?

Input is existing saved evidence, not new executable graphs: the 47-claim
P0–P6/C1/S1/T1 ledger, P8/A1 records and literal assertions, F1/F3 historical
corrections, F7's contract comparison, #27–#31 outputs, and current upstream
issue/ADR/consumer decisions. Testbed input commit is
`c528746b7826e1507a3c9732e54b4a48efe8cf89`. Historical beta.2 remains at
`571e881e6d509b6e26ff8bf14b98e207d12e7ce9`.

The [review snapshot](review-inputs.json) records GitHub check time, all input
issue states/body digests, upstream HEAD and reviewed document hashes. Upstream
HEAD was still `eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`. Issue bodies and
comments were read; unchecked boxes on closed issues were not treated as proof
of failure or completion. The delivered files and actual evidence were reviewed.
The snapshot is metadata provenance, not an archive of every issue body.

## Evidence class and result

**Saved-record and documentary/contract review; no new framework execution.**
The [synthesis](../../findings/cross-framework-reconciliation.md) retains separate
static, callable and execution classes for its inputs. P8 visualization, T1
history export, ASL service semantics and A1 HITL remain documentary candidates.

All 47 original claim IDs have an explicit verdict crosswalk; 15 additional
P8/A1 claims have finding/non-finding reasons, decision impact and bounded
follow-ups. All 56 matrix cells link to scoped answers or explicit untested
limitations. F7 is the distinct existing OR-policy finding; no new ID is created.
The local epic assessment is satisfied with explicit limits and is ready for
review, not an automatic closure or release qualification.

## Verification and reproduction

Run the bounded saved-input audit from the repository root:

```sh
rtk proxy python3 -O observations/P7/verify.py
rtk git diff --check
```

[verify.py](verify.py) uses only the standard library and Git. It invokes the
existing Prefect saved-record verifier, whose imported module has no top-level
framework import or execution. It does not invoke AutoGen's original verifier,
which reconstructs SDK definitions; instead it compares the saved static record
and literal participant/edge/root/message expectations without importing AutoGen.
This is deliberately a saved-evidence audit, not an independent SDK rerun.

The [saved audit result](audit.json) records:

- 57 byte-identical cohort pairs and 85 run-1 measured sections matching literal
  expectations read by AST, plus source/lock/ASL fixture hashes.
- P8's saved pair checked against native identities, input edges, invocation
  counts, lifecycle states/order, literal expectations and source/lock hashes.
- Four A1 cases compared across two runs, with 12 unique message UUIDs per run,
  disjoint between runs. Only message IDs and timestamps are excluded from
  equality; order, counts, content, stops and complete static configuration stay.
- Coverage of 47 existing plus 15 later claims and 56 linked matrix cells.
- 147 pre-existing JSON/SVG/text inputs and 21 beta.2 JSON/SVG/text artifacts
  byte-identical to their respective input commits, including the historical
  Airflow transcript. This count follows the script's explicit suffix/path set,
  not all repository files or a reuse of an earlier audit's differently scoped count.

`--write` regenerates only this audit summary for review; it never edits saved
framework records. Assertions raise exceptions and exit nonzero under `-O`.
The audit establishes agreement with saved expectations, not their historical
authoring order. C1 recorded empirical confirmation before encoding literals.
P8/A1 fixture corrections and repaired setup incidents remain in their READMEs.

Authoring verification passed for **686 local Markdown paths/anchors** and
**77 GitHub project endpoints**, including observation/index backlinks. Three
deliberate A1 corruptions (edge removal, message reordering and duplicate UUID)
were rejected under optimized Python without modifying saved records.
Upstream status remains
time-bound: repeat `gh issue view NUMBER --repo agent-topology/agent-topology`
and `gh api repos/agent-topology/agent-topology/commits/HEAD` before a later
handoff; retrieve the ADR and consumer README at that recorded SHA. Do not
replace the snapshot with current state without recording a new review.

## Limitations and disposition

P3 and P6 retain mismatched recorded source hashes. Literal expectations match,
but that is not proof of the original producing bytes; the audit reports these
as **unresolved**, never rewrites them. Recover those bytes first, or produce a
separately dated targeted case/control pair if a stronger claim needs it. This
review promotes no new finding from that uncertainty and requires no full rerun.

The [epic checklist disposition](../../findings/cross-framework-reconciliation.md#delegated-outputs-and-epic-outcome-review)
explains why bounded unresolved questions can finish this investigation, while
failed setup cannot. No unresolved environment failure is counted as a semantic
pass. Static extraction candidates remain conditional on their version/model/API
surface and independent producer-to-consumer evidence. No AWS execution,
universal identity guarantee, vendor-neutrality proof or beta.3 qualification is
claimed. No upstream publication, GitHub issue closure or contract change occurs.
