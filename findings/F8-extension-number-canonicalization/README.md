# F8 — Extension numbers break published canonical-byte parity

**Supported, bounded interoperability gap (2026-09-12).** Published Python
`agent-topology-spec==0.1.0b2` and npm `@agent-topology/spec@0.1.0-beta.2`
accept identical valid JSON but return different full canonical UTF-8 bytes
for numeric extension payloads. This is a full-document serialization finding,
not a structure-hash defect or a schema-shape proposal.

**Beta.3 boundary (V2, 2026-09-12).** [V2](../../observations/V2/README.md)
found equal canonical bytes and hash tuples across beta.2→beta.3 for V1's nine
fixed documents, but the pre-run inspection confirmed that none contains a
numeric extension. V2 is therefore a bounded non-finding for that corpus, not a
beta.3 replay or resolution of F8. E2
[#54](https://github.com/agent-topology/agent-topology-testbed/issues/54) remains
the planned numeric-population re-observation.

[E1](../../observations/E1/README.md) supplies retrospective callable evidence:
three seeds × 100 base examples, each with a structural permutation, repeated
in isolated registry-installed environments. There are 42 failing bases (84
comparisons) per run, all canonical-only differences. All inputs validate and
all `sha256` / algorithmVersion `1` / value tuples agree. No mutation,
idempotence or structural-order failure was observed. This finding is distinct
from F1–F7 and does not reinterpret their historical evidence.

## Smallest retained candidate

The [479-byte minimized input](../../observations/E1/run-a/minimized/ee86a4edb23649b446b91e1cbb54141c54381d423310ea9f7d9e968b895fd1ae.json)
contains one empty graph, required provenance/completeness/hash fields and
`"x-e1":0.0`. Both packages accept it. The full canonical results differ at:

```text
Python:     ...,"x-e1":0.0}
TypeScript: ...,"x-e1":0}
```

Both compute structure hash
`cc7ca998724e096e6c4a7ed4eeeda0141abd19cb830c8be1180599d305af9d22`
with algorithm `sha256`, version `1`. The
[fresh V1 replay](../../observations/E1/run-a/minimized/ee86a4edb23649b446b91e1cbb54141c54381d423310ea9f7d9e968b895fd1ae-replay.json)
retains commands, exact package/import/runtime identities, input digest, accepted
outcomes, canonical strings, hash tuples and exits. Run B independently reproduces
this and all other reduced candidates. The reducer establishes a local minimum
under documented reductions, not a universal minimality proof.

## Contract and decision impact

The [pinned canonical-form contract](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/0.1-contract.md#canonical-form)
says both spec packages implement the same canonical form and describes
cross-language byte comparisons. The schema allows arbitrary JSON values under
well-formed extension keys. The contract specifies key/collection ordering but
leaves numeric spelling unspecified. E1 demonstrates the byte-level gap without
choosing Python's or JavaScript's representation as the normative answer.
This is an implementation interoperability gap with a number-policy clarification
needed upstream; it is not evidence of invalid generated input.

A consumer cannot assume these published full-document canonical bytes agree
when extensions contain such numbers. Extensions are explicitly excluded from
hash version 1, so these same examples do not produce topology-change signals.
Artifact SHA-256 checks and historical release qualification receipts measure
something different and remain unchanged. There is no evidence here of broken
structure hashes, arbitrary numeric domains or later-version behavior.

## Suggested handoff — not posted or graduated

Proposed owner: upstream spec maintainers, through the existing
[TypeScript cross-language contract suite](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/typescript/spec/tests/contract.test.mjs)
and [Python canonical suite](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/spec/tests/test_canonical.py).
Those tests already cover fixtures and the U+E000/U+10000 ordering boundary;
the incremental regression is the valid numeric-extension candidate above.

The smallest follow-up is to choose/document the numeric canonical-byte policy,
then incorporate this input and an agreed byte oracle into an upstream-maintained
check. Retain the independent acceptance and equal-hash assertions. E1 does not
invent the target number spelling or algorithm-version transition policy.
Graduation requires a linked owning upstream change/documentation and execution
in its maintained CI/verification command; merely filing an issue is insufficient.
No upstream publication or contract change was performed. Retire duplicate local
runner maintenance after confirmed transfer, preserving these records.
