"""Compare saved K1 records against the before-extraction oracle; disagreements
return nonzero without hiding classes. Builds the versioned compatibility matrix."""
import argparse
import json
from pathlib import Path

from mutate import DOCUMENT_CASES, HASH_BOUNDARY_CASE
from run import K1, VERSIONS, digest, require, save

_ERROR_TYPE_LANGUAGE = {"py-b1": "python", "py-b2": "python", "js-b1": "typescript", "js-b2": "typescript"}


def compare(out, manifest):
    matrix = []
    mismatches = []
    for name in DOCUMENT_CASES:
        expected = manifest["cases"][name]["expected"]
        for label, version in VERSIONS.items():
            a, b = [json.loads((out / f"{label}-{name}-{n}.json").read_text()) for n in (1, 2)]
            require(a == b, f"fresh-process disagreement: {label}/{name}")
            require(a["identity"]["version"] == version, f"identity mismatch: {label}/{name}")
            row = {"case": name, "installation": label, "expected_validation": expected["validation"], "observed_status": a["status"]}
            observed_validation = "accepted" if a["status"] == "accepted" else "rejected" if a["status"] == "rejected" else "error"
            ok = observed_validation == expected["validation"]
            if ok and expected["validation"] == "accepted":
                row["expected_hash"] = expected["structureHash"]
                row["observed_hash"] = a["structureHash"]
                ok = a["structureHash"] == expected["structureHash"]
            row["match"] = ok
            matrix.append(row)
            if not ok:
                mismatches.append(row)

    expected = manifest["cases"][HASH_BOUNDARY_CASE]["expected"]
    for label, version in VERSIONS.items():
        a, b = [json.loads((out / f"{label}-{HASH_BOUNDARY_CASE}-{n}.json").read_text()) for n in (1, 2)]
        require(a == b, f"fresh-process disagreement: {label}/{HASH_BOUNDARY_CASE}")
        require(a["identity"]["version"] == version, f"identity mismatch: {label}/{HASH_BOUNDARY_CASE}")
        language = _ERROR_TYPE_LANGUAGE[label]
        row = {"case": HASH_BOUNDARY_CASE, "installation": label, "expected_outcome": expected["outcome"], "observed_status": a["status"]}
        ok = a["status"] == expected["outcome"]
        if ok and expected["outcome"] == "error":
            row["expected_error_type"] = expected["error_type"][language]
            row["observed_error_type"] = a["error"]["type"]
            ok = a["error"]["type"] == expected["error_type"][language]
        row["match"] = ok
        matrix.append(row)
        if not ok:
            mismatches.append(row)

    return {"matrix": matrix, "mismatches": mismatches, "summary": {"rows": len(matrix), "mismatches": len(mismatches)}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--expected", type=Path, default=K1 / "cases.json")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = compare(args.records, json.loads(args.expected.read_text()))
    save(args.report or args.records / "comparison.json", report)
    print(json.dumps(report["summary"]))
    raise SystemExit(1 if report["mismatches"] else 0)
