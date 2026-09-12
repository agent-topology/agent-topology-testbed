"""S1-asl: offline Amazon States Language (ASL) probe over small committed
JSON definitions, using only Python's standard-library `json` parser.

Answers one question: when the source document itself declares control-flow
meaning (state type, StartAt/Next/Default, branch/item-processor scope),
which of that meaning is representable by ordinary static inspection, and
which remains an open question this probe deliberately does not answer?

No AWS account, SDK, cloud request, third-party package, or deployment is
used or required. This probe:

  - parses JSON with the standard library only (`json.loads`);
  - performs its own bounded structural checks (state-type vocabulary,
    StartAt/Next/Default/Choice/Default reference resolution, scoped to the
    document/branch/item-processor namespace that declares them);
  - never evaluates a `Variable`/comparison expression, so it never decides
    which Choice rule an input would select;
  - never executes a state machine, invokes AWS Step Functions, or
    simulates scheduling, retry, or Catch/Retry failure handling.

Successful JSON parsing and these structural checks are evidence of exactly
that: parsing succeeded and the checks below held. They are not authoritative
ASL validation (AWS's own service performs additional checks this probe does
not implement) and not execution evidence (nothing here shows what a real
Step Functions execution would do). See docs/evidence.md's evidence-class
separation.

    python asl_probe.py --fixture choice --output out.json
"""
import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).with_name("fixtures")

# Retrieved 2026-09-11 (America/New_York). states-language.net publishes a
# living, unversioned spec with no dated revision tag; the retrieval date is
# recorded in its place, per the issue's "spec revision/retrieval date"
# requirement.
SPEC = {
    "source_url": "https://states-language.net/spec.html",
    "retrieved": "2026-09-11",
    "revision_note": (
        "states-language.net carries no dated revision tag as of retrieval; "
        "the retrieval date stands in for a spec revision identifier."
    ),
}

KNOWN_STATE_TYPES = {"Pass", "Task", "Choice", "Wait", "Succeed", "Fail", "Parallel", "Map"}
# Succeed/Fail are always terminal by the state's own type; they carry
# neither End nor Next per the spec (states-language.net#terminal-states).
ALWAYS_TERMINAL_TYPES = {"Succeed", "Fail"}


class ASLStructureError(ValueError):
    """A state's own shape does not match the ASL vocabulary this probe checks."""


class ASLReferenceError(ValueError):
    """A StartAt/Next/Default/Choice target does not resolve inside its own scope."""


def _require(condition, message, exc_cls=ASLStructureError):
    if not condition:
        raise exc_cls(message)


