"""Compare saved V2 records with acceptance, bytes, and hashes kept separate."""
import argparse
import json
from pathlib import Path

from run_v2 import EXPECTATIONS, INPUTS, VERSIONS, digest, require, save

PAIRS = (("py-b2", "py-b3"), ("js-b2", "js-b3"), ("py-b3", "js-b3"))


def compare(out, manifest, expectations):
    report = {key: [] for key in (
        "rejected", "hash_disagreements", "algorithm_transitions", "canonical_differences",
        "expectation_mismatches", "comparisons",
    )}
    require(set(expectations["inputs"]) == set(manifest["inputs"]), "V2 expectation inventory mismatch")
    for name, oracle in manifest["inputs"].items():
        expected = expectations["inputs"][name]
        require(digest((INPUTS / "inputs" / name).read_bytes()) == oracle["sha256"] == expected["sha256"], f"input changed: {name}")
        records = {}
        for label, version in VERSIONS.items():
            first, second = [json.loads((out / f"{label}-{Path(name).stem}-{repeat}.json").read_text()) for repeat in (1, 2)]
            require(first == second, f"fresh-process disagreement: {label}/{name}")
            require(first["identity"]["version"] == version, f"identity mismatch: {label}")
            require(first["input_sha256"] == oracle["sha256"], f"input mismatch: {label}/{name}")
            require(first["status"] in ("accepted", "rejected"), f"adapter error: {label}/{name}")
            if first["status"] == "rejected":
                report["rejected"].append({"input": name, "installation": label, "validation": first["validation"]})
            else:
                require(first["validation"]["accepted"] is True, "inconsistent validation")
                structure_hash = first["structureHash"]
                require(set(structure_hash) == {"algorithm", "algorithmVersion", "value"}, "incomplete hash tuple")
                if (structure_hash["algorithm"], structure_hash["algorithmVersion"]) != (oracle["expected_hash"]["algorithm"], oracle["expected_hash"]["algorithmVersion"]):
                    report["algorithm_transitions"].append({"input": name, "installation": label, "expected": oracle["expected_hash"], "actual": structure_hash})
                elif structure_hash != oracle["expected_hash"]:
                    report["hash_disagreements"].append({"input": name, "installation": label, "expected": oracle["expected_hash"], "actual": structure_hash})
            records[label] = first
        for left, right in PAIRS:
            first, second = records[left], records[right]
            pair = {"input": name, "left": left, "right": right}
            if first["status"] != "accepted" or second["status"] != "accepted":
                report["comparisons"].append(dict(pair, validation="excluded-rejected", canonical="not-compared", structure_hash="not-compared"))
                continue
            canonical_equal = first["canonical"].encode("utf-8") == second["canonical"].encode("utf-8")
            expected_canonical_equal = expected["expected_full_canonical_bytes"] == "equal"
            if not canonical_equal:
                report["canonical_differences"].append(pair)
            if canonical_equal != expected_canonical_equal:
                report["expectation_mismatches"].append(dict(pair, field="full-canonical-bytes", expected=expected["expected_full_canonical_bytes"], actual="equal" if canonical_equal else "different"))
            left_hash, right_hash = first["structureHash"], second["structureHash"]
            if (left_hash["algorithm"], left_hash["algorithmVersion"]) != (right_hash["algorithm"], right_hash["algorithmVersion"]):
                report["algorithm_transitions"].append(dict(pair, left_hash=left_hash, right_hash=right_hash))
                hash_status = "algorithm-transition"
            elif left_hash != right_hash:
                report["hash_disagreements"].append(dict(pair, left_hash=left_hash, right_hash=right_hash))
                hash_status = "same-algorithm-disagreement"
            else:
                hash_status = "same-algorithm-equal"
            if expected["expected_structure_hash_tuple"] != "equal" or hash_status != "same-algorithm-equal":
                report["expectation_mismatches"].append(dict(pair, field="structure-hash-tuple", expected=expected["expected_structure_hash_tuple"], actual=hash_status))
            report["comparisons"].append(dict(pair, validation="accepted", canonical="equal" if canonical_equal else "different", structure_hash=hash_status))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--expected", type=Path, default=EXPECTATIONS)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = compare(args.records, json.loads((INPUTS / "inputs.json").read_text()), json.loads(args.expected.read_text()))
    save(args.report or args.records / "comparison.json", report)
    print(json.dumps({key: len(value) for key, value in report.items()}))
    failure_classes = ("rejected", "hash_disagreements", "algorithm_transitions", "expectation_mismatches")
    raise SystemExit(1 if any(report[key] for key in failure_classes) else 0)
