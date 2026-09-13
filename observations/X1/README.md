# X1 — Registry beta.3 F1–F6 consumer affordances

**Disposition: the requested affordances are registry-observed, with bounded residual unknowns unchanged.**
Published Python `agent-topology-langgraph==0.1.0b3` / `agent-topology-spec==0.1.0b3`
and npm `@agent-topology/langgraph@0.1.0-beta.3` /
`@agent-topology/spec@0.1.0-beta.3` expose the F1–F5 experimental facts and F4
helper expected from source `848b179`. Synchronous CommonJS `require()` still
fails, while the pinned beta.3 guide documents ESM and asynchronous `import()`.
This is a per-affordance registry-artifact result, not a whole-finding resolution,
release qualification, upstream contract change, or vendor-neutrality claim.

This is static producer-extraction and direct public spec-callable evidence for
[testbed #55](https://github.com/agent-topology/agent-topology-testbed/issues/55),
under [#51](https://github.com/agent-topology/agent-topology-testbed/issues/51).
No node body, router, or framework graph was executed.

## Question, minimum inputs, and pre-extraction expectations

Do the registry-published beta.3 artifacts expose what the findings index and
status review previously attributed only to source and upstream-recorded
verification? The [literal expectation manifest](../../probes/registry-affordances/expectations.json)
was written from the contract, interpretation ADR, consumer guide, producer
surfaces and CommonJS guidance at `848b179` before extraction. Exact source blob
IDs are in [source-references.json](source-references.json).

The inputs are one minimum definition or document per affordance: direct fan-out,
conditional routing, an unknown router plus orphan target, a compiled child and
same-shaped ordinary node, a multi-source join and independent-edge control, and
a START→END sentinel graph. The orphan router uses `custom-router`; Python also
describes it twice through `agt describe --graph-id custom-router`. The spec-only
CommonJS input is one `require("@agent-topology/spec")` statement.

Upstream [#103](https://github.com/agent-topology/agent-topology/issues/103) already
records workspace-source producer/consumer fixture coverage. X1 does not copy its
fixture outputs. It adds isolated public-registry artifact identities, fresh-process
records, independently authored expectations, and a wrong-expectation control.

## Registry-observed results

### F1 — branch interpretation

Both languages emit `known/all-declared` with `unconditional-edges` evidence for
the direct router and `unknown/selection-not-observable` for the conditional
router. This confirms declaration interpretation only; selection and execution
remain unknown.

### F2 — entries and orphan causality

For the custom-ID orphan case, core `entryNodeIds` is `['__start__', 'target']`.
START is `observedRoot: true` and `known/confirmed`; target is
`observedRoot: true` and `unknown/entry-not-established`. The sole
`unknown-routing-targets` gap remains on router and carries graph ID
`custom-router`. No target gap or causal link is inferred, so orphan causality
remains unknown.

### F3 — opaque child

The compiled child and ordinary callable have equal core structures and equal
structure-hash tuples. The child is `known/opaque-child` with `compiled-child`
evidence; the ordinary callable remains `unknown/identity-unavailable`. Their
different extensions demonstrate directly that equal hashes do not establish
extension equality. Ordinary-callable child scope remains unknown.

### F4 — join helper

Python `derived_join_edges` and TypeScript `derivedJoinEdges` return two sorted
`{joinId, source, target}` records for the multi-source join, retaining
`join:a+b:joined` provenance. The independent-edge control returns an empty list.
Core joins and ordinary edges were asserted separately; the helper does not turn
join connections into ordinary edges.

### F5 — sentinel roles

The two-node START→END graph emits `known/start` and `known/end` with
`framework-sentinel` evidence in both languages. These are experimental
LangGraph facts from two implementations; vendor neutrality remains unproven.

### F6 — CommonJS boundary

Both fresh Node processes exit `1` with `ERR_PACKAGE_PATH_NOT_EXPORTED` for
synchronous `require("@agent-topology/spec")`. The pinned guide explicitly says
the packages are ESM-only, synchronous `require()` is unsupported, and CommonJS
applications should await `import()`. Guidance is registry-relevant source at the
tag; no CommonJS bundle or changed runtime error is observed.

## Core, extensions, hashes, and repeat comparison

The verifier asserts literal node IDs, edge endpoints and kinds, joins,
entry/exit arrays, gaps, graph references, and helper results independently for
every capture. It separately recomputes and checks each complete
`sha256`/algorithmVersion `1` structure-hash tuple. Extension facts are compared
only after removing language-specific evidence-source locator strings; core
validation is not treated as extension validation.

[comparison.json](run/comparison.json) records **32/32** successful producer
captures: eight cases × two languages × two fresh processes. All 16 within-language
fresh-process semantic comparisons and all eight cross-language semantic
comparisons match; the F3 control retains equal core/hash and unequal extension.
Two CLI graph-ID comparisons match the Python API records. Normalization removes
provenance timestamps, process IDs, executables, import paths, and only the
language-specific evidence `source` strings. It does not remove or deduplicate
nodes, edges, joins, arrays, gaps, fact states/values/reasons/evidence kinds,
hashes, or helper records.

## Environments, artifacts, and receipts

The builders were inspected before installation. [Setup receipts](setup/commands.json),
[artifact identities](setup/artifacts.json), [pip report](setup/pip-report.json),
and [lock provenance](setup/provenance.json) retain the registry URLs, transitive
versions and verified digests. Worker identities retain runtimes and exact import
paths inside the isolated environments; the verifier rejects paths outside the
Python prefix or npm installation.

| Artifact | Version | SHA-256 |
| --- | --- | --- |
| Python producer | `0.1.0b3` | `c81658d8db2293c1a87255e7437d789592d40131bc5a6db2fc5b7412795312c6` |
| Python spec | `0.1.0b3` | `45732c5080126484af8ba4bea7a1767f72fca27721825c0f678321fa7093e276` |
| npm producer | `0.1.0-beta.3` | `acd426402fa3a02f868f87ecc50a1b03468dac745a4ad504d3da30cf9d857452` |
| npm spec | `0.1.0-beta.3` | `4c5fab1be1a6fa3498a500a57bd438a7a70c53c7d7e5b5730d0665b0e1d06560` |

Python is **3.11.16**, LangGraph is **1.2.11**, Node is **22.16.0**, and
LangGraph.js is **1.4.14**. The committed pip hash lock and npm lock install only
registry artifacts; direct/editable Python inputs and linked/non-registry npm
packages fail setup.

The retained [harness failure](harness-failure/commands.json) stopped after the
first TypeScript worker could not resolve packages from the evidence directory.
It predates the successful capture, is excluded from every comparison, and is not
evidence for an affordance. The runner now executes the exact retained worker copy
from the isolated npm installation.

## Verification and negative control

The saved wrong expectation changes only F1's expected direct branch value to
`deliberately-wrong`. The optimized verifier exits **1** and reports
`fact router/branch`; [the command receipt](controls/command.json) and
[comparison](controls/comparison.json) retain the nonzero result. Unit controls
also reject a missing capture and a workspace import path.

## Closure disposition

- **Measured claims:** the F1–F5 producer facts, F4 public helpers, F6 module
  boundary, and custom graph ID/gap references described above, from the pinned
  beta.3 registry artifacts, twice in fresh processes per language.
- **Finding disposition:** each F1–F6 row now has a distinct registry-observed
  status. No finding is marked wholly resolved; F1 selection, F2 causality, F3
  ordinary-callable scope, and F5 vendor neutrality remain unchanged.
- **Evidence and index:** expectations, locks, raw records, receipts, comparison,
  control and reproduction are retained here; the [findings index](../../findings/README.md)
  links each affordance back to its section above.
- **Decision impact:** consumers of these exact beta.3 artifacts can use the
  emitted experimental facts and join helpers with the stated limits, supply
  document-local graph IDs, and follow async ESM recovery guidance. This does
  not qualify beta.3 or imply upstream approval.
- **Unresolved evidence:** stronger branch selection, orphan causality,
  ordinary-callable child identity, and vendor neutrality require the same
  independent evidence already named by the findings. No larger X1 input would
  answer them. Other runtimes, frameworks, package versions and positive-depth
  traversal remain untested.

## Reproduce

Read the expectations, builders and locks before installation. Use two new paths;
the setup and runner reject stale or in-repository environments.

```bash
rtk proxy python3.11 probes/registry-affordances/setup.py --envs /tmp/x1-envs --out /tmp/x1-setup
rtk proxy python3.11 probes/registry-affordances/run.py --envs /tmp/x1-envs --out /tmp/x1-run
rtk proxy python3.11 -O probes/registry-affordances/verify.py /tmp/x1-run --report /tmp/x1-comparison.json
rtk proxy python3.11 probes/registry-affordances/control.py /tmp/x1-run --out /tmp/x1-control
rtk proxy python3.11 -O -m unittest discover -s probes/registry-affordances -p 'test_*.py' -v
```

The first three commands and unit suite exit zero. The control wrapper exits zero
only after its nested verifier exits one for the deliberately wrong expectation.
