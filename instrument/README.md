# instrument

The renderer used to produce visual evidence for `findings/`.

**This is a measuring device, not a viewer.** Rendering is the cheapest way to
force a consumer to make every decision the format leaves open, and the drawing
makes the resulting ambiguity visible. A publishable viewer would need a stricter
contract than this one keeps — see the note on reading extensions below.

**Not part of the 0.1 contract.** It consumes the published packages exactly as any
other consumer does. A break here is a signal, not a release blocker.

```
npm install
npm run build     # renders ../repo/conformance/fixtures -> out/
open out/index.html
```

```
npm run experiment    # core-only vs proposed branch field -> out/compare.html
```

Override the inputs with `FIXTURES=/path/to/fixtures OUT=dist npm run build`.

## What it draws

Ink is what the document asserts. Red is what it cannot, and every red mark
carries a numbered note in the block beneath the drawing. Red means one thing —
*do not trust this part* — and is used for nothing else.

| Mark | Meaning |
| --- | --- |
| Filled pill | node in `entryNodeIds` |
| Double outline | node in `exitNodeIds` |
| Solid line | `kind: "direct"` |
| Dashed line | `kind: "conditional"` |
| Dotted line | derived from `joins[]`, not present in `edges[]` |
| Bar across an edge | `interrupts`, positioned before or after the node |
| Red dashed outline | element referenced by a `completeness` gap |
| Red bracket | fan-out whose semantics the document does not state |

The red bracket is the deliberate part. The document distinguishes `direct` from
`conditional` edges, and it is tempting to read a `conditional` fan-out as
alternatives and a `direct` fan-out as concurrency. That reading is not sound — see
F1 in [F1](../findings/F1-fan-out-semantics/README.md) — so the renderer refuses to make it and marks the
ambiguity instead. Line style reports `kind` because `kind` is a real field; the
bracket exists so that nobody reads more into it than it says.

## Constraints this prototype holds itself to

These are the properties that make the output usable as documentation rather than
as a one-off picture.

- **Pure.** `renderGraph(document, graph)` performs no I/O, reads no clock, and
  uses no random source.
- **Deterministic.** The same document always produces the same bytes. Layer
  ordering breaks every tie on the node identifier, and the barycenter refinement
  runs a fixed number of passes rather than iterating to convergence. Geometry is
  rounded to two decimals so committed files diff cleanly. `build.ts` renders each
  graph twice and fails if the output differs.
- **String SVG as the primary output.** A component would not embed in docs, in a
  README, or in a pull-request comment. Interactive wrappers belong on top of this,
  not in place of it.
- **Offline.** No webfonts, no network at render time, no headless browser. The
  gallery can be regenerated in CI whenever a fixture changes.
- **Read-only.** There is no path from this code back to a document. A viewer that
  can author is a viewer that breaks *derived, never authored*.
- **Core fields only by default.** `x-*` is not read unless a caller opts in.
  Reading `x-langgraph` would make the renderer LangGraph-shaped, which defeats the
  point of rendering from the format at all.

  The one sanctioned exception is trialling a *proposed core field*: `npm run
  experiment` reads `x-topology-branch` behind an explicit flag, and renders the
  same document with and without it. That is a testbed's job and would be a defect
  in a shipped viewer. The extension is named for the field being proposed, not for
  a vendor, so it cannot quietly become a vendor dialect.
- **Refuses what it does not understand.** `assertTopologyDocument` runs on every
  input, and any `topologyVersion` other than `0.1` is rejected before drawing —
  the same posture the producers take toward untested framework versions.

## Layout

Longest-path layering over the graph with back edges removed by DFS, then four
fixed barycenter passes for within-rank ordering. Back edges route through a lane
on the right; self-loops draw as a side arc. It is not a Sugiyama implementation
and makes no attempt at crossing minimisation beyond the barycenter passes —
adequate for graphs of the size this format produces, and small enough to replace.

## Files

```
src/theme.ts    design tokens
src/layout.ts   deterministic layered layout
src/render.ts   pure document -> SVG
src/build.ts    fixture corpus -> out/*.svg + out/index.html
src/experiment.ts  before/after trial of the proposed branch field
```

## Status

Prototype, and deliberately still one. It exists to answer two questions: how to
draw what the format leaves unstated, and whether rendering the conformance corpus
surfaces real problems. It does — see [`../findings/`](../findings/README.md).

Extracting a publishable viewer from this is a separate decision with a stricter
contract, and is not made yet.
