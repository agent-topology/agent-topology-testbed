# D1 — Published producer determinism

**Disposition: bounded non-finding.** On 2026-09-12, published beta.2 Python and
TypeScript LangGraph producers retained structure and the complete hash tuple for
every tested structure-preserving transformation. All seven structural positive
controls per language changed both structure and hash. There were **104 fresh
processes, 208 describes and 248 passing comparisons**, with no node-body execution.

This is [testbed #40](https://github.com/agent-topology/agent-topology-testbed/issues/40)
under [#37](https://github.com/agent-topology/agent-topology-testbed/issues/37).
Evidence class: **static extraction of compiled framework definitions**, with
**callable** public spec validation/canonical/hash checks. No graph is invoked;
this is not framework execution, scheduling evidence or release qualification.
The [findings index](../../findings/README.md#dispositions-and-unresolved-evidence)
links this explicit non-finding. Historical beta.2 evidence remains unchanged.

## Question, inputs and expected observations

Does a published producer preserve contract structure/hash under these narrowly
defined irrelevant changes? Measurement needs compiled definitions, not model calls,
execution state or arbitrary semantically equivalent programs.

The [recipes](../../probes/published-producer/recipes.json) and
[Python](../../probes/published-producer/worker.py) /
[TypeScript](../../probes/published-producer/worker.mts) builders were inspected
before framework installation. Each uses explicit IDs and fail-fast node bodies:

| Shape | Minimal input, excluding framework-owned START/END |
| --- | --- |
| linear | Two nodes: START → a → b → END |
| fanout | Two nodes: START → a and b; each → END |
| join | Three nodes: START → a and b; [a,b] → c as one join; c → END |

All compile with the same graph name `d1`, one unused string state channel and no
conditional routes, interrupts, subgraphs or model dependencies. All node bodies
raise `D1_NODE_BODY_EXECUTED`; successful extraction therefore supplies a fail-fast
check against accidental invocation. This does not establish behavior of every
possible callback or framework surface.

Before the first extraction, [plan.json](run/plan.json), [cases.json](run/cases.json)
and the exact [input files](run/inputs/) fixed the transformations and expectation:
all preserve structure/hash except the explicit positive controls. The verifier
also has independent literal node, edge, join, entry/exit and completeness oracles.
It never derives the expected connectivity by reading producer output.

## Per-transformation results

Each cell represents **two pairs in separately launched processes per shape per
language**. Every compiled graph is also described twice without rebuilding.
The [full comparison](verification/comparison.json) identifies language, shape,
transformation, repeat, structural differences and every raw-document difference.

| Transformation | Shapes | Python | TypeScript |
| --- | --- | --- | --- |
| Describe the same compiled object twice | all 26 cases | 52 pairs stable | 52 pairs stable |
| Rebuild identical input in a fresh process | all 26 cases | 26 pairs stable | 26 pairs stable |
| Reverse node declarations only | all three | 6 pairs stable | 6 pairs stable |
| Reverse ordinary edge declarations only | all three | 6 pairs stable | 6 pairs stable |
| Reverse dictionary insertion order | all three | 6 pairs stable | 6 pairs stable |
| Change an unrelated source comment | all three | 6 pairs stable | 6 pairs stable |
| Replace lambda/arrow with named callable | all three | 6 pairs stable | 6 pairs stable |
| Reverse sources within the multi-source join | join | 2 pairs stable | 2 pairs stable |
| Rename node a to renamed, including its references | all three | 6 pairs distinct | 6 pairs distinct |
| Add one ordinary edge | all three | 6 pairs distinct | 6 pairs distinct |
| Replace the join with two independent incoming edges | join | 2 pairs distinct | 2 pairs distinct |

The dictionary experiment reverses `{alpha: one, beta: two}` insertion order in
node metadata passed to `add_node` / `addNode`; values and node declarations stay
fixed. It does not claim coverage of state-schema, router path-map or every other
dictionary surface. Input SHA-256 values preserve the differing JSON bytes.

The source-comment variant changes only `D1_UNRELATED_COMMENT` in the actual worker
source executed at the same path, not a recipe field pretending to be a comment.
[Saved workers](run/workers/) retain both exact source versions; the audit checks
that the replacement changes nothing else. Recipe bytes are identical to baseline.

The named-callable variant uses `named_step` / `namedStep` in place of the
lambda/arrow while keeping every explicit node ID and connection. Neither emitted
`type`, `subgraphId` nor `interrupts`; node core records remain `{id: ...}` in both
versions. No public structural property changed. This result is about these
fail-fast callables with explicit identity, not an equivalence proof for arbitrary
functions, inferred node names, wrappers or compiled child graphs.

The extra edge is a → END for linear/join, and a → b for fanout. Renaming preserves
connectivity up to the deliberate new ID, which itself is hash-covered. The join
control replaces one `[a,b] → c` join with `a → c` and `b → c` edges; it retains all
node IDs. Independent oracles check exact connectivity and collection multiplicity,
so a constant producer or a hasher ignoring real changes cannot pass.

## Comparison and drift classification

The contract-covered projection retains graph IDs; node IDs, types, subgraph IDs
and interrupts; edge IDs, endpoints and kinds; join IDs, sources and targets; and
entry/exit IDs. Only contract-defined unordered collections and object keys are
sorted. No collection is deduplicated and no IDs, repr strings or addresses are
scrubbed. All observed non-extension structural fields are retained. An independent
SHA-256 over that projection must equal both the emitted tuple and the public spec
API's recomputation (`sha256`, algorithmVersion `1`, value).

An unequal projection is **extraction drift**; equal projection with unequal hash
is **hash computation drift**. Deliberate control changes are labeled
`expected-structural-change`. Changes to excluded fields remain visible in
`rawDifferences`, rather than being treated as structural drift. Provenance,
timestamps, graph names, limitations, completeness and `x-*` metadata are preserved
in every raw document. Runtime, process ID, executable/import paths and input digest
are recorded outside the document. Full canonical strings are retained separately.

All invariant comparisons differed only at `/provenance/generatedAt` when they
differed at all. No process-address, repr or generated-ID leak was observed in
structure **or other document fields** in these cases. No unexpected type or
connectivity change was normalized away. There was no extraction or hash drift to
minimize, and no algorithm transition. Cross-language equality is not a D1 oracle;
each language is assessed independently.

## Environment and raw evidence

Python **3.14.7**, Node **22.16.0**, npm **11.4.1**, macOS **26.5.2 ARM64**.
Python uses `-I` and a fresh venv. TypeScript uses native Node type stripping
(`--experimental-strip-types`) on `.mts`, with public bare ESM imports resolved
inside its isolated npm installation. It is runtime-tested TypeScript, not a claim
of a separate TypeScript compiler check. No workspace package import is used.

| Registry package | Exact version | Artifact SHA-256 |
| --- | --- | --- |
| Python producer | 0.1.0b2 | `a6926ef43af0a48a34ab2d29d24f3fa6d257bdd0aa0e84ee24897463ea009d16` |
| Python spec | 0.1.0b2 | `14aa6083e5d32dbec527ccb9422e91d99f4415c3d3b0a30d5677f108401a8873` |
| npm producer | 0.1.0-beta.2 | `4a13dfe6b5044ae7754708dbdf30ff0cf9f7baccabeb543ed13677311f9daeb1` |
| npm spec | 0.1.0-beta.2 | `373fbb08548ebcf8d62abb952b5f1e711be3d2616579cbe86e8c30f89e8aa9bc` |

Frameworks are pinned to Python **LangGraph 1.2.11** and **LangGraph.js 1.4.14**.
[Installed metadata](setup/installed-metadata.json) and the
[pip report](setup/pip-report.json) record runtime/dependency declarations:
Python supports 3.11–3.14 and LangGraph 1.2.10–1.2.11; npm requires Node 20+ and
pins LangGraph.js 1.4.14. D1 measures only the exact environment above, not the full
supported matrix. [Transitive locks](../../probes/published-producer/locks/) pin
every installed application dependency. Python wheel hashes and npm lock SRI are
independently checked against downloaded artifact bytes; [artifacts.json](setup/artifacts.json)
retains URLs and SHA-256 for every transitive artifact. The spec artifact hashes
match V1/E1; artifact digest is distinct from a document's structureHash.

- [Setup commands](setup/commands.json): actual commands, cwd, UTC starts, exits,
  stdout/stderr; all succeeded. Setup subprocess time: **8.80 seconds**, excluding
  HTTP artifact verification and orchestration.
- [Run commands](run/commands.json): all 104 process commands and unmodified stdout,
  stderr and exits. Each `run/<language>-<case>-<repeat>.json` also retains the exact
  stdout with both full documents, canonical strings, hashes and import identity.
- [Run provenance](run/provenance.json): source/lock digests, platform, completion
  time; **36.63 seconds** of extraction subprocess time, including process startup.
- [Verification commands](verification/commands.json): optimized-Python saved-data
  audit and **8 passing control tests**. Controls cover hash-only drift, leaked
  repr identity, duplicate edges, metadata visibility, corrupted actual hash,
  missing evidence, incorrect installed versions and constant-output controls.
  The corrupted-hash CLI test explicitly checks exit **1** under `python -O`.
- [Verification sources](verification/sources.json): final audit source hashes.
  The saved run's original source hashes and comparison are preserved; subsequent
  audit strengthening added process/runtime and comment-source checks without
  rerunning producers or rewriting raw evidence. Both comparisons report 248 passes.

## Existing coverage, disposition and handoff

[Source references](source-references.json) pin all inspected upstream files to
`eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`; the [snapshots](source/) retain their bytes.
The [spec declaration-order tests](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/spec/tests/test_canonical.py)
already reverse document collections and test descriptive exclusion, real structural
changes and join/independent distinction. The
[consumer-regression tests](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/tests/test_consumer_regression.py)
and [coverage explanation](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/conformance/consumer/README.md)
already compile forward/reversed recipes with fail-fast bodies, compare producer
documents after clock normalization, test join distinctions and experimental
interpretation. Those are **current-source** tests; beta.2 package metadata in that
checkout does not make them tests of registry beta.2 experimental output.

D1 adds **published-artifact** evidence for isolated node/edge permutations, repeated
describes of one compiled object, fresh-process reconstruction, dictionary insertion
order, actual source comments and named-callable substitution with explicit IDs.
The positive controls reinforce existing coverage; they are not presented as new
upstream discoveries. V1/E1 measure spec documents, not producer extraction.

**No new finding ID is warranted.** The measured cases support bounded determinism
and preserve the contract's real distinctions. They change no upstream contract,
historical receipt or existing finding disposition. No decisive evidence is missing
for this bounded question. Other runtime/platform versions, implicit names, routers,
subgraphs, interrupts, larger programs and arbitrary semantic equivalence remain
untested scope, not a blocked setup or a request for speculative broad reruns.

Suggested owner: upstream LangGraph producer maintainers, using the linked
[Python conformance suite](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/langgraph/tests/test_conformance.py)
and [TypeScript producer suite](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/typescript/langgraph/tests/producer.test.mjs).
The smallest additional handoff candidate is the two-node explicit-ID linear
builder with two describes and a fresh-process named/comment/order pair, retaining
the hash oracle and one structural positive control. Preserve the join control if
that coverage moves out of the existing suite. **Not posted or graduated:** transfer
requires an upstream-owned change/documentation link and execution in a maintained
check or CI. An issue alone is insufficient. Retire duplicate local maintenance
after confirmed adoption while preserving these raw records.

## Reproduce

Inspect the small recipes, workers and locks first. Use fresh directories; setup
and run refuse to overwrite existing environment/evidence directories. From repo root:

```bash
rtk proxy python3 probes/published-producer/setup.py --envs .probe-runs/D1/repro-envs --out .probe-runs/D1/repro-setup
rtk proxy python3 probes/published-producer/run.py --envs .probe-runs/D1/repro-envs --out .probe-runs/D1/repro-run
rtk proxy python3 -O probes/published-producer/verify.py observations/D1/run --report .probe-runs/D1/audit.json
rtk proxy python3 -O -m unittest discover -s probes/published-producer -v
```

All four commands should exit 0. The run already executes every case twice in
fresh processes and every compiled graph twice; no additional broad repeat is
needed. Initial capture used `setup.py --resolve` once to establish the committed
locks. Reproduction consumes them with `pip --require-hashes` and `npm ci`.
Setup/API failures and missing evidence produce nonzero failures, never a passing
non-finding. Only these isolated D1 checks were run; no renderer or other framework
suite is relevant to this change.
