"""One JSON document in; public installed Python spec observations out."""
import hashlib
import importlib.metadata
import json
import platform
import sys

import agent_topology.spec as spec

raw = sys.stdin.buffer.read()
result = {
    "identity": {
        "version": importlib.metadata.version("agent-topology-spec"),
        "runtime": platform.python_version(),
        "imported_path": spec.__file__,
        "executable": sys.executable,
    },
    "input_sha256": hashlib.sha256(raw).hexdigest(),
}
stage = "parse"
try:
    document = json.loads(raw)
    stage = "validation"
    errors = spec.validate_document(document)
    result["validation"] = {"accepted": not errors, "errors": errors}
    if errors:
        result["status"] = "rejected"
    else:
        stage = "canonical"
        result["canonical"] = spec.canonical_json(document)
        stage = "hash"
        result["structureHash"] = spec.compute_structure_hash(document)
        result["status"] = "accepted"
except Exception as error:
    result.update(status="error", error={"stage": stage, "type": type(error).__name__, "message": str(error)})
print(json.dumps(result, ensure_ascii=False))
sys.exit(0 if result["status"] == "accepted" else 2 if result["status"] == "rejected" else 3)
