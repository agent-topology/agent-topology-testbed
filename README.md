# agent-topology-testbed

Evidence for decisions about the [`agent-topology`](https://github.com/agent-topology/agent-topology)
format, gathered by consuming it.

Every claim here is produced by something that runs. The repository exists so that
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

Probes have **no dependency on the `agent-topology` packages** and are not
producers. They pin their own framework version and keep their own requirements, so
that a heavy dependency in one probe stays in that probe.

```
probes/airflow/    apache-airflow 2.10.5
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

```
cd probes/airflow && pip install -r requirements.txt && python airflow_probe.py
```

Probes are run by hand. They are not in CI, because pinning several orchestration
frameworks in one job buys less than it costs.

## Versions

Findings are recorded against a specific release and rot without one. Everything
currently here was observed against:

| Package | Version |
| --- | --- |
| `agent-topology-spec` | 0.1.0b2 |
| `@agent-topology/spec` | 0.1.0-beta.2 |
| `apache-airflow` | 2.10.5 |
