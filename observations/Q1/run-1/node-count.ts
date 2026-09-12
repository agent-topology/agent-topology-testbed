import type { TopologyDocument } from "@agent-topology/spec";

function nodeCount(document: TopologyDocument): number {
  return document.graphs.reduce(
    (total, graph) => total + graph.structure.nodes.length,
    0,
  );
}
