# agent-topology-testbed

Evidence for decisions about the [`agent-topology`](https://github.com/agent-topology/agent-topology)
format, gathered by consuming it.

[Consumer reconciliation](findings/consumer-reconciliation.md) connects
Cordboard's catalog, drift and correlation decisions to existing F1–F8 evidence.
The [R3 experiment](observations/cordboard-r3/README.md) records a literal ADR
model over four minimal producer inputs: conditional single/list selection stays
indistinguishable to the rule. This is consumer-policy evidence, not a runtime
safety test or a new finding ID.

[The consumer contract audit](observations/consumer-contract-audit/README.md)
defines five structural question groups and source-backed judgments for 31
documents under core-only and experimental opt-in profiles. Its 310 reviewed
groups preserve underdetermined answers without expected values; this is document
evidence reusable by the consumer work above, not a consumer execution or release gate.

[Q1](observations/Q1/README.md) records two fresh registry installations of each
documented quickstart: all five executable entry points pass, with unchanged
snippets, artifact identities and a bounded non-finding disposition.

[D1](observations/D1/README.md) records published beta.2 producer determinism across
small Python/TypeScript LangGraph transformations, fresh-process repetitions and
structural positive controls, with a bounded non-finding disposition.

Claims here must be tied to their evidence class and reproduction. The repository
exists so that
a question about the format — *can a consumer draw this correctly? can a second
framework emit this field?* — can be answered with a reproduction rather than an
argument.

## What this is not

**Not part of the 0.1 contract.** Nothing here is published, and nothing here
gates a release of the main repository. If a check in this repository breaks, that
is a signal to look, not a reason to hold a release. The moment this becomes a
release gate, its findings acquire leverage over the format, which is the opposite
of what it is for.

**Not a viewer.** The renderer in `instrument/` is a measuring device. It exists
because rendering forces a consumer to make every decision the format leaves open,
and the drawing makes the resulting ambiguity visible. If a publishable viewer is
ever wanted, it should be extracted as a separate repository with a stricter
contract — core fields only, no extensions, no framework dependencies. This
repository deliberately breaks all three of those rules.

## Layout

```
findings/     the unit of work; see findings/README.md
instrument/   the renderer used to produce visual evidence
probes/       per-framework structure extraction, one directory each
gallery/      the conformance corpus rendered and committed
```

### `findings/`

The working unit. A finding is a claim about the format with a reproduction
attached. Findings carry a status, and a finding is not filed upstream until it has
one. See [`findings/README.md`](findings/README.md) for the index and the rules.

A finding gets its own directory when it has evidence to hold. Short ones stay
inline in the index — structure should track weight rather than be applied for
symmetry.

### `instrument/`

A pure function from a topology document to an SVG string, plus a build that
renders the conformance corpus. Deterministic by construction so that committed
output diffs cleanly and a change in a drawing means a change in the input.

Unlike a viewer, it may read `x-*` behind an explicit flag. That is how a proposed
core field is trialled before anyone is asked to emit it.

### `probes/`

One directory per framework, each answering a single question: *can this framework
see the thing the format wants to describe?*

Framework-native probes have **no dependency on the `agent-topology` packages** and are not
producers. They pin their own framework version and keep their own requirements, so
that a heavy dependency in one probe stays in that probe.

The same directory also holds isolated published-package experiments such as
`published-producer/` and `cordboard-r3/`; those intentionally install topology
packages and retain a separate evidence class from framework-native probes.

```
probes/airflow/    apache-airflow 2.10.5
probes/dagster/    dagster 1.13.22
probes/crewai/     crewai 1.15.21
```

### `gallery/`

The conformance corpus rendered from `conformance/fixtures/*/expected.json` in the
main repository, committed. The diff is the point: when a fixture or a package
version changes, the change in the drawing is the report.

## Running

```
cd instrument && npm install
FIXTURES=../../agent-topology/conformance/fixtures OUT=../gallery npm run build
npm run experiment
```

For the isolated two-node baselines, follow [probe reproduction](probes/README.md).
New observations live in [P0](observations/P0/README.md),
[P1](observations/P1/README.md), [P2](observations/P2/README.md),
[P3](observations/P3/README.md), [P4](observations/P4/README.md),
[P5](observations/P5/README.md), [P6](observations/P6/README.md), and the
matrix-backfill/boundary observations such as [C1](observations/C1/README.md)
and [S1](observations/S1/README.md), plus the Temporal boundary inspection
[T1](observations/T1/README.md) and Prefect definition/runtime comparison
[P8](observations/P8/README.md), and the AutoGen programming-model comparison
[A1](observations/A1/README.md), with the
[final P7 comparison and epic review](findings/cross-framework-reconciliation.md), following the
[evidence conventions](docs/evidence.md). The original `airflow_probe.py` and
`OUTPUT.txt` remain historical beta.2 evidence, not these smoke/branch cases;
`airflow_probe.py`'s unsupported exclusive/concurrent conclusion was itself
corrected by P1, linked from [F1](findings/F1-fan-out-semantics/README.md#correction-p1).

Probes are run by hand. They are not in CI, because pinning several orchestration
frameworks in one job buys less than it costs.

## Versions

[E1](observations/E1/README.md) adds 300 generated beta.2 input comparisons,
structural permutations, minimized counterexamples and a fixed-seed repeat.
It found full canonical-byte differences for extension numbers ([F8](findings/F8-extension-number-canonicalization/README.md)),
with equal structure-hash tuples throughout the bounded population.

[V1](observations/V1/README.md) records the retrospective, isolated comparison of
published beta.1/beta.2 Python and npm spec hashes on nine fixed documents,
including artifact identities, raw results and a bounded non-finding disposition.

[V2](observations/V2/README.md) reuses those nine immutable documents across
isolated published beta.2/beta.3 Python and npm spec installations. All 27
requested transition/cross-language comparisons retain acceptance, full canonical
bytes and structure-hash tuples; because the corpus has no numeric extension, this
is a bounded non-finding. [E2](observations/E2/README.md) separately replays E1's
saved numeric population and all 16 minima, resolving F8 within that bounded corpus
on published beta.3 while preserving the beta.2 finding.

[K1](observations/K1/README.md) reuses V1's isolated installations and minimal
document to test six controlled single-field mutations (an unsupported
`topologyVersion`, an unsupported declared hash-algorithm version, permitted and
disallowed `x-*` extension placements, and a malformed extension key) plus one
direct out-of-range `algorithm_version` call, against a source-linked obligation
table; all four installations matched every recorded expectation across two
independent runs, a bounded non-finding disposition.

Findings are recorded against a specific release and rot without one. The
historical baseline at commit
`571e881e6d509b6e26ff8bf14b98e207d12e7ce9` was recorded against:

| Package | Version |
| --- | --- |
| `agent-topology-spec` | 0.1.0b2 |
| `@agent-topology/spec` | 0.1.0-beta.2 |
| `apache-airflow` | 2.10.5 |

The beta.3 registry set (`agent-topology-spec`/`agent-topology-langgraph`
`0.1.0b3`; `@agent-topology/spec`/`@agent-topology/langgraph`
`0.1.0-beta.3`) is separately recorded in the [2026-09-12 status snapshot](findings/evidence/upstream-status-2026-09-12-beta.3.json).
It is registry-published, not a testbed-verified release or a replacement for
the historical baseline.

[X1](observations/X1/README.md) observes the F1–F6 consumer affordances in those
four registry artifacts with pinned LangGraph 1.2.11/LangGraph.js 1.4.14 inputs,
fresh-process pairs and a negative control. Its per-affordance results do not
resolve whole findings or qualify beta.3.

New P0 observations record Python 3.11.16, framework versions, and lock/source
hashes independently; they do not revalidate F1/F3 or the gallery.
