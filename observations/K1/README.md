# K1 — Published consumer compatibility boundaries

**Disposition: bounded non-finding.** On 2026-09-12, all seven cases (six document
mutations plus one direct hash-computation call) produced exactly their
independently recorded, before-extraction expected outcome in all four published
spec installations, across two independent fresh-process runs (28 rows per run,
zero mismatches both times; 56 adapter/hash-adapter calls per run). A deliberately
corrupted oracle produces a nonzero comparison exit.

This is retrospective **callable** evidence for testbed [#41](https://github.com/agent-topology/agent-topology-testbed/issues/41)
(local planning ID K1), under [#37](https://github.com/agent-topology/agent-topology-testbed/issues/37).
It is neither framework execution nor release-time qualification. It reuses
[V1](../V1/README.md)'s isolated installations and adapters and V1's minimal
accepted document; it does not re-verify V1's own hash-stability claim, and it
does not repeat E1's generated-input canonicalization search.

## Question and minimal input

Do the published beta.1/beta.2 public spec APIs implement their versioned
compatibility obligations for an unsupported document-format version, an
unsupported declared hash-algorithm version, an out-of-range hash-computation
request, and `x-*` extension keys -- both where the schema permits them and where
it does not? The measurement needs one base document and seven single-purpose
calls per installation, not producers, framework environments or graph
executions.

Every document case is [V1's minimal input](../V1/inputs/minimal.json) — one
graph, zero nodes/edges/joins/entries/exits, already recorded as accepted by all
four installations — with exactly one controlled change. `x-*` mutations use a
string value, deliberately avoiding [F8](../../findings/F8-extension-number-canonicalization/README.md)'s
already-recorded numeric-canonicalization gap, which this issue does not retest.

## Obligation table (source-linked, fixed before extraction)

Pinned upstream inspection: beta.1 source revision
`0e127d84d77904dd0a909fab0ea58862282ceae8` (peeled `v0.1.0-beta.1` annotated tag
`a7eedef253514142a4c70f7fdcb1ece78806f1e8`, the same revision V1 used) and beta.2
prep revision `eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe` (the same revision V1 and
F8 used). `agent-topology.schema.json`, `_validation.py` and
`packages/typescript/spec/src/validation.ts` are byte-identical between these two
revisions; `_canonical.py` is also byte-identical. `packages/typescript/spec/src/canonical.ts`
differs only in `join.sources`/`entryNodeIds`/`exitNodeIds` sort (a code-point
`compareText` comparator in the beta.2 revision vs. the JS engine's default
`.sort()` in the beta.1 revision) — every K1 document has empty arrays in all
three fields, so this difference cannot fire here and is not exercised by any K1
case. It is an independent literal fact noticed while building this table, not a
K1 finding; it belongs to a different comparison (non-empty, order-sensitive
collections) that K1 does not run.

| # | Obligation | Source | Expected outcome |
| --- | --- | --- | --- |
| 1 | `topologyVersion` must equal the schema `const` `"0.1"` | [schema `$.properties.topologyVersion`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/agent-topology.schema.json) | A document declaring `"0.2"` is rejected by `validate_document`/`validateDocument` (schema-shape rejection), identically in beta.1 and beta.2, identically in Python and TypeScript |
| 2 | `structureHash.algorithmVersion` must equal the schema `const` `"1"` | [schema `$defs.structureHash.properties.algorithmVersion`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/agent-topology.schema.json) | A document whose **declared** `structureHash.algorithmVersion` is `"2"` is rejected by `validate_document`/`validateDocument` (schema-shape rejection), identically across all four installations |
| 3 | `compute_structure_hash`/`computeStructureHash` accepts an explicit `algorithm_version` and raises on an unsupported value | [`_canonical.py:117-144`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/spec/src/agent_topology/spec/_canonical.py), [`canonical.ts:134-149`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/typescript/spec/src/canonical.ts); [ADR 0003](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/docs/decisions/0003-canonical-ordering-and-versioned-structure-hash.md) ("refused rather than silently producing a different answer") | Calling the hash function directly with `algorithm_version="2"` on the (otherwise valid, unmutated) baseline document — bypassing `validate_document` entirely — raises `ValueError` in Python and `RangeError` in TypeScript, in both beta.1 and beta.2. This is the **hash-computation** boundary, distinct from obligation 2's **structural-validation** boundary: the schema check happens on a document's own declared field; this check happens on an explicit function argument that never reaches the schema at all |
| 4 | Unknown keys matching `^x-[a-z0-9][a-z0-9._-]*$` are permitted wherever a `$def` declares that `patternProperties` entry (document root, `provenance`, `namedVersion`, `producerLimitation`, `structureHash`, `graph`, `graphStructure`, `node`, `edge`, `join`, `completeness`, `gap`) | [schema, every `$def` except `elementReference`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/agent-topology.schema.json); [0.1-contract.md "optional producer or framework facts only under lower-case, namespaced `x-*` keys"](../D1/source/docs/0.1-contract.md) | A document-root key `x-k1-probe` is accepted, identically across all four installations |
| 5 | `completeness.gaps[].element` (the `elementReference` `$def`) is the one object in the schema with `additionalProperties: false` and **no** `patternProperties` `x-*` allowance | [schema `$defs.elementReference`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/agent-topology.schema.json) | The same key name (`x-k1-probe`) that obligation 4 accepts at the document root is rejected inside `completeness.gaps[0].element`, identically across all four installations. This is the placement boundary, independent of the key-shape boundary in obligation 6 |
| 6 | An extension-shaped key that does not match `^x-[a-z0-9][a-z0-9._-]*$` is not an extension at all under `additionalProperties: false` | [schema `patternProperties` regex, every `$def`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/spec/agent-topology.schema.json) | `X-k1-probe` (capital `X`) at the document root is rejected, identically across all four installations, even though the document root otherwise permits extension keys |
| 7 | Hash version 1 excludes extensions from what it hashes | [0.1-contract.md "Structure-hash coverage": "It excludes ... extensions ..."](../D1/source/docs/0.1-contract.md); confirmed by [F8](../../findings/F8-extension-number-canonicalization/README.md) | Adding `x-k1-probe` at the document root does not change `structureHash.value` versus the unmutated baseline, in any of the four installations, because `_structure_projection_v1`/`projectStructureV1` read only `document["graphs"]`/`document.graphs` |
| 8 | Canonical output is a projection of the *whole* document, not just the hashed fields; core data (including extensions) survives round-trip | [`canonicalize_document`/`canonicalizeDocument`, `_canonical.py:37-61`, `canonical.ts:74-94`](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/spec/src/agent_topology/spec/_canonical.py) | `canonical_json`/`canonicalStringify` of the accepted extension case contains `"x-k1-probe":"case-4-string-value"` verbatim, byte-identically in Python and TypeScript output for this string-valued case |

**Documentation gap, not an implementation defect:** obligation 3's function
signature and error behavior are established only by reading the source and by
the general principle in ADR 0003 ("a version outside the tested range is
refused rather than silently producing a different answer," stated there about
the LangGraph library range, not literally about `algorithm_version`); neither
`0.1-contract.md` nor the package READMEs document the `algorithm_version`
parameter or its exception type in prose. K1 records this as a gap in published
documentation, separate from and not evidence of any implementation defect — the
implementation matches the general principle exactly, in both languages.

**Opt-in extension interpretation is out of scope for this issue and does not
exist in the published spec-package public API.** The complete Python export
list (`__init__.py`: `validate_document`, `canonical_json`,
`canonicalize_document`, `compute_structure_hash`, `finalize_document`,
`derived_join_edges`, `load_schema`) and the equivalent TypeScript `index.ts`
exports contain no function that reads or interprets `x-*` *content*; the spec
packages only decide accept/reject (obligations 4-6) and exclude extensions from
the hash (obligation 7). This testbed's own `instrument/` renderer separately
reads some `x-*` keys behind an explicit, non-published flag (see the root
[README](../../README.md#instrument)), which is a local, non-published consumer
outside "the actual public APIs" this issue measures. K1 does not claim, and does
not test, that any published beta.1/beta.2 package interprets an extension it
does not implement.

## Cases and independent, before-extraction expectations

[`cases.json`](cases.json) fixes all seven expected outcomes, authored from the
obligation table above before any adapter ran; [`cases/`](cases) holds the six
mutated document bytes, each produced by exactly one [`mutate.py`](../../probes/published-consumer/mutate.py)
function. `run.py` regenerates every document from `mutate.py` and requires its
bytes and SHA-256 to match the committed copy before installing anything.

| Case | Change from the minimal document | Expected | Obligation |
| --- | --- | --- | --- |
| `baseline` | none (control) | accepted; hash `16e9f78b...7cb8421` (V1's oracle) | — |
| `unsupported-topology-version` | `topologyVersion`: `"0.1"` → `"0.2"`. **Synthetic unsupported-version input, not a real or future release** — `0.2` names no upstream milestone | rejected | 1 |
| `unsupported-hash-algorithm-version-declared` | `structureHash.algorithmVersion`: `"1"` → `"2"`, declared in the document. **Synthetic algorithm-version mutation**, not a claim about a real transition | rejected | 2 |
| `unknown-permitted-extension` | add `x-k1-probe: "case-4-string-value"` at the document root | accepted; hash unchanged from baseline | 4, 7, 8 |
| `invalid-extension-placement` | the identical key `x-k1-probe` (value `"case-5-should-be-rejected"`), placed inside a synthetic `completeness.gaps[0].element` instead of the document root; `completeness.status` flips to `"incomplete"` only because a `gaps` entry requires it — that flip is scaffolding, not a second claim under test | rejected | 5 |
| `malformed-extension-key` | add `X-k1-probe: "case-6-should-be-rejected"` (capital `X`) at the document root | rejected | 6 |
| `hash-computation-unsupported-algorithm-version` | no document change; calls `compute_structure_hash(baseline, algorithm_version="2")` / `computeStructureHash(baseline, "2")` directly, never calling `validate_document`/`validateDocument` | raises `ValueError` (Python) / `RangeError` (TypeScript) | 3 |

## Installations and raw evidence

Python **3.14.7**, Node **22.16.0**, npm **11.4.1**, macOS ARM64 — the same
runtime versions V1 recorded. Each of the four installations
(`py-b1`=`agent-topology-spec==0.1.0b1`, `py-b2`==`0.1.0b2`,
`js-b1`=`@agent-topology/spec@0.1.0-beta.1`, `js-b2`=`@agent-topology/spec@0.1.0-beta.2`)
is a fresh venv or npm project, installed with `pip --require-hashes` / `npm ci`
against **V1's own committed locks** (`probes/published-spec/locks/`) — K1 pins
no second, independently drifting copy of the same four packages. No local
source build, producer or framework is installed.

| Installation | Published artifact SHA-256 (independently re-verified by this run) |
| --- | --- |
| Python 0.1.0b1 wheel | `fd0f832969a3cb93547c30e4416d6242f6bf5115826f523504788bda7f46750b` |
| Python 0.1.0b2 wheel | `14aa6083e5d32dbec527ccb9422e91d99f4415c3d3b0a30d5677f108401a8873` |
| npm 0.1.0-beta.1 tgz | `bb1867d35c78bf84dc06bf0e9f6fa7fb343724e7b16171b4b2b1445309c657ca` |
| npm 0.1.0-beta.2 tgz | `373fbb08548ebcf8d62abb952b5f1e711be3d2616579cbe86e8c30f89e8aa9bc` |

These four SHA-256 values are identical to the ones V1 recorded — the same
published artifacts, reinstalled independently and reverified, not reused as a
cached environment. [`run/artifacts.json`](run/artifacts.json) has the full list
including transitive dependencies.

`adapter.py`/`adapter.mjs` (V1's, unchanged, copied verbatim into each
installation) exercise obligations 1, 2, 4, 5, 6, 7 and 8 through
`validate_document`/`validateDocument` and `canonical_json`/`canonicalStringify`
and `compute_structure_hash`/`computeStructureHash` with default arguments.
`hash_adapter.py`/`hash_adapter.mjs` (new; also copied into each installation)
exercise obligation 3 by calling `compute_structure_hash`/`computeStructureHash`
directly with an explicit `algorithm_version` argument, never calling
`validate_document`/`validateDocument`. Exit 0 means accepted/computed, 2 means
validation rejection, 3 means a raised exception (adapter API error and the
hash-computation-boundary case share exit 3, since both are "the call raised,"
not "the document was structurally rejected" — [`run/comparison.json`](run/comparison.json)
keeps the two cases in separate rows regardless).

[`run/commands.json`](run/commands.json) has every setup/adapter command, cwd,
UTC start, duration, exit, stdout and stderr; individual
`run/<installation>-<case>-<repeat>.json` files hold full adapter responses.
[`run/identities.json`](run/identities.json) and [`run/provenance.json`](run/provenance.json)
retain exact executable/import paths, runtime versions, source/lock SHA-256 and
9.55 seconds of subprocess time for this run. [`run/comparison.json`](run/comparison.json)
lists all 28 rows (6 document cases × 4 installations + 1 hash-boundary case ×
4 installations): zero mismatches.

[`reproduction/`](reproduction) is a second, fully independent run — fresh
venvs/npm projects, fresh registry downloads, fresh digest reverification — using
the same committed locks. Its [`comparison.json`](reproduction/comparison.json)
matrix is byte-identical to `run/comparison.json`: 28/28 rows, zero mismatches.

## Compatibility matrix

Every cell below reads "installation behavior vs. this case's recorded
expectation." All 28 cells matched in both runs; none of the four installations
diverged from any other on any case.

| Case | py-b1 | py-b2 | js-b1 | js-b2 |
| --- | --- | --- | --- | --- |
| `baseline` | accepted, hash matches | accepted, hash matches | accepted, hash matches | accepted, hash matches |
| `unsupported-topology-version` | rejected (schema `const`) | rejected (schema `const`) | rejected (schema `const`) | rejected (schema `const`) |
| `unsupported-hash-algorithm-version-declared` | rejected (schema `const`) | rejected (schema `const`) | rejected (schema `const`) | rejected (schema `const`) |
| `unknown-permitted-extension` | accepted, hash unchanged | accepted, hash unchanged | accepted, hash unchanged | accepted, hash unchanged |
| `invalid-extension-placement` | rejected (`elementReference` `additionalProperties`) | rejected (`elementReference` `additionalProperties`) | rejected (`elementReference` `additionalProperties`) | rejected (`elementReference` `additionalProperties`) |
| `malformed-extension-key` | rejected (pattern mismatch) | rejected (pattern mismatch) | rejected (pattern mismatch) | rejected (pattern mismatch) |
| `hash-computation-unsupported-algorithm-version` | `ValueError` | `ValueError` | `RangeError` | `RangeError` |

The two rejection cases carry different literal `jsonschema`/`ajv` error message
text between Python and TypeScript for the same underlying violation (for
example, `invalid-extension-placement` reports `"Additional properties are not
allowed ('x-k1-probe' was unexpected)"` in Python and `"must NOT have additional
properties"` in TypeScript, both at `$.completeness.gaps[0].element`). Message
text is validator-library phrasing, not part of any documented contract; this
matrix compares accept/reject status and, for accepted cases, the hash tuple and
canonical bytes — not error prose.

## Classification and controls

Cases are read as three independent obligations, not folded together: a
document's own declared version fields are checked by **structural validation**
(obligations 1, 2) before canonical serialization or hashing ever run; an
explicit `algorithm_version` argument bypassing validation is checked by **hash
computation** (obligation 3) with no schema involved at all; extension *content*
is never interpreted by either package (documented above, not re-tested per
case). `invalid-extension-placement` and `unknown-permitted-extension` use the
identical key name so that the only variable between the two cases is location,
isolating the placement claim (obligation 5) from the pattern claim (obligation
6, tested separately with a different, malformed key at the same permitted
location).

[Corrupted expected hash](controls/corrupted-expected.json) changes only the
recorded oracle for `baseline` to 64 zeroes; the real saved records are
unchanged. [`compare.py`](../../probes/published-consumer/compare.py) run
against it exits **1** and records exactly four mismatches (one per
installation) in [`controls/corrupted-comparison.json`](controls/corrupted-comparison.json).
[`probes/published-consumer/test_compare.py`](../../probes/published-consumer/test_compare.py)
additionally exercises, on temporary copies of the real saved records: an
accepted-case hash drift, a rejection flipped to acceptance, the
hash-computation error type drifting between languages, the hash-computation
call silently "recovering" a value instead of raising, a missing fresh-process
repeat, a fresh-process disagreement, and a wrong package identity — nine
controls in total (eight synthetic plus the real, zero-mismatch matrix), none of
which are observations of package behavior.

## Impact, existing coverage and handoff

No disagreement needs minimization and no new finding ID is allocated. All seven
before-extraction expectations held, identically in both languages and both
package generations, across two fully independent installations. This does not
prove the same for every possible document, `x-*` value type, schema location
this issue did not enumerate, runtime, platform, dependency resolution, producer
output or later release; in particular, it does not retest F8's numeric
canonicalization gap (deliberately avoided by using string extension values) or
V1's own nine-fixture hash-stability claim.

Pinned upstream inspection at `eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe` already
includes the [TypeScript contract tests](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/typescript/spec/tests/contract.test.mjs),
which assert unsupported-algorithm rejection, and the
[Python canonical suite](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/python/spec/tests/test_canonical.py).
Neither suite, as inspected, enumerates the `topologyVersion` `const` rejection,
the extension-placement-vs-pattern split (obligations 4-6), or a direct
cross-language `algorithm_version` error-type comparison against real
registry-installed packages; K1's incremental candidate is that narrow
three-way extension-legality split (permitted location + valid pattern vs.
disallowed location vs. malformed pattern) plus the registry-installed,
cross-version `algorithm_version` boundary check, reusing this same minimal
document and oracle.

Suggested handoff owner: upstream spec/release maintainers, through the linked
contract suites. Graduation requires the exact case documents and oracle to run
in an upstream-maintained verification command or CI, plus a linked owning
change and documentation of the `algorithm_version` parameter/exception contract
(the documentation gap noted above). **Not graduated:** no such transfer is
evidenced or published by this work. Until adoption, retain this bounded local
runner; after confirmed transfer, retire duplicate maintenance while preserving
the observations.

## Reproduce

Read the seven cases, obligation table and locks above first. From this repo's
root, use new directory names on every run (the runner refuses existing paths):

```bash
rtk proxy python3 probes/published-consumer/run.py --envs .probe-runs/K1/reproduce-envs --out .probe-runs/K1/reproduce-records
rtk proxy python3 -O probes/published-consumer/compare.py observations/K1/run --report .probe-runs/K1/comparison.json
rtk proxy python3 -O -m unittest discover -s probes/published-consumer -v
rtk proxy python3 -O probes/published-consumer/compare.py observations/K1/run --expected observations/K1/controls/corrupted-expected.json --report .probe-runs/K1/negative.json
```

The last command must exit 1; the others must exit 0. `run.py` always installs
against `probes/published-spec/locks/` with `pip --require-hashes` / `npm ci`;
there is no `--resolve` mode here to re-pin, by design, since K1 deliberately
reuses V1's pins rather than maintaining a second copy.
