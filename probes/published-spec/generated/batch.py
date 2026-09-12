"""One JSON document in; public installed Python spec observations out."""
import hashlib
import importlib.metadata
import json
import platform
import sys

import agent_topology.spec as spec


def observe(raw):
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
        before = json.dumps(document, ensure_ascii=False)
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
            result["properties"] = {
                "non_mutation": json.dumps(document, ensure_ascii=False) == before,
                "idempotence": spec.canonical_json(json.loads(result["canonical"])) == result["canonical"],
                "hash_idempotence": spec.compute_structure_hash(json.loads(result["canonical"])) == result["structureHash"],
            }
            result["status"] = "accepted"
    except Exception as error:
        result.update(status="error", error={"stage": stage, "type": type(error).__name__, "message": str(error)})
    return result


for raw in sys.stdin.buffer:
    print(json.dumps(observe(raw), ensure_ascii=False), flush=True)
