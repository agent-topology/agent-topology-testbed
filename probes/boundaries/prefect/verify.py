"""Validate evidence and compare semantics without treating UUIDs as graph IDs."""
import argparse
import hashlib
import json
from pathlib import Path
from uuid import UUID

from probe import HERE, require


def validate(record, raw, expected):
    require(record["prefect"], "3.6.22", "Prefect")
    require(record["python"], "3.11.16", "Python")
    for name, digest in record["sha256"].items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest(), digest, name)
    for key, value in expected["static"].items():
        require(record["static"][key], value, key)
    task_names = {t["task_key"]: t["name"] for t in record["static"]["tasks"]}
    all_ids = []
    for case, exp in expected["cases"].items():
        observation = record["execution"][case]
        require({k: observation[k] for k in exp}, exp, case)
        require(observation["flow_state"], "COMPLETED", "flow completion")
        rows = raw[case]["task_runs"]
        require(len(rows), len(exp["task_names"]), "native invocation count")
        require(len(observation["task_runs"]), len(rows), "semantic invocation count")
        ids = [r["task_run"]["id"] for r in rows]
        all_ids.extend([raw[case]["flow_run_id"], *ids])
        dynamic_keys = [r["task_run"]["dynamic_key"] for r in rows]
        all_ids.extend(dynamic_keys)
        for key in dynamic_keys:
            require(UUID(key).version, 4, "dynamic UUID4")
        deps, timeline = [], []
        for index, row in enumerate(rows):
            run = row["task_run"]
            require(run["flow_run_id"], raw[case]["flow_run_id"], "native owner")
            require(task_names[run["task_key"]], exp["task_names"][index], "native task")
            semantic = observation["task_runs"][index]
            require(semantic, {"task_key": run["task_key"],
                               "task_version": "p8-v1", "run_count": 1,
                               "dynamic_key_kind": "generated UUID4",
                               "states": expected["task_states"]}, "semantic task")
            require(run["run_count"], 1, "native retry count")
            require(run["task_version"], "p8-v1", "native version")
            require(run["state_type"], "COMPLETED", "native final state")
            require([s["type"] for s in row["states"]], expected["task_states"], "native states")
            for state in row["states"]:
                require(state["state_details"]["task_run_id"], run["id"], "state owner")
                timeline.append((state["timestamp"], index, state["type"]))
            for port, inputs in run["task_inputs"].items():
                for item in inputs:
                    require(item["input_type"], "task_run", "native dependency kind")
                    deps.append([ids.index(item["id"]), index, port])
        require(sorted(deps), exp["dependencies"], "native dependencies")
        event_order = [[i, kind] for _, i, kind in sorted(timeline)]
        require(observation["state_order"], event_order, "preserve native event order")
        require(event_order, [[i, state] for i in range(len(rows))
                              for state in expected["task_states"]], "sequential lifecycle order")
    require(len(set(all_ids)), len(all_ids), "distinct native UUID identities")
    return set(all_ids)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs=2, type=Path)
    args = parser.parse_args()
    expected = json.loads((HERE / "expected.json").read_text())
    records, identities = [], []
    for path in args.records:
        record = json.loads(path.read_text())
        raw = json.loads(path.with_suffix(".raw.json").read_text())
        identities.append(validate(record, raw, expected))
        records.append(record)
    require(records[0], records[1], "two fresh-process semantic records")
    require(bool(identities[0] & identities[1]), False, "run UUIDs differ across processes")
    print("PASS P8: native identities/dependencies/order, hashes, expectations, two-run comparison")


if __name__ == "__main__":
    main()
