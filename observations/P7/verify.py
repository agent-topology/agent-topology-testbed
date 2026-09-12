"""Audit P7's saved inputs without installing or executing any framework.

This checks recorded assertions and provenance, not their historical authoring
order or a new producer-to-consumer acceptance run. Run from any directory.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
BASE = "c528746b7826e1507a3c9732e54b4a48efe8cf89"
HISTORY = "571e881e6d509b6e26ff8bf14b98e207d12e7ce9"
COUNTS = dict(zip("P0 P1 P2 P3 P4 P5 P6 C1 S1 T1".split(),
                  [4, 9, 6, 2, 2, 6, 6, 18, 3, 1]))
SOURCES = {"P1": "airflow/branch.py", "P2": "dagster/conditional.py",
           "P3": "airflow/grouping.py", "P4": "dagster/nested.py",
           "P5": "airflow/mapped.py", "P6": "dagster/dynamic.py",
           "C1": "crewai/flow_probe.py", "S1": "step-functions/asl_probe.py"}
KNOWN_SOURCE_LIMITS = {
    "P3": "3b27f1f95ae0a72f1394f9ab17ff0235ef349bd8231a21c76eec6e4527ed09af",
    "P6": "c8d8ecb452d1a1471da068b845377af18fbe57ecee5761fab5d4b1d1fd7dd92f",
}


def require(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: mismatch")


def read(path):
    return json.loads((ROOT / path).read_text())


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def literals(path):
    result = {}
    for node in ast.parse((ROOT / path).read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("EXPECTED_"):
                    result[target.id] = ast.literal_eval(node.value)
    return result


def cohort():
    sections, limits = 0, {}
    for group, count in COUNTS.items():
        pairs = sorted((ROOT / "observations" / group).glob("*-1.json"))
        require(len(pairs), count, group)
        for first in pairs:
            require(first.read_bytes(), first.with_name(first.name[:-6] + "2.json").read_bytes(), first.name)
            record = json.loads(first.read_text())
            if group == "T1":
                directory = Path("probes/boundaries/temporal")
                require(record["observed"], read(directory / "expected.json"), "T1 literals")
                for name, value in record["source_sha256"].items():
                    require(digest(directory / name), value, name)
                require(digest(directory / "requirements.lock"), record["lock_sha256"], "T1 lock")
                sections += 1
                continue
            source = "probes/" + (first.name.split("-")[0] + "/smoke.py" if group == "P0" else SOURCES[group])
            if group in KNOWN_SOURCE_LIMITS:
                require(record["source_sha256"], KNOWN_SOURCE_LIMITS[group], group + " recorded source")
                limits[group] = {"recorded": record["source_sha256"], "current": digest(source)}
            else:
                require(record["source_sha256"], digest(source), source)
            expected = literals(source)
            if group == "S1":
                require(digest(Path(source).parent / "fixtures" / record["fixture"]), record["fixture_sha256"], "ASL fixture")
                facts = expected["EXPECTED_FACTS"][first.name.split("-")[0]]
                require(record["scopes"], facts, "ASL assertions")
                sections += 1
                continue
            require(digest(Path(source).parent / "requirements.lock"), record["lock_sha256"], "lock")
            for mode in ("static", "callable", "execution"):
                if mode not in record:
                    continue
                value = expected["EXPECTED_" + mode.upper()]
                if group == "C1":
                    case = record["case_id"].removeprefix("C1-crewai-flow-probe-")
                    value = value[case.split("-")[0] if mode == "static" else case]
                elif group in {"P1", "P2", "P5", "P6"} and mode != "static":
                    value = value[record["case_id"].split("-")[-1]]
                require(record[mode], value, first.name + " " + mode)
                sections += 1
    require(sections, 85, "cohort measured sections")
    return {"pairs": sum(COUNTS.values()), "run_1_asserted_sections": sections,
            "unresolved_source_provenance": limits}


def autogen():
    static = read("observations/A1/static.json")
    expected = read("probes/boundaries/autogen/expected.json")
    normalized, identity_sets = [], []
    for name in ("static.json", "run-1.json", "run-2.json"):
        record = read("observations/A1/" + name)
        require(record["versions"], {"autogen-" + p: "0.7.5" for p in ("agentchat", "core", "ext")}, "A1 versions")
        require(record["python"], "3.11.16", "A1 Python")
        require(set(record["cases"]), set(expected), "A1 cases")
        for path, value in record["hashes"].items():
            require(digest("probes/boundaries/autogen/" + path), value, path)
        ids = []
        result = copy.deepcopy(record)
        for key, case in record["cases"].items():
            facts = case["static"]
            require(facts, static["cases"][key]["static"], key + " saved static")
            require(facts["participants"], ["alpha", "beta"], "participants")
            require(set(facts["model_calls"].values()), {0}, "no static model calls")
            require(facts["selector_calls"], [], "no static selector")
            config = facts["component"]["config"]
            if key.startswith("graph"):
                require(facts["edges"], [["alpha", "beta"]], "declared edge")
                require(facts["roots"], ["alpha"], "root")
                require(facts["leaves"], ["beta"], "leaf")
            else:
                require("graph" in config or "selector_func" in config, False, "selector omissions")
            if name == "static.json":
                continue
            require([[m["source"], m["content"]] for m in case["messages"]], expected[key], "message oracle")
            require([m["type"] for m in case["messages"]], ["TextMessage"] * 3, "message types")
            selector = key.startswith("selector")
            require(case["selector_calls"], [m[0] for m in expected[key][1:]] if selector else [], "selection")
            require(case["model_calls"], {"alpha": 1, "beta": 1, "selector": 0} if selector else {"alpha": 1, "beta": 1}, "replay counts")
            require(case["stop_reason"], "Maximum number of turns 2 reached." if selector else "Digraph execution is complete", "stop")
            for message in result["cases"][key]["messages"]:
                ident = message.pop("id")
                require(UUID(ident).version, 4, "message UUID4")
                require(datetime.fromisoformat(message.pop("created_at")).utcoffset().total_seconds(), 0, "UTC")
                ids.append(ident)
        if name != "static.json":
            require(len(set(ids)), 12, "unique messages")
            identity_sets.append(set(ids))
            normalized.append(result)
    require(identity_sets[0].isdisjoint(identity_sets[1]), True, "distinct runs")
    require(normalized[0], normalized[1], "A1 normalized pair")
    return {"paired_cases": 4, "unique_message_ids_per_run": 12,
            "static_comparison": "saved record and literal checks; no SDK reconstruction"}


def preservation(ref):
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", ref], cwd=ROOT, text=True).splitlines()
    artifacts = [p for p in paths if p.startswith(("observations/", "findings/", "gallery/")) and Path(p).suffix in {".json", ".svg", ".txt"}]
    artifacts += ["probes/airflow/OUTPUT.txt"]
    for path in artifacts:
        old = subprocess.check_output(["git", "show", ref + ":" + path], cwd=ROOT)
        require((ROOT / path).read_bytes(), old, "preservation " + path)
    return len(artifacts)


def coverage():
    ledger = (ROOT / "findings/completed-cohort-dispositions.md").read_text()
    synthesis = (ROOT / "findings/cross-framework-reconciliation.md").read_text()
    ids = re.findall(r"^\| ([A-Z][0-9]+-[a-z]):", ledger, re.M)
    require(len(ids), 47, "original claim rows")
    crosswalk = synthesis.split("| Cohort link |")[1].split("Read verdicts")[0]
    require(sorted(re.findall(r"\b(?:P[0-6]|C1|S1|T1)-[a-z]\b", crosswalk)), sorted(ids), "crosswalk")
    later = re.findall(r"^\| ((?:P8|A1)-[a-z]):", synthesis, re.M)
    require(sorted(later), sorted(["P8-" + x for x in "abcdefg"] + ["A1-" + x for x in "abcdefgh"]), "later claims")
    matrix = (ROOT / "probes/README.md").read_text().split("## Answer matrix")[1].split("### Q1")[0]
    require(len(re.findall(r"\[(?:support|partial|untested)\]\(#q[1-7]-", matrix)), 56, "linked cells")
    return {"cohort_claims": 47, "later_claims": 15, "linked_matrix_cells": 56}


def main():
    # The P8 verifier imports only stdlib at module scope; it reads native saved
    # task/state records. It never calls its probe's framework-execution main.
    subprocess.run([sys.executable, "-O", "probes/boundaries/prefect/verify.py",
                    "observations/P8/run-1.json", "observations/P8/run-2.json"], cwd=ROOT, check=True)
    result = {"evidence_class": "saved-record audit; no framework execution",
              "cohort": cohort(), "P8": "native identities, states, edges, hashes and paired assertions passed",
              "A1": autogen(), "coverage": coverage(),
              "unchanged_input_artifacts": preservation(BASE),
              "unchanged_beta2_artifacts": preservation(HISTORY)}
    target = Path(__file__).with_name("audit.json")
    if sys.argv[1:] == ["--write"]:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result, json.loads(target.read_text()), "saved P7 audit")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
