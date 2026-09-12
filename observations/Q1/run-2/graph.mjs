import { Annotation, END, START, StateGraph } from "@langchain/langgraph";
import { describe } from "@agent-topology/langgraph";
import { canonicalStringify } from "@agent-topology/spec";

const State = Annotation.Root({ message: Annotation() });
const graph = new StateGraph(State)
  .addNode("greet", (state) => ({ message: `Hello, ${state.message}!` }))
  .addEdge(START, "greet")
  .addEdge("greet", END)
  .compile();

const document = await describe(graph);
console.log(canonicalStringify(document));
