"""Audit two E2 captures and compare their complete semantic observations."""
import argparse
from copy import deepcopy
import gzip
import json
from pathlib import Path

from compare_e2 import compare
from replay_e2 import VERSIONS, checked_inputs, require


def normalized(record):
    value = deepcopy(record)
    identity = value.get("identity", {})
    identity.pop("executable", None)
    identity.pop("imported_path", None)
    return value


def records(path, group, names):
    result = {}
    for name in names:
        for label in VERSIONS:
            result[(name, label)] = normalized(json.loads((path / group / name / f"{label}.json").read_text()))
    return result


def population(path):
    result = {}
    for label in VERSIONS:
        raw = gzip.decompress((path / "population" / f"{label}.jsonl.gz").read_bytes())
        result[label] = [normalized(json.loads(line)) for line in raw.splitlines()]
    return result


def verify(first, second):
    _, _, _, minimized, boundaries = checked_inputs()
    first_report, second_report = compare(first), compare(second)
    require(first_report == second_report, "derived replay reports differ")
    require(population(first) == population(second), "population semantic observations differ")
    minima = [sha for sha, _ in minimized]
    boundary_names = [name for name, _ in boundaries]
    require(records(first, "minimized", minima) == records(second, "minimized", minima),
            "minimized semantic observations differ")
    require(records(first, "boundary", boundary_names) == records(second, "boundary", boundary_names),
            "boundary semantic observations differ")
    require(json.loads((first / "setup/artifacts.json").read_text()) ==
            json.loads((second / "setup/artifacts.json").read_text()), "installed artifact inventories differ")

    first_identities = json.loads((first / "identities.json").read_text())
    second_identities = json.loads((second / "identities.json").read_text())
    for label in VERSIONS:
        require(first_identities[label]["version"] == second_identities[label]["version"], f"version differs: {label}")
        require(first_identities[label]["runtime"] == second_identities[label]["runtime"], f"runtime differs: {label}")
        require(first_identities[label]["imported_path"] != second_identities[label]["imported_path"],
                f"captures did not use fresh installation paths: {label}")
    return {
        "status": "passed",
        "runs": [str(first), str(second)],
        "normalization": ["identity.executable", "identity.imported_path"],
        "compared_without_normalization": [
            "validation", "canonical", "structureHash", "properties", "input_sha256",
            "identity.version", "identity.runtime", "setup/artifacts.json",
        ],
        "population_cases": first_report["summary"]["population_cases"],
        "minimized_candidates": first_report["summary"]["minimized_candidates"],
        "boundary_cases": first_report["summary"]["boundary_cases"],
        "generator_rerun": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.first, args.second)
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        raise SystemExit(1)
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
