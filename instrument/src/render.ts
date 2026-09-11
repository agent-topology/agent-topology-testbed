import type { TopologyDocument, TopologyGraph } from "@agent-topology/spec";
import { layoutGraph, n2, type LayoutEdge, type LayoutNode } from "./layout.js";
import { metrics, theme } from "./theme.js";

/**
 * Renders one graph of a topology document as a standalone SVG string.
 *
 * This is a pure function. It performs no I/O, reads no clock, and uses no
 * random source, so the same document always yields the same bytes.
 *
 * Rendering rule: anything the document asserts is drawn in ink. Anything the
 * document cannot assert is a redline annotation with a numbered margin note.
 * Red carries exactly one meaning here and is used for nothing else.
 */

const TITLE_BLOCK_H = 58;

/**
 * Proposed core field, prototyped as an extension.
 *
 * Placed on `structure` rather than on the node so that it mirrors `joins[]`:
 * the format already models convergence as a structure-level collection with
 * explicit members, and divergence is the missing half of that pair.
 */
export interface BranchExtension {
  id: string;
  sourceId: string;
  mode: "exclusive" | "concurrent" | "unknown";
  edgeIds: string[];
}

export const BRANCH_EXTENSION_KEY = "x-topology-branch";

export interface RenderOptions {
  /**
   * Read the proposed branch extension. Off by default: the renderer draws from
   * core fields only unless a caller explicitly opts into the experiment.
   */
  branchExtension?: boolean;
}

function readBranches(graph: TopologyGraph, options: RenderOptions): Map<string, BranchExtension> {
  const result = new Map<string, BranchExtension>();
  if (!options.branchExtension) return result;
  const raw = (graph.structure as unknown as Record<string, unknown>)[BRANCH_EXTENSION_KEY];
  if (!Array.isArray(raw)) return result;
  for (const entry of raw as BranchExtension[]) {
    if (entry && typeof entry.sourceId === "string") result.set(entry.sourceId, entry);
  }
  return result;
}

const MODE_LABEL: Record<BranchExtension["mode"], string> = {
  exclusive: "one of",
  concurrent: "all run",
  unknown: "? unknown",
};
const NOTE_LINE_H = 17;

interface Note {
  index: number;
  tone: "redline" | "ink";
  code: string;
  text: string;
}

