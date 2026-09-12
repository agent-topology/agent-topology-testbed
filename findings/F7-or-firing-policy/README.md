# F7 — Unrepresented OR firing policy

**Disposition: supported, bounded to C1's once-only OR policy and the inspected
core contract.** Published locally for [#27](https://github.com/agent-topology/agent-topology-testbed/issues/27)
on 2026-09-12; not filed upstream. This is a contract inspection backed by saved
framework execution, not a producer round trip or a topology execution engine.

Ordinary incoming edges preserve the two source-to-target connections, but do
not communicate C1's observed rule: fire before the second source completes,
then do not fire again when it completes. Neither independent triggering nor
absence of an AND join establishes first-trigger/once-only behavior.

The original hypothesis, **“no join mode means joins have no AND/OR semantics,”
is withdrawn**. AND is implicit in the documented multi-source join meaning.
C1's subsequent blanket **“OR requires only ordinary edges, so no loss”**
conclusion is also withdrawn as exceeding its evidence. F7 keeps both rejected
claims discoverable; this ID is no longer available for reuse.

## Evidence and minimal input

Use only C1's existing four-node chain `a → route → b`, plus `join` listening
to `a,b`; `route` selects `go_b` or `skip_b`. These four cases distinguish
all-required convergence, early firing and suppression of a later trigger.
No additional framework run is needed. The three-node convergence fragment
below is sufficient for the mapping question; it is not a replacement runtime
input because `route` supplies the controlled omission of `b`.

| Case | Execution log (ordered, no deduplication) | Join count | Saved pair |
| --- | --- | --- | --- |
| AND, both | `a, route, b, join` | 1 | [1](../../observations/C1/c1-and-both-execution-1.json), [2](../../observations/C1/c1-and-both-execution-2.json) |
| AND, only a | `a, route` | 0 | [1](../../observations/C1/c1-and-only_a-execution-1.json), [2](../../observations/C1/c1-and-only_a-execution-2.json) |
| OR, both | `a, route, join, b` | 1 | [1](../../observations/C1/c1-or-both-execution-1.json), [2](../../observations/C1/c1-or-both-execution-2.json) |
| OR, only a | `a, route, join` | 1 | [1](../../observations/C1/c1-or-only_a-execution-1.json), [2](../../observations/C1/c1-or-only_a-execution-2.json) |

[C1's full record table](../../observations/C1/README.md#observed-results)
also links both static and callable runs for each case. Static records expose
literal `condition_type: AND/OR` and `trigger_methods: [a,b]`; callable records
show router return values only. Execution records alone establish invocation
order/count. C1 uses CrewAI **1.15.21**, source tag commit
`4ed3dc929d0ee6b6981be452b2094c56fbbe7457`, and CPython **3.11.16**.

Native exposure and documented-public guarantees remain separate:
`flow_definition()` is non-underscore and source-visible; the exported
`build_flow_structure()` retains the distinction. C1 records that neither
accessor is mentioned in its pinned Flows guide. Export status does not close
that documentation gap. Q4 support is a source-capability result, not proof
of target-format loss. The loss claim requires the contract comparison below.
The pinned guide's repeated-OR example disagrees with the saved once-only
execution; this finding relies on execution for those cases, not a universal
documented CrewAI promise. Cycles, rearming, races and nested conditions remain
outside the claim.

[S1 Parallel](../../observations/S1/README.md#comparison-against-the-current-topology-contract)
is supplementary static/documentary evidence for declared all-branch convergence.
It supplies neither an OR policy nor AWS execution evidence.

## Contract versions and authority

The audited file hashes and exact commits are in [audit.json](evidence/audit.json).
Package releases, topology version `0.1` and unreleased source are separate axes.

| Snapshot | What it establishes |
| --- | --- |
| Historical `v0.1.0-beta.2`, `cbd2f404a36834fb9ba318500b7832f03ba610da` | Schema distinguishes joins from edges. The contract delegates graph meanings to conformance fixtures; the multi-source fixture retains a single join. ADR 0003 explains that it waits for all sources, unlike separate edges. The contract also explicitly declines broader unobservable all/any semantics. The consuming guide has no join-helper section; the helper is not in published beta.2. |
| C1 pin `3715dd32a0efc3e7bd500d26d038774d6a37f4e6` | Same schema; consuming guide explicitly states implicit AND/all-sources-required semantics, and the Python helper retains AND join identity. This is later guidance, not evidence that beta.2 exported the helper. |
| Current upstream fetched 2026-09-12, `eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe` | Schema, consuming guide and Python helper are byte-identical to C1's pin. No new OR firing guarantee appears in those files. Experimental interpretation revision 1 has branch/subgraph/sentinel/entry facts, no convergence firing-policy fact. This is not a beta.3 release claim. |

Primary references:

- Historical [contract](https://github.com/agent-topology/agent-topology/blob/cbd2f404a36834fb9ba318500b7832f03ba610da/docs/0.1-contract.md#candidate-contract), [limitations](https://github.com/agent-topology/agent-topology/blob/cbd2f404a36834fb9ba318500b7832f03ba610da/docs/0.1-contract.md#known-limitations-and-excluded-consumers), [ADR 0003](https://github.com/agent-topology/agent-topology/blob/cbd2f404a36834fb9ba318500b7832f03ba610da/docs/decisions/0003-canonical-ordering-and-versioned-structure-hash.md), and [join fixture](https://github.com/agent-topology/agent-topology/blob/cbd2f404a36834fb9ba318500b7832f03ba610da/conformance/fixtures/multi-source-join/expected.json).
- C1 [schema](https://github.com/agent-topology/agent-topology/blob/3715dd32a0efc3e7bd500d26d038774d6a37f4e6/spec/agent-topology.schema.json), [consuming guide](https://github.com/agent-topology/agent-topology/blob/3715dd32a0efc3e7bd500d26d038774d6a37f4e6/docs/guides/consuming-documents.md#join-connections), and [helper](https://github.com/agent-topology/agent-topology/blob/3715dd32a0efc3e7bd500d26d038774d6a37f4e6/packages/python/spec/src/agent_topology/spec/_joins.py).
- Current [schema](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/agent-topology.schema.json), [consuming guide](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/guides/consuming-documents.md#join-connections), [helper](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/spec/src/agent_topology/spec/_joins.py), and [experimental schema](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/experimental/interpretation-v1.schema.json).

## Smallest mapping and counterexample

These are **authored consumer trial fragments**, not producer output, complete
topology documents, or proposed core semantics. Keep the same visible nodes
`a,b,join`; omit the shared router chain only from this convergence comparison.

AND maps to `joins: [{id: "wait", sources: ["a","b"], target: "join"}]`
with no duplicated ordinary incoming edges. It conveys that both sources are
required. The helper can derive drawing links with `joinId: "wait"`; it cannot
turn them into independent triggers. This supports the all-required distinction,
not a universal per-run count, reset or failure policy.

The proposed OR mapping is:

```json
{
  "edges": [
    {"id": "a-join", "source": "a", "target": "join", "kind": "direct"},
    {"id": "b-join", "source": "b", "target": "join", "kind": "direct"}
  ],
  "joins": []
}
```

On the already observed ordered arrivals `a,b`, compare two **hypothetical
consumer policies**, not two measured frameworks:

| Policy added by the consumer | After a | After b | Agreement with C1 OR-both |
| --- | --- | --- | --- |
| Fire for each incoming trigger | join count 1 | join count 2 | Fails once-only assertion |
| Fire for the first trigger and latch until reset | join count 1 | join count 1 | Matches these runs, but requires the extra latch/reset rule |

Both preserve the same endpoints and direct edge kinds. The inspected contract
does not select the second rule or encode its reset scope. Waiting for both
sources instead fails C1's early-firing and only-a assertions. Thus the ordinary
edge mapping is connectivity-preserving but does not preserve the measured OR
firing policy as a contract-backed consumer fact. This is under-specification
for that interpretation, not proof that an upstream scheduler executes twice.

An arbitrary node `type` string, label, or namespaced extension could carry a
producer convention, but none gives a common first-trigger/once-only meaning
in the inspected contract. Extensions make absolute “impossible to encode in
JSON” claims false. No extension is proposed or emitted here.

## Decision impact and remaining boundary

Reject both blanket conclusions above. A consumer may display AND convergence
and OR connectivity with these mappings, but must not infer C1's once-only OR
policy from ordinary edges. Preserve the policy separately or expose it as
unestablished when a consumer needs firing semantics. This evidence does not
require a schema change, certify a CrewAI producer, or gate a release.

[ISSUE.md](ISSUE.md) is a reviewable draft for upstream consideration, not a
published issue. Upstream owns whether firing policy belongs in its scope.
The minimal follow-up for a stronger lossless-mapping claim is an upstream
normative mapping selecting both early firing and suppression after `b`, with
its reset boundary, checked against these same four records. Until then that
stronger claim remains unresolved; no larger framework suite would settle a
missing contract rule. A new cyclic or racing run is warranted only if such a
rule expands the intended scope.

## Verification

Run from the testbed root with an upstream Git checkout containing all three
commits (no installation needed):

```sh
rtk proxy python3 -O findings/F7-or-firing-policy/verify.py /path/to/agent-topology
```

The audit checks 24 saved records / 12 byte-identical pairs, metadata, current
probe/lock SHA-256 against every record, all applicable original literal
assertions via AST reading without importing CrewAI, and the three pinned
contracts against the saved audit. It preserves event order and multiplicity.
`--write` deliberately regenerates the audit for review. Mismatches raise
`ValueError`, including under `-O`; success is not a fresh framework execution.
The reviewed probe assertions were confirmed empirically before encoding in
C1, as its provenance states; this audit does not recast them as blind predictions.

Historical beta.2 evidence at testbed baseline
`571e881e6d509b6e26ff8bf14b98e207d12e7ce9`, C1 JSON, probe source and lock are
unchanged. C1's prior prose is retained with an explicit correction link.
