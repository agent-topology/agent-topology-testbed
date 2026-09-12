"""Validate A1 native records before comparing; normalize message UUIDs and wall times."""
import copy
import json
import sys
from pathlib import Path
from uuid import UUID
from datetime import datetime

from probe import EXPECTED, require


def validate(record):
    require(record["case_id"], "A1")
    require(record["evidence_class"], "execution")
    require(sorted(record["cases"]), sorted(EXPECTED))
    ids = []
    for key, case in record["cases"].items():
        model = key.split("-")[0]
        require([[m["source"], m["content"]] for m in case["messages"]], EXPECTED[key])
        require([m["type"] for m in case["messages"]], ["TextMessage"] * 3)
        require(case["model_calls"], {"alpha": 1, "beta": 1, "selector": 0}
                if model == "selector" else {"alpha": 1, "beta": 1})
        require(case["selector_calls"], [m[0] for m in EXPECTED[key][1:]] if model == "selector" else [])
        require(case["stop_reason"], "Maximum number of turns 2 reached."
                if model == "selector" else "Digraph execution is complete")
        for message in case["messages"]:
            require(UUID(message["id"]).version, 4)
            require(datetime.fromisoformat(message["created_at"]).utcoffset().total_seconds(), 0)
            ids.append(message["id"])
    require(len(set(ids)), 12)
    # Reconstruct only definitions to independently recheck static facts and hashes.
    import asyncio
    from probe import collect
    static = asyncio.run(collect(static_only=True))
    require(record["hashes"], static["hashes"])
    require(record["versions"], static["versions"])
    require(record["python"], static["python"])
    for key, case in record["cases"].items():
        require(case["static"], static["cases"][key]["static"])
    return ids


def normalize(record):
    result = copy.deepcopy(record)
    for case in result["cases"].values():
        for message in case["messages"]:
            del message["id"]
            del message["created_at"]
    return result


def compare(left, right):
    left_ids, right_ids = validate(left), validate(right)
    require(set(left_ids).isdisjoint(right_ids), True)
    require(normalize(left), normalize(right))


if __name__ == "__main__":
    compare(*(json.loads(Path(p).read_text()) for p in sys.argv[1:]))
    print("A1: four cases equal; 12 unique message UUIDs per run, disjoint across runs")
