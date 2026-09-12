**Title:** 0.1: a fan-out cannot be read as exclusive or concurrent

---

Consumer evidence from building a renderer against
`@agent-topology/spec@0.1.0-beta.2`, using `conformance/fixtures/*/expected.json`
as the corpus. Reproductions and rendered output:
[agent-topology-testbed F1](https://github.com/agent-topology/agent-topology-testbed/tree/main/findings/F1-fan-out-semantics).

## What a consumer cannot do

Determine whether the several destinations of a branching node are alternatives or
run together. Anything that draws or reasons about a graph has to decide this, and
the document does not.

Rendered from the corpus, two fixtures describing different execution semantics
come out as the same picture with a different dash pattern:

| Fixture | Edges out of the branching node |
| --- | --- |
| `parallel-fanout` | `fork → left`, `fork → right`, both `kind: "direct"` |
| `conditional-routing` | `router → left`, `router → right`, both `kind: "conditional"` |

`kind` does not settle it. A LangGraph conditional router may return a list of
destinations, so a `conditional` fan-out can also be concurrent. Reading multiple
`conditional` edges as exclusive is an unsound inference that a consumer is
nonetheless pushed toward.

The README records that the format does not establish this. This issue is about its
cost: every consumer guesses, and each guesses differently. That is the failure
mode `conformance/fixtures/` prevents among producers, with no equivalent on the
consuming side.

## The asymmetry

The format models convergence as a structure-level collection with explicit members
(`joins[]`, carrying `sources` and `target`). It has no representation of
divergence.

Convergence is often inferable from edges. Divergence is the genuinely ambiguous
one. The missing half of the pair is the half that needed writing down.

## Proposed shape

A structure-level collection mirroring `joins[]`:

```json
"branches": [
  {
    "id": "branch:router",
    "sourceId": "router",
    "mode": "exclusive",
    "edgeIds": ["edge:router:left:conditional:1", "edge:router:right:conditional:1"]
  }
]
```

`mode` in `exclusive | concurrent | unknown`. `unknown` keeps the "honest about
gaps" posture where a producer genuinely cannot tell, and is distinct from the
format being unable to express it — a distinction consumers currently cannot make.

## Trialled as an extension

Injected as `structure["x-topology-branch"]` and rendered before and after:

| Fixture | Declared mode | Valid 0.1 document | Structure hash |
| --- | --- | --- | --- |
| `conditional-routing` | `exclusive` | yes | unchanged |
| `parallel-fanout` | `concurrent` | yes | unchanged |
| `multi-source-join` | `concurrent` | yes | unchanged |
| `loop` | `unknown` | yes | unchanged |

The hash does not move because `_NODE_HASH_FIELDS` and its edge and join
counterparts project a fixed field set (`_canonical.py:14`), leaving `x-*` outside
the hash by construction. A producer can therefore trial this field without
invalidating any published fixture hash or qualification receipt.

## Against the core field test

> Would Temporal, Airflow, CrewAI, and LangGraph all be able to emit this?

Airflow: yes, and checked rather than argued. Constructing a DAG and reading its
structure — no scheduler, webserver, metadata database, or `airflow db init` —
gives:

```
task           downstream                   fan-out mode
fork           left,right                   concurrent
router         a,b                          exclusive
```

`BranchPythonOperator` selects among its downstream tasks; every other operator
runs all of them. A producer reads `mode` off the operator type. Script:
`probes/airflow/airflow_probe.py`.

Temporal is a separate matter. Its workflows are imperative code whose structure is
not available without execution, so it cannot emit this field — or, for the same
reason, most existing core fields. A "no" from Temporal may mean the framework is
not a candidate producer rather than that the field is vendor-specific. Raising it
here only because the test names it; happy to split that into its own issue.

## Not yet proven

The modes above are asserted from each fixture's name, not derived by a producer.
This shows what the field buys a consumer, and that a structurally different
framework can see the distinction. It does not show an `agent-topology` producer
populating it end to end.

The natural next step is the Python LangGraph producer emitting
`x-topology-branch` for real, before any schema change is proposed. Happy to do
that work if the direction is welcome.

## Correction

The Airflow check above read `exclusive` off operator class alone. A follow-up
probe (testbed issue #3) found a `BranchPythonOperator` callback returning
`["a", "b"]` runs both targets — operator class does not establish exclusivity.
See the "Correction (P1)" section in the linked finding before filing this
issue upstream as written.
