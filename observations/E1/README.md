# E1 — Generated published Python/TypeScript canonicalization

**Disposition: reproduced full-document serialization gap, [F8](../../findings/F8-extension-number-canonicalization/README.md); bounded structure-hash non-finding.**
On 2026-09-12, 42 of 300 generated base documents produced different canonical
UTF-8 bytes in published Python `0.1.0b2` and npm `0.1.0-beta.2`. Their structural
permutations reproduced the differences: 84 of 600 comparisons per run. All
inputs were accepted by both packages; all full hash tuples agreed. The smallest
retained candidate has one empty graph and `"x-e1":0.0`: Python emits `0.0`,
JavaScript emits `0`. Extensions are excluded from the structure hash.

This is retrospective **callable** evidence for [#39](https://github.com/agent-topology/agent-topology-testbed/issues/39)
under [#37](https://github.com/agent-topology/agent-topology-testbed/issues/37),
reusing [V1's](../V1/README.md) published-package locks, public APIs and unchanged
one-shot adapters. It is not framework execution or release qualification.

## Question, minimal inputs and pre-run expectations

Do the published beta.2 implementations agree beyond handwritten fixtures?
The input is JSON, not producers, framework definitions or arbitrary JavaScript
objects. Hypothesis generates 1–2 graphs, 0–3 nodes per graph, 0–2 edges and
0–2 joins. Empty required arrays stay present; each join has at least two unique
sources. Definitions have unique IDs within their graph/kind scope; references,
subgraph IDs and completeness gaps resolve. A gap refers to an existing graph;
complete/incomplete status follows gap cardinality. Optional graph names, node
types, interrupts, subgraph references, source provenance and extensions vary.
The supplied hash value is a schema-valid placeholder, not an expected hash;
the measurement compares the separately computed complete tuples.

Before running, the oracles were: independently valid generated inputs remain in
the population even if one package rejects them; acceptance, full canonical bytes,
and full hash tuples are separate observations; canonicalization and hashing do
not mutate inputs, are idempotent, and are invariant under reversal of the
contract's unordered structural collections. Extension/descriptive array order
is preserved. No NFC/NFD equivalence is asserted. API/setup failures cannot pass.

[Generator](../../probes/published-spec/generated/generate.py) uses an independent
Draft 2020-12 schema validator with date-time checking plus explicit reference,
ID and completeness checks. The copied [schema](../../probes/published-spec/generated/schema.json)
has SHA-256 `6e98d8b829e9cd3558499abfc2943335d4d0564d21ae1706a0797df4159bf006`,
identical to V1's schema and the pinned upstream source. Invalid shrink proposals
are rejected locally before either adapter; missing required arrays and other
invalid mutations occur only in control tests, outside the parity population.

Numbers occur only in schema-permitted `x-e1` payloads on documents/nodes.
The numeric domain is integers −100…100 and finite binary64 values `0.0`, `-0.0`,
`1.0`, `0.5`, `1e-7`, `1e-6`, `1e20`. There are no NaNs, infinities, surrogate
code points, arbitrary-precision integer probes, or invented numeric core fields.
Payload nesting is bounded by six leaves; text length is 1–4 Unicode scalars.

## Existing coverage and the increment

[Source references](source-references.json) pin inspection to upstream
`eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`, not moving main. Its
[TypeScript contract tests](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/typescript/spec/tests/contract.test.mjs)
already compare fixture canonical bytes/hashes with Python and explicitly test
U+E000 versus U+10000 in nodes, join sources and entry/exit IDs. Its
[Python tests](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/spec/tests/test_canonical.py)
already check declaration-order invariance, non-mutation, descriptive exclusion,
structural positive controls and algorithm versions. V1 added nine fixed inputs
across four registry installations. E1 adds combinations of those dimensions,
combining characters, composed characters as distinct strings, quotes/backslashes,
optional presence/absence, nested extension objects/arrays and finite numbers,
using identical serialized input bytes in two published beta.2 environments.
It does not claim the existing Unicode boundary test was missing.

The [canonical contract](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/0.1-contract.md#canonical-form)
specifies sorted structural collections and recursive object keys, UTF-8 and no
insignificant whitespace, and says both packages implement the same form. It does
not select a number spelling or require Unicode normalization. The observed
number-spelling divergence is an interoperability/coverage gap; choosing the
normative spelling and transition policy remains an upstream decision.

## Runs, coverage and retained evidence

Python **3.14.7**, Node **22.16.0**, npm **11.4.1**, macOS ARM64.
Hypothesis **6.168.0**, jsonschema **4.26.0** and all their dependencies are
[locked separately](../../probes/published-spec/generated/requirements.lock)
from V1's spec environments. No framework or producer is installed.
[Initial setup](setup-commands.json) records resolution and installation;
[lock-only setup](locked-setup/commands.json) reproduces three isolated environments.
[Verified artifacts](locked-setup/artifacts.json) retain registry URLs/digests,
including transitive dependencies. Both beta.2 artifact digests match V1.

| Seed | Base examples | Canonical differences in bases |
| --- | ---: | ---: |
| 39 | 100 | 20 |
| 20260912 | 100 | 13 |
| 103 | 100 | 9 |

Each run contains 300 base examples plus 300 structural reversals. Hypothesis uses
`Phase.generate`, `database=None`, `deadline=None`, `max_examples=100` per seed;
no acceptance-based filtering occurs. It may repeat a document: this is **300
examples, not a claim of 300 unique topologies**. Each run uses two persistent
processes and caches identical bytes, including shrink evaluations. There are
3,264 distinct evaluated inputs per language, not one process launch per input.

[Run A summary](run-a/summary.json) reports **13.89 seconds**;
[run B](run-b/summary.json), in fresh lock-only environments, reports **14.00 seconds**.
Setup cost is separate in the command logs. Run B regenerates the fixed seeds;
all 600 serialized population lines and all 3,264 paired evaluation records
reproduce. The audit ignores only installation/executable paths when comparing
identities; versions and runtime versions remain compared. Canonical strings,
hash tuples, validation and property results are never normalized.

| Generated dimension | Base documents exercising it |
| --- | ---: |
| Non-ASCII BMP / supplementary scalars | 254 / 241 |
| Combining U+0301 | 186 |
| Escaped quote / backslash | 256 / 228 |
| Extension payload / float / integer | 198 / 42 / 61 |
| Optional graph name present / absent | 155 / 196 |
| Nontrivial structural reversal | 211 |

Counts overlap. Alphabet categories and optional names are coverage indicators,
not exhaustive coverage of Unicode or every permitted optional field.

For each `run-a/` and `run-b/`:

- `inputs.jsonl.gz` retains all 600 exact serialized input lines in `cases.json`
  order. The newline is part of the hashed bytes. Python and Node receive those
  same UTF-8 bytes; Node's line adapter restores exactly that newline.
- `cases.json` records seed, index, variant, input SHA-256 and separate mismatch
  classes, including any one-sided or both-sided rejection.
- `evaluated-inputs.jsonl.gz` and `batch-0.jsonl.gz` / `batch-1.jsonl.gz` retain
  **every unique evaluation**, including shrink inputs and full raw adapter output,
  aligned by line and checked by digest. Identity includes the exact import path.
- `batch-commands.json` records commands, process exits, stderr, call count and
  duration. `summary.json` records source hashes, versions, seeds and search limits.
- `failures.json` maps each failing base/permutation to its reduced candidate,
  attempts and stopping reason. `minimized/*.json` retains exact candidate bytes;
  corresponding `*-replay.json` retains fresh, unchanged V1 adapter commands,
  stdout/stderr, exits and durations. All 16 distinct candidates replay per run.

[Numeric diagnosis](numeric-diagnosis.json) confirms all 84 population differences
are number-spelling-only: replacing only unquoted JSON number tokens with equal
Decimal forms makes the strings match. This is post-run diagnosis, never a
normalization applied to the parity oracle.

All 84 failures were shrunk separately, with byte-cache reuse and content-addressed
candidate deduplication. The deterministic shrinker tries tree deletion, container
collapse and scalar simplification; it accepts only independently valid inputs
that retain the same mismatch classification. Limit: 300 valid candidate attempts
per failing input. All reached a local fixed point; none exhausted the limit.
These are minima under the stated reductions, **not globally minimal JSON proofs**.
Hypothesis generates inputs; this explicit validity-preserving reducer shrinks them.

Two earlier captures are preserved as `run-1-preliminary.tar.gz` and
`run-2-preliminary.tar.gz`, with per-file digests in [the archive manifest](preliminary-archives.json).
They found the same 42 base differences. Run 1 predates container-collapse shrinking
and retained 21 candidates, and lacks a complete shrink-input byte archive;
run 2 added that archive and reduced to 16. Runs A/B are the authoritative complete
repeat after input-stream archival and explicit numeric coverage were added.
No historical V1, beta.2 receipts, transcripts or gallery artifacts were changed.

## Verification, impact and handoff

[Verification commands](verification-commands.json) record the optimized-Python
saved-evidence audit, ten deterministic generated-runner controls and V1's seven
existing comparator controls. A deliberately altered **actual recorded adapter
hash** is retained in `controls/altered-pair.json`; the pair comparator exits **1**
and reports only `structure-hash`. The actual unaltered minimal pair separately
exits **1** for `canonical`. Measurement completion is not a claim of parity.

There were zero one-sided rejections, both-sided rejections, hash disagreements,
algorithm transitions, non-mutation/idempotence failures or structural-order
failures. Float spelling differences concern full-document bytes; the core hash
projection has no numeric fields and excludes these extensions. No qualification
receipt or artifact digest is invalidated by this result. V1's nine inputs remain
passing and its bounded result is unchanged.

The supported local finding is [F8](../../findings/F8-extension-number-canonicalization/README.md),
[indexed separately](../../findings/README.md). Consumers comparing full canonical
bytes across these packages must account for the demonstrated gap; this evidence
supplies no reason to treat equal structure hashes as unequal. The minimum next
step is an upstream spec-maintainer decision on numeric spelling and a maintained
cross-language regression using the retained candidate. Existing contract-suite
links above identify the proposed owning code. **Not graduated or posted:**
graduation requires an upstream owning change/documentation link and execution in
its maintained check/CI. Once transferred, retire duplicate runner maintenance
while preserving evidence. No external adoption or release gate is implied here.

Passing the remaining 258 base documents is bounded coverage, not equivalence
proof. Larger graphs, other numbers/Unicode scalars/optional combinations,
platforms/runtimes, producer behavior and future versions remain untested.

## Reproduce

Inspect `generate.py`, the small schema and locks before installation. Use new
paths for every setup/run; commands refuse existing output/environment directories.
From the repository root:

```bash
rtk proxy python3 probes/published-spec/generated/setup.py --envs .probe-runs/E1/repro-envs --out .probe-runs/E1/repro-setup
rtk proxy .probe-runs/E1/repro-envs/generator/bin/python -O probes/published-spec/generated/run.py --envs .probe-runs/E1/repro-envs --out .probe-runs/E1/repro-a
rtk proxy .probe-runs/E1/repro-envs/generator/bin/python -O probes/published-spec/generated/run.py --envs .probe-runs/E1/repro-envs --out .probe-runs/E1/repro-b
rtk proxy .probe-runs/E1/repro-envs/generator/bin/python -O probes/published-spec/generated/verify.py .probe-runs/E1/repro-a .probe-runs/E1/repro-b
rtk proxy .probe-runs/E1/repro-envs/generator/bin/python -O -m unittest discover -s probes/published-spec/generated -v
rtk proxy python3 -O -m unittest discover -s probes/published-spec -v
rtk proxy .probe-runs/E1/repro-envs/generator/bin/python -O probes/published-spec/generated/verify.py --pair observations/E1/controls/altered-pair.json
```

The last command must exit 1; the others must exit 0. Run commands record
mismatches without turning a completed measurement into a parity claim;
`verify.py --pair` is the strict, nonzero differential comparator.
