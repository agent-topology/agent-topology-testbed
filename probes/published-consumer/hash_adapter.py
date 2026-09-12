"""One JSON document + a requested algorithm version in; a direct compute_structure_hash
call out, never passing through validate_document.

Isolates the hash-computation boundary (K1 case 7) from structural validation
(K1's document-mutation cases, exercised through adapter.py instead).
"""
import hashlib
import importlib.metadata
import json
import platform
import sys

import agent_topology.spec as spec

algorithm_version = sys.argv[1]
raw = sys.stdin.buffer.read()
result = {
    "identity": {
        "version": importlib.metadata.version("agent-topology-spec"),
        "runtime": platform.python_version(),
        "imported_path": spec.__file__,
        "executable": sys.executable,
    },
    "input_sha256": hashlib.sha256(raw).hexdigest(),
    "requested_algorithm_version": algorithm_version,
}
try:
    document = json.loads(raw)
    result["structureHash"] = spec.compute_structure_hash(document, algorithm_version=algorithm_version)
    result["status"] = "computed"
except Exception as error:
    result.update(status="error", error={"type": type(error).__name__, "message": str(error)})
print(json.dumps(result, ensure_ascii=False))
sys.exit(0 if result["status"] == "computed" else 3)
