/** X1 TypeScript builder: minimum compiled definitions; every user body fails. */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { Annotation, END, START, StateGraph } from "@langchain/langgraph";
import { describe } from "@agent-topology/langgraph";
import { canonicalStringify, computeStructureHash, derivedJoinEdges, validateDocument } from "@agent-topology/spec";

function forbidden(): never { throw new Error("X1_USER_BODY_EXECUTED"); }
const State = Annotation.Root({ value: Annotation<string>() });

function chain(runnable: unknown = forbidden) {
  const graph = new StateGraph(State);
  graph.addNode("child", runnable as typeof forbidden);
  graph.addEdge(START, "child");
  graph.addEdge("child", END);
  return graph.compile();
}

function build(caseName: string) {
  if (["opaque-child", "ordinary-node"].includes(caseName))
    return chain(caseName === "opaque-child" ? chain() : forbidden);
  const graph = new StateGraph(State);
  if (["direct-fanout", "conditional-router"].includes(caseName)) {
    for (const name of ["router", "a", "b"]) graph.addNode(name, forbidden);
    graph.addEdge(START, "router");
    if (caseName === "direct-fanout") {
      graph.addEdge("router", "a"); graph.addEdge("router", "b");
    } else graph.addConditionalEdges("router", forbidden, ["a", "b"]);
    graph.addEdge("a", END); graph.addEdge("b", END);
  } else if (caseName === "orphan-router") {
    graph.addNode("router", forbidden); graph.addNode("target", forbidden);
    graph.addEdge(START, "router");
    graph.addConditionalEdges("router", forbidden);
    graph.addEdge("target", END);
  } else if (["multi-source-join", "independent-edges"].includes(caseName)) {
    for (const name of ["a", "b", "joined"]) graph.addNode(name, forbidden);
    graph.addEdge(START, "a"); graph.addEdge(START, "b");
    if (caseName === "multi-source-join") graph.addEdge(["a", "b"], "joined");
    else { graph.addEdge("a", "joined"); graph.addEdge("b", "joined"); }
    graph.addEdge("joined", END);
  } else if (caseName === "sentinels") graph.addEdge(START, END);
  else throw new Error(caseName);
  return graph.compile();
}

const caseName = process.argv[2]!;
const graphId = caseName === "orphan-router" ? "custom-router" : "main";
const document = await describe(build(caseName), { graphId });
const validation = validateDocument(document);
if (!validation.valid) throw new Error(JSON.stringify(validation));
if (JSON.stringify(JSON.parse(canonicalStringify(document))) !== JSON.stringify(document))
  throw new Error("canonical round trip");
const computedHash = computeStructureHash(document);
if (JSON.stringify(computedHash) !== JSON.stringify(document.structureHash)) throw new Error("structure hash");
const packages = ["@agent-topology/langgraph", "@agent-topology/spec", "@langchain/langgraph"];
console.log(JSON.stringify({
  case: caseName,
  inputSha256: createHash("sha256").update(caseName).digest("hex"),
  identity: {
    runtime: process.version, executable: process.execPath, pid: process.pid,
    versions: Object.fromEntries(packages.map(name => [name,
      JSON.parse(readFileSync(new URL(`./node_modules/${name}/package.json`, import.meta.url), "utf8")).version])),
    imports: Object.fromEntries(packages.map(name => [name, import.meta.resolve(name)])),
  },
  document, computedHash,
  derivedJoinEdges: derivedJoinEdges(document.graphs[0].structure),
}));
