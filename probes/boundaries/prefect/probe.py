"""Public definition inspection followed by bounded local framework execution."""
import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path
import platform
import tempfile
import time
from uuid import UUID

HERE = Path(__file__).resolve().parent


def require(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, got {actual!r}")


def inspect_definitions(fixtures):
    flows = [fixtures.linear, fixtures.loop]
    tasks = [fixtures.task_a, fixtures.task_b]
    return {
        "flow_names": [f.name for f in flows],
        "task_names": [t.name for t in tasks],
        "bodies_entered": list(fixtures.BODIES_ENTERED),
        "flows": [{"name": f.name, "version": f.version,
                   "python_entrypoint": f"{f.fn.__module__}:{f.fn.__qualname__}",
                   "signature": str(inspect.signature(f.fn)),
                   "parameters": f.parameters.model_dump(mode="json")} for f in flows],
        "tasks": [{"name": t.name, "version": t.version, "task_key": t.task_key,
                   "python_entrypoint": f"{t.fn.__module__}:{t.fn.__qualname__}",
                   "signature": str(inspect.signature(t.fn))} for t in tasks],
    }


def collect(client, flow_id, expected_count):
    from prefect.client.schemas.filters import FlowRunFilter, FlowRunFilterId
    # Task-state persistence is asynchronous. Wait for terminal records, then
    # check the exact independent count and history; never trim extra records.
    deadline = time.monotonic() + 30
    while True:
        runs = client.read_task_runs(
            flow_run_filter=FlowRunFilter(id=FlowRunFilterId(any_=[flow_id])))
        histories = {str(r.id): client.read_task_run_states(r.id) for r in runs}
        if len(runs) >= expected_count and all(
            r.state_type.value == "COMPLETED" and len(histories[str(r.id)]) >= 3
            for r in runs
        ):
            break
        if time.monotonic() >= deadline:
            raise TimeoutError("Task records/history did not settle within 30 seconds")
        time.sleep(0.2)
    runs.sort(key=lambda r: r.start_time)
    return runs, histories


def observe_case(client, fixtures, fn, args, expected):
    fixtures.BODIES_ENTERED.clear()
    state = fn(*args, return_state=True)
    require(state.type.value, "COMPLETED", "flow state")
    flow_id = state.state_details.flow_run_id
    runs, histories = collect(client, flow_id, len(expected["task_names"]))
    ids = [str(r.id) for r in runs]
    require(len(set(ids)), len(ids), "unique task run UUIDs")
    names = {fixtures.task_a.task_key: fixtures.task_a.name,
             fixtures.task_b.task_key: fixtures.task_b.name}
    dynamic_keys = [r.dynamic_key for r in runs]
    for key in dynamic_keys:
        require(UUID(key).version, 4, "generated dynamic key UUID version")
    require(len(set(dynamic_keys)), len(dynamic_keys), "unique dynamic keys")
    dependencies = []
    for index, run in enumerate(runs):
        require(str(run.flow_run_id), str(flow_id), "owning flow")
        for port, inputs in sorted(run.task_inputs.items()):
            for item in inputs:
                require(item.input_type, "task_run", "dependency input kind")
                dependencies.append([ids.index(str(item.id)), index, port])
    observed = {
        "result": state.result(), "body_order": list(fixtures.BODIES_ENTERED),
        "task_names": [names[r.task_key] for r in runs],
        "dependencies": sorted(dependencies),
    }
    require(observed, expected, "case structure and values")
    semantic_runs = []
    raw_runs = []
    timeline = []
    for index, run in enumerate(runs):
        history = sorted(histories[str(run.id)], key=lambda s: s.timestamp)
        states = [s.type.value for s in history]
        semantic_runs.append({"task_key": run.task_key, "dynamic_key_kind": "generated UUID4",
                              "task_version": run.task_version,
                              "run_count": run.run_count, "states": states})
        for s in history:
            timeline.append((s.timestamp, index, s.type.value))
        raw_runs.append({"task_run": run.model_dump(mode="json"),
                         "states": [s.model_dump(mode="json") for s in history]})
    # Retain event ordering, with timestamps only in raw evidence. These ordinals
    # are comparison-local references, never proposed persistent graph IDs.
    observed["state_order"] = [[i, kind] for _, i, kind in sorted(timeline)]
    observed["task_runs"] = semantic_runs
    observed["flow_state"] = state.type.value
    return observed, {"flow_run_id": str(flow_id), "task_runs": raw_runs}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected", type=Path, default=HERE / "expected.json")
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    expected = json.loads(args.expected.read_text())
    require(platform.python_version(), "3.11.16", "Python pin")
    # Set before importing Prefect: no ambient profiles, API URL/key or persistent
    # home. The harness owns its temporary database and subprocess server.
    with tempfile.TemporaryDirectory(prefix="p8-home-") as home:
        for key in list(os.environ):
            if key.startswith("PREFECT_"):
                del os.environ[key]
        os.environ.update(PREFECT_HOME=home, PREFECT_PROFILES_PATH=home + "/profiles.toml",
                          PREFECT_SERVER_ANALYTICS_ENABLED="false",
                          PREFECT_LOGGING_LEVEL="WARNING")
        import prefect
        import fixtures
        from prefect.client.orchestration import get_client
        from prefect.testing.utilities import prefect_test_harness
        require(prefect.__version__, "3.6.22", "Prefect pin")
        static = inspect_definitions(fixtures)
        for key, value in expected["static"].items():
            require(static[key], value, "static " + key)
        record = {"case_id": "P8", "python": platform.python_version(),
                  "prefect": prefect.__version__, "static": static,
                  "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(HERE.iterdir())
                             if p.is_file() and p.suffix in {".py", ".json", ".lock", ".txt"}},
                  "execution": {}}
        raw = {}
        if not args.static_only:
            error = None
            with prefect_test_harness():
                # Let the harness finish its normal shutdown even on validation
                # failure (this SDK's post-yield shutdown is not in a finally).
                try:
                    with get_client(sync_client=True) as client:
                        for name, fn, inputs in [("linear", fixtures.linear, ()),
                                                 ("loop-0", fixtures.loop, (0,)),
                                                 ("loop-2", fixtures.loop, (2,))]:
                            result, native = observe_case(client, fixtures, fn, inputs,
                                                          expected["cases"][name])
                            for run in result["task_runs"]:
                                require(run["states"], expected["task_states"], "state history")
                                require(run["run_count"], 1, "no retries")
                            record["execution"][name], raw[name] = result, native
                except BaseException as exc:
                    error = exc
            if error is not None:
                raise error
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        if not args.static_only:
            args.output.with_suffix(".raw.json").write_text(
                json.dumps(raw, indent=2, sort_keys=True) + "\n")
        print(f"PASS P8 {'static' if args.static_only else 'static + linear + loop-0 + loop-2'}")


if __name__ == "__main__":
    main()
