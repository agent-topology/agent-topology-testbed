"""Literal ADR-0007 Action 4 model, NOT Cordboard code or a safety oracle.

Input must already pass core validation. Only immediate direct targets count.
No dynamic-interrupt declarations, extension interpretation or descendant walk.
"""


def evaluate(document, *, allow_parallel_interrupt=False):
    if type(allow_parallel_interrupt) is not bool:
        raise ValueError("override must be a boolean")
    matches = []
    for graph in document["graphs"]:
        structure = graph["structure"]
        nodes = {node["id"]: node for node in structure["nodes"]}
        outgoing = {}
        for edge in structure["edges"]:
            if edge["kind"] == "direct":
                outgoing.setdefault(edge["source"], []).append(edge)
        for source, edges in sorted(outgoing.items()):
            if len(edges) < 2:
                continue
            targets = [
                {"edgeId": edge["id"], "nodeId": edge["target"],
                 "interrupts": list(nodes[edge["target"]]["interrupts"])}
                for edge in sorted(edges, key=lambda edge: edge["id"])
                if nodes[edge["target"]].get("interrupts")
            ]
            if targets:
                matches.append({"graphId": graph["id"], "source": source,
                                "directEdgeIds": sorted(e["id"] for e in edges),
                                "interruptedTargets": targets})
    matches.sort(key=lambda item: (item["graphId"], item["source"]))
    matched = bool(matches)
    return {"rule": "R3", "matched": matched, "matches": matches,
            "override_requested": allow_parallel_interrupt,
            "override_applied": matched and allow_parallel_interrupt,
            "decision": "reject" if matched and not allow_parallel_interrupt else "not-rejected"}
