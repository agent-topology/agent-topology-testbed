from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from agent_topology.langgraph import describe
from agent_topology.spec import canonical_json


class State(TypedDict):
    message: str


def greet(state: State) -> dict[str, str]:
    return {"message": f"Hello, {state['message']}!"}


builder = StateGraph(State)
builder.add_node("greet", greet)
builder.add_edge(START, "greet")
builder.add_edge("greet", END)
graph = builder.compile()

if __name__ == "__main__":
    print(canonical_json(describe(graph)))