def extract_scope(states, start_at, scope_id, collected):
    """Validate and record one State Machine-shaped scope (the top-level
    document, a Parallel branch, or a Map ItemProcessor/Iterator), without
    looking outside `states` for any reference. A branch or item processor is
    validated against only its own `states` dict, so a Next/Default/StartAt
    that names something defined only in an ancestor scope fails to resolve
    right here -- this is the whole mechanism that catches a cross-boundary
    reference; no separate cross-scope pass is needed.
    """
    _require(isinstance(states, dict) and states, f"scope {scope_id!r}: States must be a non-empty object")
    _require(start_at in states, f"scope {scope_id!r}: StartAt {start_at!r} is not defined in this scope")

    state_types = {}
    terminal_states = []
    next_edges = {}
    choice_rules = {}
    map_config = {}
    parallel_branch_counts = {}

    for name, state in states.items():
        state_type = state.get("Type")
        _require(
            state_type in KNOWN_STATE_TYPES,
            f"scope {scope_id!r}: state {name!r} has unknown Type {state_type!r}",
        )
        state_types[name] = state_type

        end = state.get("End", False)
        nxt = state.get("Next")

        if state_type in ALWAYS_TERMINAL_TYPES:
            _require(nxt is None and not end, f"scope {scope_id!r}: state {name!r} ({state_type}) must not declare Next/End")
            terminal_states.append(name)
        elif state_type == "Choice":
            _require(nxt is None, f"scope {scope_id!r}: Choice state {name!r} must not declare Next directly")
            choices = state.get("Choices")
            _require(isinstance(choices, list) and choices, f"scope {scope_id!r}: Choice state {name!r} needs a non-empty Choices list")
            # Order is the ordered-rule-selection evidence itself: ASL
            # evaluates Choices in list order and takes the first match, so
            # this list is kept exactly as declared, never sorted.
            ordered_targets = []
            for index, rule in enumerate(choices):
                target = rule.get("Next")
                _require(target is not None, f"scope {scope_id!r}: Choice state {name!r} rule {index} has no Next")
                _require(
                    target in states,
                    f"scope {scope_id!r}: state {name!r} rule {index} references unknown target {target!r}",
                    ASLReferenceError,
                )
                ordered_targets.append(target)
            default = state.get("Default")
            if default is not None:
                _require(
                    default in states,
                    f"scope {scope_id!r}: state {name!r} Default references unknown target {default!r}",
                    ASLReferenceError,
                )
            # Default is a distinct fallback slot, not one more ordered rule:
            # it is only reached when every Choices rule above it failed to
            # match, so it is recorded separately rather than appended.
            choice_rules[name] = {"ordered_targets": ordered_targets, "default": default}
        else:
            if end:
                _require(nxt is None, f"scope {scope_id!r}: state {name!r} declares both End and Next")
                terminal_states.append(name)
            else:
                _require(nxt is not None, f"scope {scope_id!r}: state {name!r} must declare exactly one of End or Next")
                _require(
                    nxt in states,
                    f"scope {scope_id!r}: state {name!r} references unknown target {nxt!r}",
                    ASLReferenceError,
                )
                next_edges[name] = nxt

        if state_type == "Parallel":
            branches = state.get("Branches")
            _require(isinstance(branches, list) and branches, f"scope {scope_id!r}: Parallel state {name!r} needs a non-empty Branches list")
            # Branch count is declared fan-out: every branch is enumerated
            # and, per ASL semantics, the Parallel state runs all of them --
            # this is not a selection among alternatives the way a Choice
            # state's rules are.
            parallel_branch_counts[name] = len(branches)
            for index, branch in enumerate(branches):
                child_id = f"{scope_id}/{name}/branch{index}"
                extract_scope(branch.get("States", {}), branch.get("StartAt"), child_id, collected)
        elif state_type == "Map":
            processor = state.get("ItemProcessor") or state.get("Iterator")
            _require(processor is not None, f"scope {scope_id!r}: Map state {name!r} needs ItemProcessor or Iterator")
            mode = (processor.get("ProcessorConfig") or {}).get("Mode", "INLINE")
            # ItemsPath names where the runtime array lives; this probe never
            # reads or infers its length from the template -- cardinality is
            # execution evidence this probe does not produce. MaxConcurrency
            # is recorded on the same line specifically so the two axes sit
            # next to each other as distinct facts, never merged.
            map_config[name] = {
                "items_path": state.get("ItemsPath"),
                "max_concurrency": state.get("MaxConcurrency"),
                "mode": mode,
                "array_length_known": False,
            }
            child_id = f"{scope_id}/{name}/item_processor"
            extract_scope(processor.get("States", {}), processor.get("StartAt"), child_id, collected)

    collected.append({
        "scope_id": scope_id,
        "start_at": start_at,
        "state_names": sorted(states),
        "state_types": state_types,
        "terminal_states": sorted(terminal_states),
        "next_edges": next_edges,
        "choice_rules": choice_rules,
        "map_config": map_config,
        "parallel_branch_counts": parallel_branch_counts,
    })


def load_fixture(fixture_path):
    return json.loads(fixture_path.read_text())


def build_scopes(document):
    _require(isinstance(document, dict) and "StartAt" in document and "States" in document,
             "top-level document needs StartAt and States")
    scopes = []
    extract_scope(document["States"], document["StartAt"], "root", scopes)
    # Depth-first append puts children before their parent; sort by scope_id
    # for a stable, comparable order across runs.
    scopes.sort(key=lambda scope: scope["scope_id"])
    return scopes


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"observation mismatch: {actual!r} != {expected!r}")


