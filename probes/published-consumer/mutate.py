"""Single-field mutations of V1's minimal accepted document for K1 boundary cases.

Each function returns one document that differs from the base by exactly the
change named in its docstring. No mutation touches more than one obligation
under test; `invalid-extension-placement` also flips `completeness.status`
because that is required scaffolding to attach a `gaps` entry, not a second
independent claim under test.
"""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_DOCUMENT = json.loads((HERE.parents[1] / "observations/V1/inputs/minimal.json").read_text())
BASE_STRUCTURE_HASH = BASE_DOCUMENT["structureHash"]["value"]


def _document():
    return copy.deepcopy(BASE_DOCUMENT)


def case_baseline():
    """Unmutated control: the same document V1 already recorded as accepted."""
    return _document()


def case_unsupported_topology_version():
    """topologyVersion 0.1 -> 0.2: synthetic unsupported document-format version."""
    doc = _document()
    doc["topologyVersion"] = "0.2"
    return doc


def case_unsupported_hash_algorithm_version_declared():
    """structureHash.algorithmVersion 1 -> 2: synthetic unsupported hash-algorithm version, declared in the document."""
    doc = _document()
    doc["structureHash"]["algorithmVersion"] = "2"
    return doc


def case_unknown_permitted_extension():
    """Add one schema-permitted x-* key at the document root (string value; avoids the F8 numeric-canonicalization gap, which this case does not test)."""
    doc = _document()
    doc["x-k1-probe"] = "case-4-string-value"
    return doc


def case_invalid_extension_placement():
    """Place the same key name as case 4, unchanged, inside completeness.gaps[].element -- a location the schema does not grant the x-* allowance."""
    doc = _document()
    doc["completeness"] = {
        "status": "incomplete",
        "gaps": [
            {
                "code": "k1-probe-gap",
                "message": "synthetic gap added only to place an extension key inside completeness.gaps[].element",
                "element": {"graphId": "g", "kind": "graph", "id": "g", "x-k1-probe": "case-5-should-be-rejected"},
            }
        ],
    }
    return doc


def case_malformed_extension_key():
    """Add a document-root key shaped like an extension but violating the x-[a-z0-9][a-z0-9._-]* pattern (uppercase X)."""
    doc = _document()
    doc["X-k1-probe"] = "case-6-should-be-rejected"
    return doc


DOCUMENT_CASES = {
    "baseline": case_baseline,
    "unsupported-topology-version": case_unsupported_topology_version,
    "unsupported-hash-algorithm-version-declared": case_unsupported_hash_algorithm_version_declared,
    "unknown-permitted-extension": case_unknown_permitted_extension,
    "invalid-extension-placement": case_invalid_extension_placement,
    "malformed-extension-key": case_malformed_extension_key,
}

# Case 7, hash-computation-unsupported-algorithm-version, calls compute_structure_hash /
# computeStructureHash directly on the unmutated baseline document with an explicit
# out-of-range algorithm_version argument, bypassing validate_document entirely. It is
# not a document mutation and has no entry in DOCUMENT_CASES; see hash_adapter.py/.mjs.
HASH_BOUNDARY_CASE = "hash-computation-unsupported-algorithm-version"
HASH_BOUNDARY_REQUESTED_VERSION = "2"
