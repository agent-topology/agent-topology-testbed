# F1 — A fan-out cannot be read as exclusive or concurrent

**Status: trialled.** Observed against `@agent-topology/spec@0.1.0-beta.2`.
Upstream issue body in [ISSUE.md](ISSUE.md).

## The claim

A consumer cannot determine, from a 0.1 document, whether the several destinations
of a branching node are alternatives or run together. Every consumer that draws or
reasons about a graph must decide this, and nothing in the document decides it for
them.

## Reproduction

`instrument/` renders the conformance corpus. Two fixtures that describe
fundamentally different execution semantics come out as the same picture with a
different dash pattern:

| Fixture | Edges out of the branching node |
| --- | --- |
| `parallel-fanout` | `fork → left`, `fork → right`, both `kind: "direct"` |
| `conditional-routing` | `router → left`, `router → right`, both `kind: "conditional"` |

See `evidence/parallel-fanout.core.svg` and `evidence/conditional-routing.core.svg`.

The tempting inference — *multiple `direct` means all run, multiple `conditional`
means one runs* — is not sound. A LangGraph conditional router may return a list of
destinations, so a `conditional` fan-out can also be concurrent. The main README
already states the format does not settle this. The cost of not settling it is that
every consumer guesses, and each guesses differently.

That is the failure mode `conformance/fixtures/` exists to prevent among producers.
There is no equivalent protection on the consuming side.

## The asymmetry

The format models **convergence** as a structure-level collection with explicit
members (`joins[]`, with `sources` and `target`). It has no representation of
**divergence** at all.

This is backwards relative to difficulty. Convergence can often be inferred from
edges; divergence is the genuinely ambiguous one. The missing half of the pair is
the half that needed to be written down.

## Trial

`instrument/src/experiment.ts` injects a candidate field as
`structure["x-topology-branch"]` and renders each fixture twice — core fields only,
and with the field read. Output in `evidence/compare.html`.

```
conditional-routing  mode=exclusive   valid=true hashUnchanged=true
loop                 mode=unknown     valid=true hashUnchanged=true
multi-source-join    mode=concurrent  valid=true hashUnchanged=true
parallel-fanout      mode=concurrent  valid=true hashUnchanged=true
```

**The hash result is what makes this trialable.** `_NODE_HASH_FIELDS` and its edge
and join counterparts project a fixed field set, so `x-*` data sits outside the
hash by construction (`_canonical.py:14`). An experimental field can ship in a
producer without moving a single published fixture hash or qualification receipt.

Two things the rendering shows that a schema discussion does not:

- `conditional-routing` and `parallel-fanout` stop being the same picture. One
  reads *one of*, the other *all run*, and the redline disappears from both because
  there is nothing left to withhold.
- `loop` keeps its redline but changes note code, from
  `fan-out-semantics-unstated` to `fan-out-semantics-unknown`. That distinction is
  worth carrying: the first says the format has no way to express this, the second
  says a producer looked and could not tell. A consumer should treat them
  differently and today cannot tell them apart.

## Cross-framework check

`probes/airflow/` constructs a DAG and reads its structure with no scheduler, no
webserver, no metadata database, and no `airflow db init`. Transcript in
`evidence/airflow-probe.txt`.

```
task           downstream                   fan-out mode
fork           left,right                   concurrent
router         a,b                          exclusive
```

Airflow carries the distinction natively: `BranchPythonOperator` selects among its
downstream tasks, every other operator runs all of them. A producer reads `mode`
off the operator type.

## What is not proven

The modes in the trial are asserted from each fixture's name, not derived by a
producer. This demonstrates what the field buys a **consumer**. The Airflow probe
demonstrates that a structurally different framework **can see** the distinction.
Neither demonstrates that an `agent-topology` producer populates it end to end.

The next piece of evidence is the Python LangGraph producer emitting
`x-topology-branch` for real. That is cheap — the hash does not move, so nothing
published is invalidated — and it is the step that should come before anyone
proposes a schema change.

## Correction (P1)

The "Cross-framework check" above asserts `router → a,b : exclusive` from
`BranchPythonOperator`'s operator class alone. [P1](../../observations/P1/README.md)
(issue [#3](https://github.com/agent-topology/agent-topology-testbed/issues/3))
tested that claim directly and it does not hold: a `BranchPythonOperator` whose
callback returns `["a", "b"]` runs both `a` and `b` (`dag.test()`, both task
instances `success`). Operator class is a static fact; how many targets a given
run selects is a callback-return fact; which downstream tasks actually execute
is scheduler evidence. The original check conflated the three, exactly the
shortcut `AGENTS.md` now names: "No fixture-name, operator-class, or
return-annotation shortcut establishes runtime semantics."

This does not withdraw F1's core claim — the format still cannot distinguish
exclusive from concurrent fan-out, and Airflow still resolves that ambiguity for
its own execution, just not from operator class alone. `probes/airflow/airflow_probe.py`
and its example DAG were corrected to report the operator-class fact without the
derived exclusive/concurrent conclusion. `OUTPUT.txt` and `evidence/airflow-probe.txt`
are left as the original beta.2 transcripts of the pre-correction script.

## Note on the core field test

The main README's test is *"Would Temporal, Airflow, CrewAI, and LangGraph all be
able to emit this?"* That test has a hidden assumption: that all four have a
statically derivable structure.

Temporal workflows are imperative code. Their structure is not available without
execution, so Temporal cannot emit this field — or, for the same reason, most of
the existing core fields. A "no" from Temporal therefore does not mean a field is
vendor-specific; it may mean Temporal is not a candidate producer. The example list
in that test may be worth revisiting separately.
