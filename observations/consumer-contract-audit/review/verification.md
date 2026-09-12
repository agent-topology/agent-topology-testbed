# Documentation and evidence integrity verification

The semantic review is in [semantic-review.md](semantic-review.md). The checks
below verify transcription, provenance and table completeness, not consumer
behavior, framework execution or the truth of a producer assertion. They do not
calculate reachability or generate semantic expectations. No dependencies need
installation; Python's standard library and the sibling upstream Git repository
at the pinned object are sufficient.

From the testbed root, run `rtk git diff --check` and the following as a one-shot
`rtk proxy python3 -` input. This is an editorial record check, not a new consumer
or maintained conformance test. Explicit exceptions also operate under Python `-O`.

```python
from pathlib import Path
from hashlib import sha256
from collections import Counter
import itertools
import json
import subprocess

root = Path("observations/consumer-contract-audit")
def require(value, message):
    if not value:
        raise ValueError(message)
def load(path):
    return json.loads((root / path).read_text())
def digest(raw):
    return sha256(raw).hexdigest()
def pointer(value, path):
    if path == "":
        return value
    require(path.startswith("/"), path)
    for token in path[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value
manifest = load("manifest.json")
ref = manifest["upstream_commit"]
def upstream(path):
    return subprocess.check_output(["git", "-C", "../agent-topology", "show", ref + ":" + path])
inputs = {item["id"]: item for item in manifest["inputs"]}
require(len(inputs) == len(manifest["inputs"]) == 31, "input inventory")
documents = {}
for item in manifest["sources"]:
    raw = (root / item["local_path"]).read_bytes()
    require(digest(raw) == item["sha256"], item["local_path"])
    require(raw == upstream(item["upstream_path"]), item["upstream_path"])
for cid, item in inputs.items():
    raw = (root / item["local_path"]).read_bytes()
    original = upstream(item["upstream_path"])
    require(digest(raw) == item["sha256"], cid)
    require(digest(original) == item["source_sha256"], cid + " source")
    document = json.loads(raw)
    require(document == pointer(json.loads(original), item["source_pointer"]), cid + " extraction")
    if not item["source_pointer"]:
        require(raw == original, cid + " exact fixture bytes")
    documents[cid] = document
sources = load("sources.json")
rules = {s["id"] for s in sources} | {"L-PROFILE", "L-ROOT", "L-PATH"}
for source in sources:
    lines = (root / source["local_path"]).read_text().splitlines()
    lo, hi = source["lines"]
    require(1 <= lo <= hi <= len(lines), source["id"] + " span")
    require(source["quote"] in "\n".join(lines[lo-1:hi]), source["id"] + " quotation")
    require(source["upstream_commit"] == ref, source["id"] + " pin")
facts = load("core-facts.json")
prerequisites = load("prerequisites.json")
require(set(facts) == set(prerequisites) == set(inputs), "case coverage")
for cid, document in documents.items():
    structure = document["graphs"][0]["structure"]
    for output, field in [("ordinary_edges", "edges"), ("joins", "joins"), ("listed_candidates", "entryNodeIds")]:
        require(facts[cid][output] == structure[field], cid + " transcription " + field)
    require(facts[cid]["recorded_uncertainty"] == {"completeness": document["completeness"], "producerLimitations": document["producerLimitations"]}, cid + " uncertainty transcription")
    node_ids = {n["id"] for n in structure["nodes"]}
    require(set(facts[cid]["structural_reachability"]) == node_ids, cid + " path table subjects")
    for destinations in facts[cid]["structural_reachability"].values():
        require(set(destinations) <= node_ids, cid + " path table reference")
        require(destinations == sorted(set(destinations)), cid + " path table order/duplicates")
    for verdict in prerequisites[cid].values():
        require(set(verdict["rules"]) <= rules, cid + " prerequisite citations")
        for p in verdict.get("input_pointers", []):
            pointer(document, p)
rows = [json.loads(line) for line in (root / "matrix.jsonl").read_text().splitlines()]
expected_ids = {f"{cid}/{profile}/CQ{q}" for cid, profile, q in itertools.product(inputs, ["core-only", "opt-in"], range(1, 6))}
require(len(rows) == 310 and {row["id"] for row in rows} == expected_ids, "310 unique groups")
def check_refs(value):
    if isinstance(value, dict):
        if "expected_ref" in value:
            file, fragment = value["expected_ref"].split("#", 1)
            pointer(load(file), fragment)
        for child in value.values():
            check_refs(child)
    elif isinstance(value, list):
        for child in value:
            check_refs(child)
for row in rows:
    document = documents[row["input_id"]]
    parts = [answer["part"] for answer in row["answers"]]
    require(len(parts) == len(set(parts)), row["id"] + " unique subquestions")
    for answer in row["answers"]:
        status = answer["judgment"]
        require(status in {"determined", "underdetermined", "contradictory"}, row["id"] + " status")
        require(("expected" in answer) == (status == "determined"), row["id"] + " blank discipline")
        require(answer["derivation"] and answer["rules"] and answer["input_pointers"], row["id"] + " traceability")
        require(set(answer["rules"]) <= rules, row["id"] + " citation")
        for p in answer["input_pointers"]:
            pointer(document, p)
        check_refs(answer.get("expected"))
packet = [json.loads(line) for line in (root / "review/questions-without-expectations.jsonl").read_text().splitlines()]
require({row["id"] for row in packet} == expected_ids and len(packet) == 310, "redacted packet coverage")
require(all(set(q) == {"part", "input_pointers", "rules"} for row in packet for q in row["questions"]), "packet has no expected answers")
for path, expected in load("review/pre-comparison-sha256.json")["files"].items():
    raw = (root / path).read_bytes()
    if path == "sources.json":
        correction = load("review/citation-correction.json")
        current = json.loads(raw)
        found = next(i for i, s in enumerate(current) if s["id"] == "R-LIMIT")
        require(current[found] == correction["after"], "citation correction result")
        before, after = correction["before"], correction["after"]
        require({k: v for k, v in before.items() if k not in {"lines", "url"}} == {k: v for k, v in after.items() if k not in {"lines", "url"}}, "only citation span/URL changed")
        current[found] = before
        raw = (json.dumps(current, indent=2) + "\n").encode()
    require(digest(raw) == expected, "post-label semantic drift: " + path)
labels = load("review/upstream-labels.json")["rows"]
require(Counter(row["status_comparison"] for row in labels) == {"agrees": 23}, "status label comparison")
require(Counter(row["shape_comparison"] for row in labels) == {"agrees": 21, "not-comparable": 2}, "shape label comparison")
counts = Counter(a["judgment"] for row in rows for a in row["answers"])
require(counts == {"determined": 900, "underdetermined": 402}, "reported counts")
print("31 input identities and 19 source copies match pinned Git objects")
print("26 source quotations, 310 groups, 1302 subanswers, pointers and references verified")
print("900 determined; 402 underdetermined with no expected value; 0 contradictory/unreviewed")
print("310 redacted review groups; no semantic drift after label comparison")
```

## Recorded result

Executed successfully with **Python 3.14.7**, including `-O`. No installation,
consumer package, framework process or reference test was used.

```text
31 input identities and 19 source copies match pinned Git objects
26 source quotations, 310 groups, 1302 subanswers, pointers and references verified
900 determined; 402 underdetermined with no expected value; 0 contradictory/unreviewed
310 redacted review groups; no semantic drift after label comparison
```

The initial run failed on R-LIMIT: its end-line locator was 81 in a 79-line
source. The quotation itself was already correct. The retained
[citation correction](citation-correction.json) records the old/new locator;
only that span and URL changed. The check above reconstructs the original source
ledger to verify its pre-comparison digest while requiring every other field to
remain unchanged. Matrix, core facts and prerequisites still match their frozen
pre-comparison bytes. This is not a second semantic evaluation or a consumer run.

All authored Markdown local targets/anchors were checked, including the matrix
input links and existing finding anchors. Archived upstream source files were
checked byte-for-byte against Git instead; their original relative links were
not rewritten into a partial local docs tree. `rtk git diff --check` passed;
new authored files were also checked directly for trailing whitespace and newline
termination because they are untracked until a later commit.