# Independent literal expectations, written from the fixtures above and the
# states-language.net spec before this module's extraction logic ran against
# them -- not values copied back out of a prior run's output.
EXPECTED_FACTS = {
    "choice": [
        {
            "scope_id": "root",
            "start_at": "CheckStatus",
            "state_names": ["Approved", "CheckStatus", "Pending", "Rejected"],
            "state_types": {"Approved": "Pass", "CheckStatus": "Choice", "Pending": "Pass", "Rejected": "Pass"},
            "terminal_states": ["Approved", "Pending", "Rejected"],
            "next_edges": {},
            "choice_rules": {"CheckStatus": {"ordered_targets": ["Approved", "Rejected"], "default": "Pending"}},
            "map_config": {},
            "parallel_branch_counts": {},
        },
    ],
    "parallel": [
        {
            "scope_id": "root",
            "start_at": "RunBoth",
            "state_names": ["Converge", "RunBoth"],
            "state_types": {"Converge": "Pass", "RunBoth": "Parallel"},
            "terminal_states": ["Converge"],
            "next_edges": {"RunBoth": "Converge"},
            "choice_rules": {},
            "map_config": {},
            "parallel_branch_counts": {"RunBoth": 2},
        },
        {
            "scope_id": "root/RunBoth/branch0",
            "start_at": "Step",
            "state_names": ["Step"],
            "state_types": {"Step": "Pass"},
            "terminal_states": ["Step"],
            "next_edges": {},
            "choice_rules": {},
            "map_config": {},
            "parallel_branch_counts": {},
        },
        {
            "scope_id": "root/RunBoth/branch1",
            "start_at": "Step",
            "state_names": ["Step"],
            "state_types": {"Step": "Pass"},
            "terminal_states": ["Step"],
            "next_edges": {},
            "choice_rules": {},
            "map_config": {},
            "parallel_branch_counts": {},
        },
    ],
    "map": [
        {
            "scope_id": "root",
            "start_at": "ProcessItems",
            "state_names": ["ProcessItems"],
            "state_types": {"ProcessItems": "Map"},
            "terminal_states": ["ProcessItems"],
            "next_edges": {},
            "choice_rules": {},
            "map_config": {
                "ProcessItems": {
                    "items_path": "$.items",
                    "max_concurrency": 1,
                    "mode": "INLINE",
                    "array_length_known": False,
                },
            },
            "parallel_branch_counts": {},
        },
        {
            "scope_id": "root/ProcessItems/item_processor",
            "start_at": "HandleItem",
            "state_names": ["HandleItem"],
            "state_types": {"HandleItem": "Pass"},
            "terminal_states": ["HandleItem"],
            "next_edges": {},
            "choice_rules": {},
            "map_config": {},
            "parallel_branch_counts": {},
        },
    ],
}

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fixture", required=True,
                         choices=sorted(p.stem for p in FIXTURES_DIR.glob("*.json")))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    _require(sys.version_info >= (3, 8), f"unsupported Python version {platform.python_version()}")

    fixture_path = FIXTURES_DIR / f"{args.fixture}.json"
    source_path = Path(__file__).resolve()
    document = load_fixture(fixture_path)

    scopes = build_scopes(document)
    if args.fixture in EXPECTED_FACTS:
        require_equal(scopes, EXPECTED_FACTS[args.fixture])

    record = {
        "case_id": f"S1-asl-{args.fixture}",
        "fixture": fixture_path.name,
        "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "spec": SPEC,
        "evidence_class": "static",
        "json_parsed": True,
        "scopes": scopes,
        "probe_disclaimer": (
            "Successful JSON parsing and this probe's own bounded structural "
            "checks (state-type vocabulary, scoped StartAt/Next/Default/Choice "
            "reference resolution) are not authoritative ASL validation and "
            "not AWS Step Functions execution evidence. No expression "
            "evaluator, simulator, or cloud request is implemented."
        ),
    }
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
