async function main() {
  const { Annotation, END, START, StateGraph } = await import("@langchain/langgraph");
  const { describe } = await import("@agent-topology/langgraph");
  const { canonicalStringify } = await import("@agent-topology/spec");

  const State = Annotation.Root({ message: Annotation() });
  const graph = new StateGraph(State)
    .addNode("greet", (state) => ({ message: `Hello, ${state.message}!` }))
    .addEdge(START, "greet")
    .addEdge("greet", END)
    .compile();

  const document = await describe(graph);
  console.log(canonicalStringify(document));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
