import type { TopologyGraph } from "@agent-topology/spec";
import { metrics } from "./theme.js";

/**
 * Deterministic layered layout.
 *
 * Determinism is a hard requirement: this output is meant to be committed and
 * diffed, so the same document must always produce byte-identical geometry.
 * Every ordering step below therefore breaks ties on the node identifier, and
 * the barycenter refinement runs a fixed number of passes rather than
 * iterating to convergence.
 */

export type EdgeKind = "direct" | "conditional" | "join-in" | "join-out";

export interface LayoutNode {
  id: string;
  kind: "node" | "join";
  label: string;
  rank: number;
  x: number;
  y: number;
  w: number;
  h: number;
  isEntry: boolean;
  isExit: boolean;
  interruptBefore: boolean;
  interruptAfter: boolean;
  /** Number of outgoing edges whose relationship to each other is unstated. */
  fanOut: number;
}

export interface LayoutEdge {
  id: string;
  source: string;
  target: string;
  kind: EdgeKind;
  /** False when the edge is synthesised from `joins[]` rather than `edges[]`. */
  declared: boolean;
  backEdge: boolean;
  selfLoop: boolean;
  path: string;
  arrowAt: { x: number; y: number };
}

export interface Layout {
  nodes: LayoutNode[];
  edges: LayoutEdge[];
  width: number;
  height: number;
}

function nodeWidth(label: string): number {
  return Math.max(
    metrics.minNodeWidth,
    Math.round(label.length * metrics.charWidth) + metrics.nodePadX * 2,
  );
}

