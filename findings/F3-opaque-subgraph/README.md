# F3 — An opaque subgraph is indistinguishable from an ordinary node

> **Current disposition (2026-09-12): improved in upstream source `eb0e2d8`.**
> [Dedicated #98 / merged #111 and consumer evidence](../upstream-status.md#f3)
> provide experimental `opaque-child` facts without dangling `subgraphId`.
> The historical core-marker proposal below is superseded by that experiment.
> “Nothing of any kind” is too broad: framework metadata may differ without a
> child-presence contract. The gallery comparison is qualitative, not an equal
> node-count control; upstream's minimal comparison supplies that control.
> The beta.2 report below and its P3 correction are preserved; P3 does not prove
> opaque-child equivalence. See also [P4](../completed-cohort-dispositions.md#p4)
> and [S1](../completed-cohort-dispositions.md#s1). This is no published fix claim.

**Status: reproduced.** Observed against `@agent-topology/spec@0.1.0-beta.2`.
Upstream issue body in [ISSUE.md](ISSUE.md).

## The claim

At the default `depth: 0`, nothing in a document marks a node as containing a
nested graph. A consumer cannot tell a node that hides a whole graph from a node
that does not.

## Reproduction

`node.subgraphId` must reference a graph present in `graphs[]`:

```
packages/python/spec/src/agent_topology/spec/_validation.py:89
    subgraph_id = node.get("subgraphId")
    if subgraph_id is not None and subgraph_id not in graph_by_id:
        ... unknown graph id
```

At `depth: 0` there is no child graph in `graphs[]`, so the field cannot be set.
The `nested` node in the `nested-subgraph` fixture therefore carries no marker of
any kind:

```json
"nodes": [{ "id": "__end__" }, { "id": "__start__" }, { "id": "nested" }]
```

Rendered, `evidence/nested-subgraph.svg` is the same shape as
`evidence/linear-flow.svg`. Nothing distinguishes them.

## Why it matters

The affordance this removes is the one a consumer most wants to offer: telling the
reader *"there is more inside this node — re-derive with `depth=1` to see it."*

Today no consumer can offer it, and a reader has no way to know the document is
hiding a graph. That interacts badly with the known limit already recorded about
expansion being unreliable past two levels: a reader cannot even tell there is
something there to be careful about.

## Cross-framework check

`probes/airflow/` shows the same concept exists elsewhere and is visible without
expanding it (`evidence/airflow-probe.txt`):

```
task groups: ['nested']
```

An Airflow `TaskGroup` is discoverable as a group whether or not a producer
descends into it. The marker is emittable there too.

## Suggestion

A core marker independent of whether the child is present — a boolean such as
`node.hasSubgraph: true`, or a reserved `node.type` value. It composes with the
existing `subgraphId` rather than replacing it: `hasSubgraph` says something is
inside, `subgraphId` says where to find it once expanded.

## Cost

`node` already accepts `x-*`, and node-level extensions sit outside the hash
projection (`_NODE_HASH_FIELDS`), so this can be trialled as
`x-topology-opaque-subgraph` without moving any published hash — the same route
F1 took.

## Correction (P3)

The "Cross-framework check" above prints `task groups: ['nested']` and leaves
it there, as evidence that the *concept* of a node hiding more structure exists
in Airflow too. [P3](../../observations/P3/README.md) (issue
[#5](https://github.com/agent-topology/agent-topology-testbed/issues/5))
measured what a `TaskGroup` actually exposes, and the concept is narrower than
the cross-framework check implies.

**What grouping proves.** A `TaskGroup`'s membership, its qualified task IDs,
and its own boundary edges (`upstream_task_ids`/`downstream_task_ids`) are all
discoverable through public attributes without executing anything or expanding
a black box — confirming, with a direct measurement rather than a one-line
print, that Airflow does not need a `depth` parameter to tell a consumer a
group exists and what touches it. Every member task keeps its own identity,
its own qualified ID, and its own dependency edges throughout; nothing about
crossing the boundary changed scheduling behavior in P3's execution case, and a
two-source convergence downstream of the group ran under the same trigger-rule
semantics P1 already established for two ungrouped sibling sources.

**What is still missing for subgraph equivalence.** F3's claim is about a
single node that can hide an entire graph behind `subgraphId`, discoverable
only once a consumer re-derives at a deeper `depth`. A `TaskGroup` is not that:
it is not one node — it is a label attached to a set of already-enumerable
tasks and edges, with no boundary node of its own that could carry a
`hasSubgraph` marker, fail as a unit, or gate what a consumer sees by default.
P3 never had to "expand" anything to see `g_a`/`g_b`; they were always present
in `dag.task_ids`, just with a `group_id` prefix. So the print in this finding's
"Cross-framework check" is accurate as far as it goes — Airflow does expose
*something* here — but it does not show Airflow has an opaque-subgraph node in
F3's sense, and no claim of that equivalence should be drawn from it.
`probes/airflow/airflow_probe.py` and its example DAG are unchanged by this
correction; their `task groups: ['nested']` line remains a true but narrower
fact than a reader might infer from sitting next to F3's claim.
