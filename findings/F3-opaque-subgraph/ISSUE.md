> **Historical unposted beta.2 draft; superseded proposal.** Existing upstream
> [#98](https://github.com/agent-topology/agent-topology/issues/98) addresses F3;
> use the [current disposition and corrections](README.md) and
> [upstream status review](../upstream-status.md#f3). The original text below is
> preserved, including its unsupported TaskGroup analogy and receipt claim.
> Equal structure hashes do not establish equal metadata or preserve release
> qualification receipts. This draft is not ready to post as a current proposal.

**Title:** 0.1: an opaque subgraph is indistinguishable from an ordinary node

---

Consumer evidence from building a renderer against
`@agent-topology/spec@0.1.0-beta.2`. Reproductions and rendered output:
[agent-topology-testbed F3](https://github.com/agent-topology/agent-topology-testbed/tree/main/findings/F3-opaque-subgraph).

## What a consumer cannot do

Tell that a node contains a nested graph, at the default `depth: 0`.

`node.subgraphId` must reference a graph present in `graphs[]`
(`_validation.py:89`). At `depth: 0` there is no child graph, so the field cannot
be set. The `nested` node in the `nested-subgraph` fixture carries no marker:

```json
"nodes": [{ "id": "__end__" }, { "id": "__start__" }, { "id": "nested" }]
```

Rendered, `nested-subgraph` is the same shape as `linear-flow`. Nothing
distinguishes a node hiding a whole graph from a node that does not.

## Why it matters

The affordance this removes is the one a consumer most wants to offer: *"there is
more inside this node — re-derive with `depth=1` to see it."*

It also interacts with the expansion limit already recorded in the README. A reader
cannot tell there is something there to be careful about, so the documented caution
has nothing to attach to.

## Proposed shape

A marker independent of whether the child graph is present:

```json
{ "id": "nested", "hasSubgraph": true }
```

or a reserved value of the existing `node.type`. It composes with `subgraphId`
rather than replacing it — `hasSubgraph` says something is inside, `subgraphId`
says where to find it once expanded.

## Against the core field test

Airflow `TaskGroup` is discoverable as a group whether or not a producer descends
into it. Reading a DAG with no scheduler, webserver, or metadata database:

```
task groups: ['nested']
```

Script: `probes/airflow/airflow_probe.py`.

## Cost

`node` already accepts `x-*`, and node extensions sit outside the hash projection
(`_NODE_HASH_FIELDS`, `_canonical.py:14`), so this can be trialled as
`x-topology-opaque-subgraph` in a producer without moving any published fixture
hash or qualification receipt.