export function layoutGraph(graph: TopologyGraph): Layout {
  const structure = graph.structure;
  const entry = new Set(structure.entryNodeIds);
  const exit = new Set(structure.exitNodeIds);

  const nodes: LayoutNode[] = structure.nodes.map((n) => ({
    id: n.id,
    kind: "node" as const,
    label: n.id,
    rank: 0,
    x: 0,
    y: 0,
    w: nodeWidth(n.id),
    h: metrics.nodeHeight,
    isEntry: entry.has(n.id),
    isExit: exit.has(n.id),
    interruptBefore: (n.interrupts ?? []).includes("before"),
    interruptAfter: (n.interrupts ?? []).includes("after"),
    fanOut: 0,
  }));

  const edges: LayoutEdge[] = structure.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    kind: e.kind as EdgeKind,
    declared: true,
    backEdge: false,
    selfLoop: e.source === e.target,
    path: "",
    arrowAt: { x: 0, y: 0 },
  }));

  // A multi-source join is declared only in `joins[]`. There is no corresponding
  // entry in `edges[]`, so a renderer that draws edges alone produces a
  // disconnected graph. Synthesise the connection and mark it as derived.
  for (const join of structure.joins) {
    nodes.push({
      id: join.id,
      kind: "join",
      label: join.id,
      rank: 0,
      x: 0,
      y: 0,
      w: 0,
      h: metrics.joinBarHeight,
      isEntry: false,
      isExit: false,
      interruptBefore: false,
      interruptAfter: false,
      fanOut: 0,
    });
    for (const source of join.sources) {
      edges.push({
        id: `${join.id}//in//${source}`,
        source,
        target: join.id,
        kind: "join-in",
        declared: false,
        backEdge: false,
        selfLoop: false,
        path: "",
        arrowAt: { x: 0, y: 0 },
      });
    }
    edges.push({
      id: `${join.id}//out`,
      source: join.id,
      target: join.target,
      kind: "join-out",
      declared: false,
      backEdge: false,
      selfLoop: false,
      path: "",
      arrowAt: { x: 0, y: 0 },
    });
  }

  const byId = new Map(nodes.map((n) => [n.id, n]));

  // Count declared outgoing edges per node. Two or more means the document
  // shows a fan-out whose semantics it does not state.
  for (const e of edges) {
    if (!e.declared) continue;
    const n = byId.get(e.source);
    if (n) n.fanOut += 1;
  }

  // --- back-edge detection -------------------------------------------------
  const out = new Map<string, LayoutEdge[]>();
  for (const n of nodes) out.set(n.id, []);
  for (const e of edges) out.get(e.source)?.push(e);
  for (const list of out.values()) list.sort((a, b) => (a.target < b.target ? -1 : a.target > b.target ? 1 : 0));

  const state = new Map<string, 0 | 1 | 2>(nodes.map((n) => [n.id, 0]));
  const discovery = new Map<string, number>();
  let counter = 0;

  const roots = [
    ...[...entry].filter((id) => byId.has(id)).sort(),
    ...nodes.map((n) => n.id).sort(),
  ];

  for (const root of roots) {
    if (state.get(root) !== 0) continue;
    // Iterative DFS, so that deep graphs cannot blow the stack.
    const stack: Array<{ id: string; i: number }> = [{ id: root, i: 0 }];
    state.set(root, 1);
    discovery.set(root, counter++);
    while (stack.length > 0) {
      const frame = stack[stack.length - 1];
      const outgoing = out.get(frame.id) ?? [];
      if (frame.i >= outgoing.length) {
        state.set(frame.id, 2);
        stack.pop();
        continue;
      }
      const edge = outgoing[frame.i++];
      if (edge.selfLoop) continue;
      const s = state.get(edge.target);
      if (s === 1) {
        edge.backEdge = true;
      } else if (s === 0) {
        state.set(edge.target, 1);
        discovery.set(edge.target, counter++);
        stack.push({ id: edge.target, i: 0 });
      }
    }
  }

  // --- longest-path layering on the acyclic remainder ----------------------
  const forward = edges.filter((e) => !e.backEdge && !e.selfLoop);
  const indegree = new Map<string, number>(nodes.map((n) => [n.id, 0]));
  for (const e of forward) indegree.set(e.target, (indegree.get(e.target) ?? 0) + 1);

  const ready = nodes
    .map((n) => n.id)
    .filter((id) => (indegree.get(id) ?? 0) === 0)
    .sort();
  const rank = new Map<string, number>(nodes.map((n) => [n.id, 0]));
  const queue = [...ready];
  while (queue.length > 0) {
    const id = queue.shift() as string;
    for (const e of out.get(id) ?? []) {
      if (e.backEdge || e.selfLoop) continue;
      rank.set(e.target, Math.max(rank.get(e.target) ?? 0, (rank.get(id) ?? 0) + 1));
      const left = (indegree.get(e.target) ?? 0) - 1;
      indegree.set(e.target, left);
      if (left === 0) {
        queue.push(e.target);
        queue.sort();
      }
    }
  }
  for (const n of nodes) n.rank = rank.get(n.id) ?? 0;

  // --- ordering within each rank -------------------------------------------
  const ranks: LayoutNode[][] = [];
  for (const n of nodes) {
    (ranks[n.rank] ??= []).push(n);
  }
  for (let r = 0; r < ranks.length; r++) {
    ranks[r] ??= [];
    ranks[r].sort((a, b) => {
      const da = discovery.get(a.id) ?? Number.MAX_SAFE_INTEGER;
      const db = discovery.get(b.id) ?? Number.MAX_SAFE_INTEGER;
      return da !== db ? da - db : a.id < b.id ? -1 : 1;
    });
  }

  const position = new Map<string, number>();
  const reindex = () => {
    for (const row of ranks) row.forEach((n, i) => position.set(n.id, i));
  };
  reindex();

  const neighbours = (id: string, dir: -1 | 1): string[] => {
    const result: string[] = [];
    for (const e of forward) {
      if (dir === -1 && e.target === id) result.push(e.source);
      if (dir === 1 && e.source === id) result.push(e.target);
    }
    return result;
  };

  // Fixed pass count keeps this deterministic; convergence is not required for
  // graphs of the size this format produces.
  for (let pass = 0; pass < 4; pass++) {
    const dir: -1 | 1 = pass % 2 === 0 ? -1 : 1;
    const order = dir === -1 ? [...ranks.keys()] : [...ranks.keys()].reverse();
    for (const r of order) {
      const row = ranks[r];
      if (!row || row.length < 2) continue;
      const bary = new Map<string, number>();
      for (const n of row) {
        const ns = neighbours(n.id, dir)
          .map((id) => position.get(id))
          .filter((v): v is number => v !== undefined);
        bary.set(n.id, ns.length === 0 ? position.get(n.id) ?? 0 : ns.reduce((a, b) => a + b, 0) / ns.length);
      }
      row.sort((a, b) => {
        const diff = (bary.get(a.id) as number) - (bary.get(b.id) as number);
        if (Math.abs(diff) > 1e-9) return diff;
        return a.id < b.id ? -1 : 1;
      });
      reindex();
    }
  }

  // --- coordinates ---------------------------------------------------------
  // A join bar spans the nodes feeding it, so it is sized after ordering.
  const rowWidth = (row: LayoutNode[]) =>
    row.reduce((sum, n) => sum + n.w, 0) + metrics.siblingGap * Math.max(0, row.length - 1);

  for (const row of ranks) {
    for (const n of row) {
      if (n.kind !== "join") continue;
      const sources = edges.filter((e) => e.kind === "join-in" && e.target === n.id).map((e) => byId.get(e.source));
      const widths = sources.filter((s): s is LayoutNode => Boolean(s)).map((s) => s.w);
      n.w = Math.max(110, widths.reduce((a, b) => a + b, 0) + metrics.siblingGap);
    }
  }

  const widest = Math.max(...ranks.map((row) => rowWidth(row ?? [])), 1);
  const canvasWidth = widest + metrics.marginX * 2;

  for (let r = 0; r < ranks.length; r++) {
    const row = ranks[r];
    if (!row) continue;
    let x = (canvasWidth - rowWidth(row)) / 2;
    const slotTop = metrics.marginTop + r * (metrics.nodeHeight + metrics.rankGap);
    for (const n of row) {
      n.x = x;
      n.y = slotTop + (metrics.nodeHeight - n.h) / 2;
      x += n.w + metrics.siblingGap;
    }
  }

  const canvasHeight =
    metrics.marginTop +
    ranks.length * metrics.nodeHeight +
    Math.max(0, ranks.length - 1) * metrics.rankGap +
    metrics.marginBottom;

  // --- edge routing --------------------------------------------------------
  const sideLane = canvasWidth - 12;
  for (const e of edges) {
    const s = byId.get(e.source);
    const t = byId.get(e.target);
    if (!s || !t) continue;

    if (e.selfLoop) {
      const x = s.x + s.w;
      const y = s.y + s.h / 2;
      e.path = `M ${x} ${y - 8} C ${x + 34} ${y - 26}, ${x + 34} ${y + 26}, ${x} ${y + 8}`;
      e.arrowAt = { x: x + 1, y: y + 8 };
      continue;
    }

    if (e.backEdge) {
      const sy = s.y + s.h / 2;
      const ty = t.y + t.h / 2;
      const sx = s.x + s.w;
      const tx = t.x + t.w;
      e.path =
        `M ${sx} ${sy} L ${sideLane - 14} ${sy} ` +
        `Q ${sideLane} ${sy}, ${sideLane} ${sy - 14} ` +
        `L ${sideLane} ${ty + 14} ` +
        `Q ${sideLane} ${ty}, ${sideLane - 14} ${ty} L ${tx} ${ty}`;
      e.arrowAt = { x: tx, y: ty };
      continue;
    }

    const x1 = s.x + s.w / 2;
    const y1 = s.y + s.h;
    const x2 = t.x + t.w / 2;
    const y2 = t.y;
    const mid = (y1 + y2) / 2;
    e.path = `M ${x1} ${y1} C ${x1} ${mid}, ${x2} ${mid}, ${x2} ${y2}`;
    e.arrowAt = { x: x2, y: y2 };
  }

  return { nodes, edges, width: canvasWidth, height: canvasHeight };
}

/** Rounds geometry so that committed SVG files diff cleanly. */
export function n2(value: number): string {
  return (Math.round(value * 100) / 100).toString();
}
