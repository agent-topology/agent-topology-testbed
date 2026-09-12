"""Fix K1's six document cases and their independent oracles once, into observations/K1/.

Run once, like published-spec/run.py's initial --resolve; do not rerun to reproduce
K1 -- run.py verifies the committed cases against mutate.py's deterministic output
instead of regenerating them differently.
"""
import hashlib
import json
from pathlib import Path

from mutate import BASE_STRUCTURE_HASH, DOCUMENT_CASES, HASH_BOUNDARY_CASE, HASH_BOUNDARY_REQUESTED_VERSION

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "observations/K1"

# Independent, before-extraction expected outcomes. Reasons cite the obligation
# table in observations/K1/README.md; they are not derived by calling the spec
# packages under test.
EXPECTED = {
    "baseline": {
        "call": "adapter",
        "validation": "accepted",
        "structureHash": {"algorithm": "sha256", "algorithmVersion": "1", "value": BASE_STRUCTURE_HASH},
        "reason": "unmutated document V1 already recorded as accepted in all four installations",
    },
    "unsupported-topology-version": {
        "call": "adapter",
        "validation": "rejected",
        "reason": "schema requires topologyVersion const 0.1; identical in the beta.1 and beta.2 pinned schema snapshots",
    },
    "unsupported-hash-algorithm-version-declared": {
        "call": "adapter",
        "validation": "rejected",
        "reason": "schema requires structureHash.algorithmVersion const 1; identical in both pinned schema snapshots",
    },
    "unknown-permitted-extension": {
        "call": "adapter",
        "validation": "accepted",
        "structureHash": {"algorithm": "sha256", "algorithmVersion": "1", "value": BASE_STRUCTURE_HASH},
        "reason": "x-k1-probe matches the schema's x-[a-z0-9][a-z0-9._-]* pattern at the document root, which allows unknown keys; hash version 1's projection reads only graphs, so it is unaffected by any root-level key",
    },
    "invalid-extension-placement": {
        "call": "adapter",
        "validation": "rejected",
        "reason": "completeness.gaps[].element (the elementReference def) has additionalProperties:false with no x-* patternProperties allowance, unlike every other object in the schema; the same key name accepted in unknown-permitted-extension is rejected here purely because of where it sits",
    },
    "malformed-extension-key": {
        "call": "adapter",
        "validation": "rejected",
        "reason": "X-k1-probe does not match the schema's x-[a-z0-9][a-z0-9._-]* pattern (capital X); additionalProperties:false rejects it at the document root even though extension keys are otherwise allowed there",
    },
    HASH_BOUNDARY_CASE: {
        "call": "hash_adapter",
        "input": "baseline",
        "requested_algorithm_version": HASH_BOUNDARY_REQUESTED_VERSION,
        "outcome": "error",
        "error_type": {"python": "ValueError", "typescript": "RangeError"},
        "reason": "compute_structure_hash/computeStructureHash's algorithm_version parameter is checked against the single supported version (1) and raises without touching validate_document; this is the hash-computation boundary, not the structural-validation boundary exercised by the two synthetic-version document cases above",
    },
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    (OUT / "cases").mkdir(parents=True, exist_ok=True)
    manifest = {"source_document": "observations/V1/inputs/minimal.json", "cases": {}}
    for name, build in DOCUMENT_CASES.items():
        document = build()
        path = OUT / "cases" / f"{name}.json"
        save(path, document)
        raw = path.read_bytes()
        manifest["cases"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "expected": EXPECTED[name]}
    manifest["cases"][HASH_BOUNDARY_CASE] = {"sha256": None, "expected": EXPECTED[HASH_BOUNDARY_CASE]}
    save(OUT / "cases.json", manifest)
    print(f"wrote {len(DOCUMENT_CASES)} case documents and {OUT}/cases.json")


if __name__ == "__main__":
    main()
