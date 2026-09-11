# F3 — An opaque subgraph is indistinguishable from an ordinary node

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
