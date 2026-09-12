"""Compare saved V1 records; disagreements return nonzero without hiding classes."""
import argparse
import json
from pathlib import Path

from run import INPUTS, VERSIONS, digest, require, save


def compare(out, manifest):
    report = {k: [] for k in ("rejected", "hash_disagreements", "algorithm_transitions", "canonical_differences", "comparisons")}
    for name, expected in manifest["inputs"].items():
        require(digest((INPUTS / "inputs" / name).read_bytes()) == expected["sha256"], f"input changed: {name}")
        records = {}
        for label, version in VERSIONS.items():
            a, b = [json.loads((out / f"{label}-{Path(name).stem}-{n}.json").read_text()) for n in (1, 2)]
            require(a == b, f"fresh-process disagreement: {label}/{name}")
            require(a["identity"]["version"] == version, f"identity mismatch: {label}")
            require(a["input_sha256"] == expected["sha256"], f"input mismatch: {label}/{name}")
            require(a["status"] in ("accepted", "rejected"), f"adapter error: {label}/{name}")
            if a["status"] == "rejected":
                report["rejected"].append({"input": name, "installation": label, "validation": a["validation"]})
            else:
                require(a["validation"]["accepted"] is True, "inconsistent validation")
                h = a["structureHash"]
                require(set(h) == {"algorithm", "algorithmVersion", "value"}, "incomplete hash tuple")
                if (h["algorithm"], h["algorithmVersion"]) != (expected["expected_hash"]["algorithm"], expected["expected_hash"]["algorithmVersion"]):
                    report["algorithm_transitions"].append({"input": name, "installation": label, "expected": expected["expected_hash"], "actual": h})
                elif h != expected["expected_hash"]:
                    report["hash_disagreements"].append({"input": name, "installation": label, "expected": expected["expected_hash"], "actual": h})
            records[label] = a
        for left, right in (("py-b1", "py-b2"), ("js-b1", "js-b2"), ("py-b1", "js-b1"), ("py-b2", "js-b2")):
            a, b = records[left], records[right]
            pair = {"input": name, "left": left, "right": right}
            if a["status"] != "accepted" or b["status"] != "accepted":
                report["comparisons"].append(dict(pair, status="excluded-rejected"))
                continue
            if a["canonical"].encode("utf-8") != b["canonical"].encode("utf-8"):
                report["canonical_differences"].append(pair)
            ha, hb = a["structureHash"], b["structureHash"]
            if (ha["algorithm"], ha["algorithmVersion"]) != (hb["algorithm"], hb["algorithmVersion"]):
                report["algorithm_transitions"].append(dict(pair, left_hash=ha, right_hash=hb))
                status = "algorithm-transition"
            elif ha != hb:
                report["hash_disagreements"].append(dict(pair, left_hash=ha, right_hash=hb))
                status = "hash-disagreement"
            else:
                status = "same-algorithm-equal"
            report["comparisons"].append(dict(pair, status=status))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--expected", type=Path, default=INPUTS / "inputs.json")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = compare(args.records, json.loads(args.expected.read_text()))
    save(args.report or args.records / "comparison.json", report)
    print(json.dumps({k: len(v) for k, v in report.items()}))
    # Canonical differences are independently reviewable, never structural failures.
    raise SystemExit(1 if any(report[k] for k in ("hash_disagreements", "algorithm_transitions", "rejected")) else 0)
