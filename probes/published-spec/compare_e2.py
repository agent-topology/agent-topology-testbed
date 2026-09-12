"""Audit and compare one E2 replay without normalizing package observations."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from replay_e2 import OBSERVATION, VERSIONS, checked_inputs, digest, require, save


def load_population(out, label):
    raw = gzip.decompress((out / "population" / f"{label}.jsonl.gz").read_bytes())
    return [json.loads(line) for line in raw.splitlines()]


def load_one(out, group, name, label):
    return json.loads((out / group / name / f"{label}.json").read_text())


def accepted(record, context):
    require(record.get("status") != "error", f"adapter error: {context}")
    require(record.get("status") == "accepted", f"validation rejection: {context}")
    require(record.get("validation", {}).get("accepted") is True, f"inconsistent validation: {context}")
    require(set(record["structureHash"]) == {"algorithm", "algorithmVersion", "value"}, f"incomplete hash tuple: {context}")


def pair(first, second):
    return {
        "validation": "accepted" if first["status"] == second["status"] == "accepted" else "different-or-rejected",
        "canonical": "equal" if first.get("canonical", "").encode() == second.get("canonical", "").encode() else "different",
        "structure_hash": "equal" if first.get("structureHash") == second.get("structureHash") else "different",
    }


def compare(out):
    expected, population, cases, minimized, boundaries = checked_inputs()
    rows = {label: load_population(out, label) for label in VERSIONS}
    require(all(len(value) == len(cases) for value in rows.values()), "population result count mismatch")
    counts = Counter()
    comparisons = []
    for index, (raw, case) in enumerate(zip(population.splitlines(keepends=True), cases)):
        records = {label: rows[label][index] for label in VERSIONS}
        for label, record in records.items():
            accepted(record, f"population/{case['case']}/{label}")
            require(record["identity"]["version"] == VERSIONS[label], f"identity mismatch: {case['case']}/{label}")
            require(record["input_sha256"] == digest(raw) == case["input_sha256"], f"input mismatch: {case['case']}/{label}")
            properties = record.get("properties", {})
            require(set(properties) == {"non_mutation", "idempotence", "hash_idempotence"}
                    and all(properties.values()), f"property failure: {case['case']}/{label}")
        hashes = {json.dumps(record["structureHash"], sort_keys=True) for record in records.values()}
        require(len(hashes) == 1, f"structure hash transition: {case['case']}")
        beta2 = pair(records["py-b2"], records["js-b2"])
        py_transition = pair(records["py-b2"], records["py-b3"])
        js_transition = pair(records["js-b2"], records["js-b3"])
        beta3 = pair(records["py-b3"], records["js-b3"])
        require(beta3["canonical"] == "equal", f"beta.3 canonical mismatch: {case['case']}")
        historical_difference = "canonical" in case["mismatch"]
        require((beta2["canonical"] == "different") == historical_difference,
                f"beta.2 F8 classification changed: {case['case']}")
        counts.update({f"python_b2_to_b3_canonical_{py_transition['canonical']}": 1,
                       f"npm_b2_to_b3_canonical_{js_transition['canonical']}": 1,
                       f"beta2_cross_language_canonical_{beta2['canonical']}": 1,
                       f"beta3_cross_language_canonical_{beta3['canonical']}": 1})
        comparisons.append({"case": case["case"], "input_sha256": case["input_sha256"],
                            "python_beta2_to_beta3": py_transition, "npm_beta2_to_beta3": js_transition,
                            "beta2_cross_language": beta2, "beta3_cross_language": beta3})

    minimized_report = []
    for sha, _ in minimized:
        records = {label: load_one(out, "minimized", sha, label) for label in VERSIONS}
        for label, record in records.items():
            accepted(record, f"minimized/{sha}/{label}")
            require(record["input_sha256"] == sha, f"minimized input mismatch: {sha}/{label}")
        require(len({json.dumps(record["structureHash"], sort_keys=True) for record in records.values()}) == 1,
                f"minimized hash transition: {sha}")
        beta2 = pair(records["py-b2"], records["js-b2"])
        beta3 = pair(records["py-b3"], records["js-b3"])
        require(beta2["canonical"] == "different", f"minimized F8 no longer reproduced on beta.2: {sha}")
        require(beta3["canonical"] == "equal", f"minimized F8 reproduced on beta.3: {sha}")
        minimized_report.append({"input_sha256": sha, "beta2_cross_language": beta2,
                                 "beta3_cross_language": beta3,
                                 "python_beta2_to_beta3": pair(records["py-b2"], records["py-b3"]),
                                 "npm_beta2_to_beta3": pair(records["js-b2"], records["js-b3"])})

    boundary_report = []
    for name, raw in boundaries:
        records = {label: load_one(out, "boundary", name, label) for label in VERSIONS}
        for label, record in records.items():
            accepted(record, f"boundary/{name}/{label}")
            require(record["input_sha256"] == digest(raw), f"boundary input mismatch: {name}/{label}")
        require(len({json.dumps(record["structureHash"], sort_keys=True) for record in records.values()}) == 1,
                f"boundary hash transition: {name}")
        beta2 = pair(records["py-b2"], records["js-b2"])
        beta3 = pair(records["py-b3"], records["js-b3"])
        require(beta2["canonical"] == "different", f"beta.2 boundary unexpectedly byte-equal: {name}")
        require(beta3["canonical"] == "equal", f"beta.3 boundary not narrowed equally: {name}")
        narrowed = "-9007199254740992" if name == "unsafe-negative" else "9007199254740992"
        require(f'"x-e2":{narrowed}' in records["py-b3"]["canonical"], f"wrong beta.3 narrowing: {name}")
        boundary_report.append({
            "case": name,
            "input_sha256": digest(raw),
            "classification": "compatibility-transition: beta.2 rejected from cross-language byte parity; beta.3 narrows identically",
            "package_validation": "accepted in all four installations",
            "narrowed_value": narrowed,
            "beta2_cross_language": beta2,
            "beta3_cross_language": beta3,
            "python_beta2_to_beta3": pair(records["py-b2"], records["py-b3"]),
            "npm_beta2_to_beta3": pair(records["js-b2"], records["js-b3"]),
        })

    report = {
        "summary": {
            "population_cases": len(cases),
            "minimized_candidates": len(minimized),
            "boundary_cases": len(boundaries),
            "validation_rejections": 0,
            "structure_hash_transitions_or_disagreements": 0,
            **dict(sorted(counts.items())),
            "beta3_minimized_canonical_differences": 0,
            "beta3_boundary_canonical_differences": 0,
        },
        "population_comparisons": comparisons,
        "minimized_comparisons": minimized_report,
        "boundary_comparisons": boundary_report,
        "disposition": "F8 resolved within E1's bounded saved population and all 16 minimized candidates on published beta.3; beta.2 evidence preserved",
        "generator_rerun": False,
    }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = compare(args.records)
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        raise SystemExit(1)
    save(args.report or args.records / "comparison.json", result)
    print(json.dumps(result["summary"], sort_keys=True))
