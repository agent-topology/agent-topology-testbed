"""A1: public configuration inspection and bounded, local replay execution."""
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow, SelectorGroupChat
from autogen_ext.models.replay import ReplayChatCompletionClient

ROOT = Path(__file__).resolve().parent
EXPECTED = json.loads((ROOT / "expected.json").read_text())


def require(actual, expected):
    if actual != expected:
        raise ValueError(f"Expected {repr(expected)[:500]}, got {repr(actual)[:500]}")


def build(model):
    clients = {name: ReplayChatCompletionClient([name + "-reply"])
               for name in ("alpha", "beta")}
    agents = [AssistantAgent(name, model_client=client)
              for name, client in clients.items()]
    selections = []

    def selector(messages):
        task = messages[0].content
        require(task in ("forward", "reverse"), True)
        if messages[-1].source == "user":
            chosen = "alpha" if task == "forward" else "beta"
        else:
            chosen = "beta" if messages[-1].source == "alpha" else "alpha"
        selections.append(chosen)
        return chosen

    graph = None
    if model == "selector":
        # Empty replay fails if the custom selector ever falls back to a model.
        clients["selector"] = ReplayChatCompletionClient([])
        team = SelectorGroupChat(agents, model_client=clients["selector"],
                                 selector_func=selector, max_turns=2)
    else:
        builder = DiGraphBuilder()
        for agent in agents:
            builder.add_node(agent)
        builder.add_edge(agents[0], agents[1])
        graph = builder.build()
        team = GraphFlow(agents, graph=graph, max_turns=2)
    return team, graph, clients, selections


def inspect_static(team, graph, clients, selections):
    config = team.dump_component().model_dump(mode="json")
    facts = {"component": config,
             "participants": [p["config"]["name"] for p in config["config"]["participants"]],
             "model_calls": {k: len(v.create_calls) for k, v in clients.items()},
             "selector_calls": list(selections)}
    require(facts["participants"], ["alpha", "beta"])
    require(list(facts["model_calls"].values()), [0] * len(clients))
    require(selections, [])
    require(config["config"]["max_turns"], 2)
    if graph is not None:
        facts["graph"] = graph.model_dump(mode="json")
        facts["roots"] = sorted(graph.get_start_nodes())
        facts["leaves"] = sorted(graph.get_leaf_nodes())
        facts["edges"] = sorted([name, edge.target] for name, node in graph.nodes.items()
                                for edge in node.edges)
        require(sorted(graph.nodes), ["alpha", "beta"])
        require(facts["edges"], [["alpha", "beta"]])
        require(facts["roots"], ["alpha"])
        require(facts["leaves"], ["beta"])
        require(config["config"]["graph"], graph.model_dump(mode="json", exclude_none=True))
    else:
        require("graph" in config["config"], False)
        require("selector_func" in config["config"], False)
    return facts


async def collect(static_only=False):
    require(platform.python_version(), "3.11.16")
    versions = {p: importlib.metadata.version(p)
                for p in ("autogen-agentchat", "autogen-core", "autogen-ext")}
    require(list(versions.values()), ["0.7.5"] * 3)
    record = {"case_id": "A1", "evidence_class": "static" if static_only else "execution",
              "python": platform.python_version(), "versions": versions,
              "hashes": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                         for name in ("probe.py", "verify.py", "test_probe.py", "expected.json",
                                      "requirements.txt", "requirements.lock", ".python-version")},
              "cases": {}}
    for key in EXPECTED:
        model, task = key.split("-")
        team, graph, clients, selections = build(model)
        try:
            case = {"static": inspect_static(team, graph, clients, selections)}
            if not static_only:
                result = await asyncio.wait_for(team.run(task=task), timeout=15)
                case["messages"] = [m.model_dump(mode="json") for m in result.messages]
                case["stop_reason"] = result.stop_reason
                case["selector_calls"] = list(selections)
                case["model_calls"] = {k: len(v.create_calls) for k, v in clients.items()}
                require([[m.source, m.content] for m in result.messages], EXPECTED[key])
                require([m.type for m in result.messages], ["TextMessage"] * 3)
                require(case["model_calls"], {"alpha": 1, "beta": 1, "selector": 0}
                        if model == "selector" else {"alpha": 1, "beta": 1})
                require(selections, [m[0] for m in EXPECTED[key][1:]] if model == "selector" else [])
                require(result.stop_reason, "Maximum number of turns 2 reached."
                        if model == "selector" else "Digraph execution is complete")
            record["cases"][key] = case
        finally:
            for client in clients.values():
                await client.close()
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = asyncio.run(collect(args.static_only))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"A1 {record['evidence_class']}: four cases passed")


if __name__ == "__main__":
    main()
