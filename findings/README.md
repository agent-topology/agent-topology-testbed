# Findings

A finding is a claim about the `agent-topology` format with a reproduction
attached. This file is the index.

## Index

| ID | Claim | Status | Upstream |
| --- | --- | --- | --- |
| [F1](F1-fan-out-semantics/) | A fan-out cannot be read as exclusive or concurrent | trialled | not filed |
| [F2](#f2--entrynodeids-conflates-a-graph-entry-with-a-node-that-lost-its-predecessor) | `entryNodeIds` conflates entry with orphaned-by-gap | reproduced | not filed |
| [F3](F3-opaque-subgraph/) | An opaque subgraph is indistinguishable from an ordinary node | reproduced | not filed |
| [F4](#f4--join-connections-exist-only-in-joins-never-in-edges) | Join connections absent from `edges[]` | reproduced | not filed |
| [F5](#f5--hiding-framework-sentinels-requires-vendor-coupling) | Sentinels cannot be hidden neutrally | reproduced | not filed |
| [F6](#f6--agent-topologyspec-is-esm-only-and-the-failure-is-not-actionable) | ESM-only package, unactionable error | reproduced | not filed |

All findings above were observed against `@agent-topology/spec@0.1.0-beta.2`.

## Status lifecycle

```
observed     someone hit it once
reproduced   a script in this repository reproduces it from a fixture
trialled     a candidate change is implemented here and its cost measured
filed        an issue exists upstream
resolved     upstream changed, or the finding was withdrawn with a reason
withdrawn    the claim did not survive; the reason stays recorded
```

Two rules that keep this honest:

**Nothing is filed before it is reproduced.** An upstream issue without a
reproduction spends a maintainer's attention to re-derive what this repository
exists to have derived already.

**Withdrawn findings are not deleted.** A claim that did not survive is evidence
about the format too, and deleting it means the next person re-opens it.

## What a finding directory contains

A finding earns a directory when it has evidence to hold. Otherwise it stays
inline here.

```
F1-fan-out-semantics/
  README.md     the claim, the reproduction, what is and is not proven
  ISSUE.md      the upstream issue body, ready to paste
  evidence/     rendered output, probe transcripts
```

`ISSUE.md` is kept separate from `README.md` on purpose. The finding is written for
whoever maintains this repository and may say "not yet proven"; the issue is
written for whoever maintains the format and should not carry this repository's
internal bookkeeping.

---

## F2 — `entryNodeIds` conflates a graph entry with a node that lost its predecessor

**Status: reproduced.** `gallery/unknown-routing-targets.svg`.

In the `unknown-routing-targets` fixture the router's destinations could not be
determined, so `target` has no incoming edge. It therefore appears in
`entryNodeIds` alongside `__start__`, and any renderer draws it as a second entry
point to the graph.

That picture is wrong, and a consumer that surfaces `completeness` correctly still
draws it. The gap is recorded against `router`; the visible damage lands on
`target`; nothing connects the two.

This also blocks a useful affordance. A consumer would like to say *"this is where
the graph starts"*, and cannot, because membership in `entryNodeIds` may instead
mean *"the producer could not see what points here"*.

**Suggestion.** Either omit nodes orphaned by a recorded gap from `entryNodeIds`,
or emit a second gap against the orphaned node so the consequence is discoverable
at the element that shows it.

---

## F4 — Join connections exist only in `joins[]`, never in `edges[]`

**Status: reproduced.** `gallery/multi-source-join.svg`.

There is no `left → joined` or `right → joined` edge in that fixture. The
connection appears only as a `joins[]` entry, so a consumer that iterates `edges[]`
to draw the graph — the obvious first implementation — produces a disconnected
picture with two dead ends and an orphan.

This is a reasonable modelling decision, not necessarily a defect. But it is a
silent trap, and the derivation rule is not stated in
`docs/guides/consuming-documents.md`.

**Suggestion.** Document the rule, and consider exporting a helper from the spec
packages (`derivedJoinEdges(structure)` or similar) so every consumer derives the
same connections the same way. Leaving each consumer to reimplement it is how
consumer dialects start — the thing `conformance/fixtures/` prevents among
producers, with no equivalent on the consuming side.

---

## F5 — Hiding framework sentinels requires vendor coupling

**Status: reproduced.** Visible in all eight drawings in `gallery/`.

`__start__` and `__end__` are ordinary entries in `nodes[]`. In every fixture, two
of the nodes are framework artifacts rather than author intent.

A framework-neutral consumer has no good option. Drawing them exposes LangGraph
internals in a picture meant to be neutral. Hiding them requires reading
`x-langgraph`, which couples the consumer to one producer. Matching the literal
strings is the same coupling with worse hygiene. `entryNodeIds` / `exitNodeIds` do
not help, both because of F2 and because membership does not imply the node is a
sentinel rather than a real first step.

The main README already lists this as a known limit. This is a note on its cost: it
is paid by every consumer, in every document, and there is currently no neutral way
to pay it.

---

## F6 — `@agent-topology/spec` is ESM-only, and the failure is not actionable

**Status: reproduced.** Hit while setting up `instrument/`.

A CommonJS consumer gets:

```
Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: No "exports" main defined in
.../node_modules/@agent-topology/spec/package.json
```

The `exports` map declares only `types` and `import` — no `require` condition and
no `default`. The error says nothing about ESM, so the reader's first guess is a
broken package rather than a module-format mismatch.

**Suggestion.** Ship a `require` condition, or state ESM-only prominently in
`docs/getting-started/typescript.md`. Given the pre-1.0 posture, documenting it is
probably enough.

**What worked.** Beyond this, the package holds up as a standalone dependency:
zero runtime dependencies, clean install, and `assertTopologyDocument` usable with
no framework runtime present. The claim that the spec package is independently
consumable checks out.
