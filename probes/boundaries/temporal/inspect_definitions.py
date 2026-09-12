"""Inspect T1 without calling workflow/activity bodies or private SDK accessors."""

import argparse
from dataclasses import fields
import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import platform

from temporalio import activity, workflow
from temporalio.worker import Worker

import fixtures


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"Observation mismatch:\nactual={actual!r}\nexpected={expected!r}")


def extract(workflows, activities):
    """Python metadata from supplied definitions, not a Temporal graph export.

    `run` is explicitly selected by this fixture, not discovered via SDK internals.
    Registration parameters are inspected, but no Worker or Client is constructed.
    """
    return {
        "activities": sorted([
            {"python_name": fn.__name__, "signature": str(inspect.signature(fn)),
             "async": inspect.iscoroutinefunction(fn)}
            for fn in activities
        ], key=lambda item: item["python_name"]),
        "workflows": sorted([
            {"python_name": cls.__name__, "run_signature": str(inspect.signature(cls.run)),
             "async": inspect.iscoroutinefunction(cls.run)}
            for cls in workflows
        ], key=lambda item: item["python_name"]),
        "bodies_entered": list(fixtures.BODIES_ENTERED),
        "registration_parameter_names": sorted(
            name for name in inspect.signature(Worker).parameters
            if name in ("workflows", "activities")
        ),
        "context": {"in_activity": activity.in_activity(), "in_workflow": workflow.in_workflow()},
        # Public dataclass schemas only: these are field names, NOT runtime values.
        "runtime_identity_field_names": {
            "activity": sorted(field.name for field in fields(activity.Info)
                               if field.name in ("activity_id", "activity_type", "workflow_id",
                                                 "workflow_run_id", "workflow_type")),
            "workflow": sorted(field.name for field in fields(workflow.Info)
                               if field.name in ("run_id", "workflow_id", "workflow_type")),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("expected.json"))
    args = parser.parse_args()
    require_equal(platform.python_version(), "3.11.16")
    require_equal(importlib.metadata.version("temporalio"), "1.18.0")
    expected = json.loads(args.expected.read_text())
    observed = extract([fixtures.LinearWorkflow, fixtures.ChoiceWorkflow],
                       [fixtures.activity_a, fixtures.activity_b])
    require_equal(observed, expected)
    root = Path(__file__).resolve().parent
    record = {
        "case_id": "T1-temporal-definitions",
        "evidence_class": "static",
        "question": "What can public definition inspection distinguish between linear and input-dependent workflow code?",
        "minimal_input": {"workflow_definitions": 2, "activity_definitions": 2,
                          "execution_inputs_supplied": [], "worker_constructed": False},
        "framework": "temporalio", "version": "1.18.0", "python": platform.python_version(),
        "source_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                          for name in ("fixtures.py", "inspect_definitions.py", "expected.json")},
        "lock_sha256": hashlib.sha256((root / "requirements.lock").read_bytes()).hexdigest(),
        "sdk_source_sha256": {name: hashlib.sha256(Path(inspect.getfile(module)).read_bytes()).hexdigest()
                              for name, module in (("workflow.py", workflow), ("activity.py", activity))},
        "assertions": "exact equality with independently written expected.json; explicit exception under -O",
        "observed": observed,
        "limitations": [
            "Python names/signatures are not extracted Temporal type names or invocation node IDs.",
            "The run method and definition lists are fixture inputs, not an SDK discovery result.",
            "No private definition accessor, graph inference, callable evaluation, or Temporal execution.",
            "No topology-export capability found in the documented surface reviewed in T1 README; not a universal absence proof.",
        ],
    }
    # Write only after successful checks. Callers must still check exit status.
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