function esc(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function collectNotes(
  doc: TopologyDocument,
  graph: TopologyGraph,
  layout: ReturnType<typeof layoutGraph>,
  branches: Map<string, BranchExtension>,
) {
  const notes: Note[] = [];
  const flaggedNodes = new Map<string, number[]>();
  const flaggedEdges = new Map<string, number[]>();
  let index = 0;

  const push = (tone: Note["tone"], code: string, text: string): number => {
    index += 1;
    notes.push({ index, tone, code, text });
    return index;
  };

  // 1. Completeness gaps that point at this graph.
  for (const gap of doc.completeness.gaps) {
    const element = gap.element as { kind: string; id?: string; graphId?: string };
    if (element.graphId !== undefined && element.graphId !== graph.id) continue;
    const marker = push("redline", gap.code, gap.message);
    if (element.id) {
      if (layout.nodes.some((node) => node.id === element.id)) {
        flaggedNodes.set(element.id, [...(flaggedNodes.get(element.id) ?? []), marker]);
      }
      if (layout.edges.some((edge) => edge.id === element.id)) {
        flaggedEdges.set(element.id, [...(flaggedEdges.get(element.id) ?? []), marker]);
      }
    }
  }

  // 2. Fan-out. Resolved by the branch extension where present; otherwise the
  //    document leaves the relationship between destinations unstated.
  const fanOutNodes = layout.nodes.filter((node) => node.fanOut >= 2).map((node) => node.id).sort();
  const unresolved = fanOutNodes.filter((id) => {
    const branch = branches.get(id);
    return branch === undefined || branch.mode === "unknown";
  });
  let fanOutMarker: number | undefined;
  if (unresolved.length > 0) {
    const declaredUnknown = unresolved.filter((id) => branches.get(id)?.mode === "unknown");
    fanOutMarker = push(
      "redline",
      declaredUnknown.length === unresolved.length && declaredUnknown.length > 0
        ? "fan-out-semantics-unknown"
        : "fan-out-semantics-unstated",
      declaredUnknown.length === unresolved.length && declaredUnknown.length > 0
        ? `The producer could not determine whether the destinations of ${unresolved
            .map((id) => `'${id}'`)
            .join(", ")} are alternatives or run together, and says so.`
        : `The document does not state whether the destinations of ${unresolved
            .map((id) => `'${id}'`)
            .join(", ")} are alternatives or run together. Edge 'kind' does not settle this.`,
    );
  }
  const resolvedCount = fanOutNodes.length - unresolved.length;
  if (resolvedCount > 0) {
    push(
      "ink",
      BRANCH_EXTENSION_KEY,
      `${resolvedCount} fan-out${resolvedCount === 1 ? "" : "s"} read from the proposed branch extension. This field is not part of the 0.1 contract.`,
    );
  }

  // 3. Connections present in joins[] but absent from edges[].
  const joinCount = graph.structure.joins.length;
  if (joinCount > 0) {
    push(
      "ink",
      "derived-join-edges",
      `${joinCount} join${joinCount === 1 ? "" : "s"} declared in joins[] with no matching entry in edges[]. The dotted connections are derived by this renderer.`,
    );
  }

  // 4. Producer-wide limitations. These do not make a document incomplete, but
  //    a consumer still has to surface them.
  for (const limitation of doc.producerLimitations) {
    const item = limitation as { code?: string; message?: string };
    push("ink", item.code ?? "producer-limitation", item.message ?? "");
  }

  return { notes, flaggedNodes, flaggedEdges, fanOutMarker };
}

function drawNode(node: LayoutNode, markers: number[] | undefined): string {
  if (node.kind === "join") {
    return [
      `<rect x="${n2(node.x)}" y="${n2(node.y)}" width="${n2(node.w)}" height="${n2(node.h)}" rx="2" fill="${theme.ink}"/>`,
      `<text x="${n2(node.x + node.w + 8)}" y="${n2(node.y + node.h)}" font-family="${theme.sans}" font-size="10" fill="${theme.muted}">join</text>`,
    ].join("");
  }

  const flagged = markers !== undefined && markers.length > 0;
  const stroke = flagged ? theme.redline : theme.ink;
  const rx = node.isEntry || node.isExit ? node.h / 2 : 4;
  const fill = node.isEntry ? theme.ink : theme.paper;
  const textFill = node.isEntry ? theme.paper : theme.ink;

  const parts: string[] = [];
  if (flagged) {
    parts.push(
      `<rect x="${n2(node.x - 5)}" y="${n2(node.y - 5)}" width="${n2(node.w + 10)}" height="${n2(node.h + 10)}" rx="${n2(rx + 5)}" fill="${theme.redlineWash}" stroke="${theme.redline}" stroke-width="1" stroke-dasharray="4 3"/>`,
    );
  }
  parts.push(
    `<rect x="${n2(node.x)}" y="${n2(node.y)}" width="${n2(node.w)}" height="${n2(node.h)}" rx="${n2(rx)}" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>`,
  );
  if (node.isExit) {
    parts.push(
      `<rect x="${n2(node.x + 3.5)}" y="${n2(node.y + 3.5)}" width="${n2(node.w - 7)}" height="${n2(node.h - 7)}" rx="${n2(Math.max(1, rx - 3.5))}" fill="none" stroke="${stroke}" stroke-width="1"/>`,
    );
  }
  parts.push(
    `<text x="${n2(node.x + node.w / 2)}" y="${n2(node.y + node.h / 2 + 4.5)}" text-anchor="middle" font-family="${theme.mono}" font-size="${metrics.fontSize}" fill="${textFill}">${esc(node.label)}</text>`,
  );

  // Interrupts are positioned where they happen: a bar across the top edge for
  // 'before', across the bottom edge for 'after'.
  if (node.interruptBefore) {
    parts.push(
      `<rect x="${n2(node.x + node.w / 2 - 11)}" y="${n2(node.y - 9)}" width="22" height="4" rx="1" fill="${theme.ink}"/>`,
      `<text x="${n2(node.x + node.w / 2 + 17)}" y="${n2(node.y - 5)}" font-family="${theme.sans}" font-size="9.5" fill="${theme.muted}">interrupt before</text>`,
    );
  }
  if (node.interruptAfter) {
    parts.push(
      `<rect x="${n2(node.x + node.w / 2 - 11)}" y="${n2(node.y + node.h + 5)}" width="22" height="4" rx="1" fill="${theme.ink}"/>`,
      `<text x="${n2(node.x + node.w / 2 + 17)}" y="${n2(node.y + node.h + 9)}" font-family="${theme.sans}" font-size="9.5" fill="${theme.muted}">interrupt after</text>`,
    );
  }

  for (const [i, marker] of (markers ?? []).entries()) {
    const cx = node.x + node.w + 7 + i * 18;
    const cy = node.y - 2;
    parts.push(
      `<circle cx="${n2(cx)}" cy="${n2(cy)}" r="8" fill="${theme.redline}"/>`,
      `<text x="${n2(cx)}" y="${n2(cy + 3.5)}" text-anchor="middle" font-family="${theme.sans}" font-size="10" font-weight="600" fill="${theme.paper}">${marker}</text>`,
    );
  }
  return parts.join("");
}

function drawEdge(edge: LayoutEdge, flagged: boolean): string {
  const stroke = flagged ? theme.redline : theme.ink;
  let dash = "";
  if (edge.kind === "conditional") dash = ` stroke-dasharray="6 4"`;
  if (edge.kind === "join-in" || edge.kind === "join-out") dash = ` stroke-dasharray="1.5 3.5"`;
  const marker = edge.kind === "join-in" ? "" : ` marker-end="url(#arrow-${flagged ? "red" : "ink"})"`;
  return `<path d="${edge.path}" fill="none" stroke="${stroke}" stroke-width="1.4"${dash}${marker}/>`;
}

/** The bracket that marks a fan-out whose semantics the document leaves open. */
function drawFanOutBracket(
  _node: LayoutNode,
  children: LayoutNode[],
  label: string,
  tone: "redline" | "ink",
): string {
  if (children.length < 2) return "";
  const colour = tone === "redline" ? theme.redline : theme.ink;
  const dash = tone === "redline" ? ` stroke-dasharray="4 3"` : "";
  const pillW = Math.max(48, label.length * 6.2 + 20);
  const xs = children.map((c) => c.x + c.w / 2).sort((a, b) => a - b);
  const left = xs[0];
  const right = xs[xs.length - 1];
  const y = Math.min(...children.map((c) => c.y)) - 20;
  const cx = (left + right) / 2;
  return [
    `<path d="M ${n2(left)} ${n2(y)} L ${n2(left)} ${n2(y + 8)} M ${n2(left)} ${n2(y)} L ${n2(right)} ${n2(y)} M ${n2(right)} ${n2(y)} L ${n2(right)} ${n2(y + 8)}" fill="none" stroke="${colour}" stroke-width="1.2"${dash}/>`,
    `<rect x="${n2(cx - pillW / 2)}" y="${n2(y - 9)}" width="${n2(pillW)}" height="18" rx="9" fill="${theme.paper}" stroke="${colour}" stroke-width="1.2"${dash}/>`,
    `<text x="${n2(cx)}" y="${n2(y + 3.5)}" text-anchor="middle" font-family="${theme.sans}" font-size="10" fill="${colour}">${esc(label)}</text>`,
  ].join("");
}

function titleBlock(doc: TopologyDocument, graph: TopologyGraph, width: number): string {
  const incomplete = doc.completeness.status !== "complete";
  const hash = doc.structureHash.value.slice(0, 12);
  const framework = `${doc.provenance.framework.name} ${doc.provenance.framework.version}`;
  const statusColour = incomplete ? theme.redline : theme.muted;
  return [
    `<text x="${n2(metrics.marginX)}" y="24" font-family="${theme.mono}" font-size="14" fill="${theme.ink}">${esc(graph.name ?? graph.id)}</text>`,
    `<text x="${n2(width - metrics.marginX)}" y="24" text-anchor="end" font-family="${theme.sans}" font-size="10.5" fill="${statusColour}">${esc(doc.completeness.status)}</text>`,
    `<text x="${n2(metrics.marginX)}" y="41" font-family="${theme.sans}" font-size="10.5" fill="${theme.muted}">topology ${esc(doc.topologyVersion)} &#160;&#160; ${esc(framework)} &#160;&#160; ${esc(doc.structureHash.algorithm)}:${esc(hash)}</text>`,
    `<line x1="0" y1="${TITLE_BLOCK_H - 8}" x2="${n2(width)}" y2="${TITLE_BLOCK_H - 8}" stroke="${theme.rule}" stroke-width="1"/>`,
  ].join("");
}

function notesBlock(notes: Note[], width: number, top: number): string {
  if (notes.length === 0) return "";
  const parts = [
    `<line x1="0" y1="${n2(top)}" x2="${n2(width)}" y2="${n2(top)}" stroke="${theme.rule}" stroke-width="1"/>`,
  ];
  let y = top + 22;
  for (const note of notes) {
    const colour = note.tone === "redline" ? theme.redline : theme.muted;
    parts.push(
      `<circle cx="${n2(metrics.marginX + 7)}" cy="${n2(y - 4)}" r="7.5" fill="${note.tone === "redline" ? theme.redline : "none"}" stroke="${colour}" stroke-width="1"/>`,
      `<text x="${n2(metrics.marginX + 7)}" y="${n2(y - 0.5)}" text-anchor="middle" font-family="${theme.sans}" font-size="9.5" font-weight="600" fill="${note.tone === "redline" ? theme.paper : colour}">${note.index}</text>`,
      `<text x="${n2(metrics.marginX + 22)}" y="${n2(y)}" font-family="${theme.mono}" font-size="10" fill="${colour}">${esc(note.code)}</text>`,
    );
    y += NOTE_LINE_H;
    for (const line of wrap(note.text, Math.floor((width - metrics.marginX * 2 - 22) / 5.9))) {
      parts.push(
        `<text x="${n2(metrics.marginX + 22)}" y="${n2(y)}" font-family="${theme.sans}" font-size="10.5" fill="${theme.ink}">${esc(line)}</text>`,
      );
      y += 14;
    }
    y += 8;
  }
  return parts.join("");
}

function wrap(text: string, columns: number): string[] {
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let line = "";
  for (const word of words) {
    if (line.length > 0 && line.length + 1 + word.length > columns) {
      lines.push(line);
      line = word;
    } else {
      line = line.length === 0 ? word : `${line} ${word}`;
    }
  }
  if (line.length > 0) lines.push(line);
  return lines;
}

function notesHeight(notes: Note[], width: number): number {
  if (notes.length === 0) return 0;
  let height = 22;
  for (const note of notes) {
    height += NOTE_LINE_H;
    height += wrap(note.text, Math.floor((width - metrics.marginX * 2 - 22) / 5.9)).length * 14;
    height += 8;
  }
  return height + 10;
}

export function renderGraph(
  doc: TopologyDocument,
  graph: TopologyGraph,
  options: RenderOptions = {},
): string {
  const layout = layoutGraph(graph);
  const branches = readBranches(graph, options);
  const { notes, flaggedNodes, flaggedEdges, fanOutMarker } = collectNotes(doc, graph, layout, branches);

  const width = Math.max(layout.width, 460);
  const notesH = notesHeight(notes, width);
  const height = TITLE_BLOCK_H + layout.height + notesH;
  const byId = new Map(layout.nodes.map((node) => [node.id, node]));

  const body: string[] = [];
  for (const edge of layout.edges) {
    body.push(drawEdge(edge, flaggedEdges.has(edge.id)));
  }
  for (const node of layout.nodes) {
    if (node.fanOut < 2) continue;
    const children = layout.edges
      .filter((edge) => edge.declared && edge.source === node.id && !edge.selfLoop && !edge.backEdge)
      .map((edge) => byId.get(edge.target))
      .filter((child): child is LayoutNode => Boolean(child));
    const branch = branches.get(node.id);
    if (branch !== undefined && branch.mode !== "unknown") {
      body.push(drawFanOutBracket(node, children, MODE_LABEL[branch.mode], "ink"));
    } else if (fanOutMarker !== undefined) {
      const label = branch?.mode === "unknown" ? `? note ${fanOutMarker}` : `? note ${fanOutMarker}`;
      body.push(drawFanOutBracket(node, children, label, "redline"));
    }
  }
  for (const node of layout.nodes) {
    body.push(drawNode(node, flaggedNodes.get(node.id)));
  }

  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${n2(width)}" height="${n2(height)}" viewBox="0 0 ${n2(width)} ${n2(height)}" role="img" aria-label="Topology of graph ${esc(graph.id)}">`,
    `<defs>`,
    `<marker id="arrow-ink" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9 z" fill="${theme.ink}"/></marker>`,
    `<marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9 z" fill="${theme.redline}"/></marker>`,
    `</defs>`,
    `<rect width="100%" height="100%" fill="${theme.paper}"/>`,
    titleBlock(doc, graph, width),
    `<g transform="translate(0 ${TITLE_BLOCK_H})">${body.join("")}</g>`,
    notesBlock(notes, width, TITLE_BLOCK_H + layout.height),
    `</svg>`,
  ].join("\n");
}

export function renderDocument(
  doc: TopologyDocument,
  options: RenderOptions = {},
): Array<{ graphId: string; svg: string }> {
  return doc.graphs.map((graph) => ({ graphId: graph.id, svg: renderGraph(doc, graph, options) }));
}
