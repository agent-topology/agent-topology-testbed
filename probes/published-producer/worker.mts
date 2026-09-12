import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { Annotation, StateGraph } from "@langchain/langgraph";
import { describe } from "@agent-topology/langgraph";
import { canonicalStringify, computeStructureHash, validateDocument } from "@agent-topology/spec";

type Recipe = {
  nodes: string[]; edges: [string, string][]; joins: [string[], string][];
  callable: string; metadata: Record<string, unknown>;
};

function fail(): never { throw new Error("D1_NODE_BODY_EXECUTED"); }
function namedStep(state: unknown): never { return fail(); }

function build(recipe: Recipe) {
  const state = Annotation.Root({ value: Annotation<string>() });
  const graph = new StateGraph(state);
  for (const node of recipe.nodes) {
    const body = recipe.callable === "named" ? namedStep : (state: unknown) => fail();
    graph.addNode(node, body, { metadata: recipe.metadata });
  }
  for (const [source, target] of recipe.edges) graph.addEdge(source, target);
  for (const [sources, target] of recipe.joins) graph.addEdge(sources, target);
  return graph.compile({ name: "d1" });
}

const raw = readFileSync(process.argv[2]);
const compiled = build(JSON.parse(raw.toString()) as Recipe);
// D1_UNRELATED_COMMENT
const documents = [];
for (let i = 0; i < 2; i++) {
  const document = await describe(compiled);
  const validation = validateDocument(document);
  if (!validation.valid) throw new Error(JSON.stringify(validation));
  documents.push({ document, canonical: canonicalStringify(document),
                   computedHash: computeStructureHash(document) });
}
const packages = ["@agent-topology/langgraph", "@agent-topology/spec", "@langchain/langgraph"];
console.log(JSON.stringify({
  inputSha256: createHash("sha256").update(raw).digest("hex"),
  identity: { runtime: process.version, executable: process.execPath, pid: process.pid,
    versions: Object.fromEntries(packages.map(name => [name,
      JSON.parse(readFileSync(new URL(`./node_modules/${name}/package.json`, import.meta.url), "utf8")).version])),
    imports: Object.fromEntries(packages.map(name => [name, import.meta.resolve(name)])) },
  describes: documents,
}));
