# V2 — Published beta.2/beta.3 structure hashes and canonical bytes

**Disposition: bounded non-finding.** On 2026-09-12, the nine unchanged V1
documents validated in isolated published Python beta.2/beta.3 and npm
beta.2/beta.3 spec installations. All 27 requested comparisons retained the
complete `sha256` / algorithmVersion `1` / value tuple and identical full
canonical UTF-8 bytes. No algorithm transition occurred.

This is **callable** evidence for testbed
[#53](https://github.com/agent-topology/agent-topology-testbed/issues/53), under
[#51](https://github.com/agent-topology/agent-topology-testbed/issues/51). It is
not framework execution, a release qualification, an upstream contract change,
or a claim beyond these documents.

## Question, minimal input and pre-run expectations

Does an identical valid document retain its structure-hash tuple from published
beta.2 to beta.3 within each language, and do the two languages agree at beta.3?
The minimal input is V1's existing nine-document corpus, fixed by the same SHA-256
values in [V1's manifest](../V1/inputs.json); no producer, framework or generated
population is needed.

Before beta.3 was installed or executed, each document was recursively inspected
for numbers nested under an `x-*` key and its expected result was written to
[expectations.json](expectations.json). None contains such a number, so every row
expected both equal full canonical bytes and an equal structure-hash tuple:

| Input | Numeric value under `x-*` | Expected canonical bytes | Expected hash tuple |
| --- | --- | --- | --- |
| conditional-routing | none | equal | equal |
| interrupt-before | none | equal | equal |
| linear-flow | none | equal | equal |
| loop | none | equal | equal |
| minimal | none | equal | equal |
| multi-source-join | none | equal | equal |
| nested-subgraph | none | equal | equal |
| parallel-fanout | none | equal | equal |
| unknown-routing-targets | none | equal | equal |

The conditional expectation comes from accepted
[ADR 0009](https://github.com/agent-topology/agent-topology/blob/848b179aee32789a6f8b0ad4552a3a1262a05d55/docs/decisions/0009-numeric-canonical-form.md):
numeric extensions may change full-document canonical bytes across the package
transition, while extensions remain outside hash algorithm version 1. The ADR
also states that existing fixtures contain no numeric extension. Exact inspected
source identities are retained in [source-references.json](source-references.json).

## Installations and evidence

The initial capture resolved only the two new beta.3 locks. Beta.2 used V1's
existing locks unchanged. The independent reproduction then used all four locks
with pip `--require-hashes` and `npm ci`. The imported package calls record
Python **3.14.7** and Node **22.16.0** on macOS ARM64.

| Installation | Published spec artifact SHA-256 |
| --- | --- |
| Python `0.1.0b2` | `14aa6083e5d32dbec527ccb9422e91d99f4415c3d3b0a30d5677f108401a8873` |
| Python `0.1.0b3` | `45732c5080126484af8ba4bea7a1767f72fca27721825c0f678321fa7093e276` |
| npm `0.1.0-beta.2` | `373fbb08548ebcf8d62abb952b5f1e711be3d2616579cbe86e8c30f89e8aa9bc` |
| npm `0.1.0-beta.3` | `4c5fab1be1a6fa3498a500a57bd438a7a70c53c7d7e5b5730d0665b0e1d06560` |

- [Initial artifacts](run/artifacts.json) and
  [reproduction artifacts](locked-reproduction/artifacts.json) retain registry
  URLs, every transitive artifact version, verified SHA-256, and npm SRI.
- New [Python beta.3](../../probes/published-spec/locks/py-b3/requirements.lock)
  and [npm beta.3](../../probes/published-spec/locks/js-b3/package-lock.json)
  locks sit beside the unchanged beta.2 locks.
- [Identity records](run/identities.json) retain exact runtimes, executables and
  imported paths inside each isolated installation. [Command records](run/commands.json)
  retain cwd, UTC start, duration, exit, stdout and stderr.
- Each input ran twice in a fresh process in each installation: **72/72** adapter
  exits were zero in both the initial capture and lock-only reproduction.
  Complete repeated adapter records match within each installation.
- The [initial comparison](run/comparison.json) and
  [lock-only comparison](locked-reproduction/comparison.json) are byte-identical:
  27 accepted pairings, with zero rejections, canonical differences, hash
  disagreements, algorithm transitions or expectation mismatches.

Adapters use only public validation, canonicalization and structure-hash APIs.
Setup/import/API failures are nonzero and cannot be classified as evidence.

## Comparison classes and control

For each document the comparator evaluates Python b2→b3, npm b2→b3, and
Python↔npm at beta.3. Validation acceptance, full canonical bytes and complete
hash tuples are separate fields. A changed algorithm name/version is recorded as
an `algorithm-transition`, never as same-algorithm structural drift.

The [corrupted expectation](controls/corrupted-expectations.json) changes exactly
one saved outcome: `minimal.json` canonical bytes from `equal` to `different`.
The comparator exited **1**, recording three expectation mismatches and no
package disagreement; the [report](controls/corrupted-comparison.json) and
[command receipt](controls/commands.json) retain the result. Fifteen deterministic
V1/V2 controls also cover transitions, same-algorithm hash disagreement,
canonical-only difference, rejection exclusion, missing repetition, adapter
error and package identity.

## Closure disposition

- **Measured claims:** published Python `0.1.0b2`→`0.1.0b3`, npm
  `0.1.0-beta.2`→`0.1.0-beta.3`, and Python↔npm beta.3 acceptance, full
  canonical bytes and complete structure hashes for nine fixed documents, twice
  in fresh processes.
- **Finding disposition:** explicit bounded non-finding. No transition or
  disagreement occurred, so no new finding is allocated. This reinforces V1 for
  the same numeric-extension-free corpus without rewriting its beta.2 evidence.
- **Evidence and index:** saved records and reproduction are linked above; the
  [findings index](../../findings/README.md#dispositions-and-unresolved-evidence)
  links back here.
- **Decision impact:** consumers can treat these exact documents as unchanged
  across the measured package transition. This does not qualify beta.3, change
  hash policy or imply upstream approval.
- **Unresolved evidence:** V2 contains no numeric extension and therefore does
  not itself settle F8 on beta.3. The planned E2 follow-up
  [#54](https://github.com/agent-topology/agent-topology-testbed/issues/54) has now
  [replayed E1's numeric population](../E2/README.md) through these installations
  and resolved F8 within that bounded corpus. No broader input or framework run
  is needed for V2's bounded question.

## Reproduce

Read [expectations.json](expectations.json), V1's input manifest and the locks
before running. Use new directories; the runner refuses stale paths.

```bash
rtk proxy python3 probes/published-spec/run_v2.py --envs .probe-runs/V2/reproduce-envs --out .probe-runs/V2/reproduce-records
rtk proxy python3 -O probes/published-spec/compare_v2.py observations/V2/run --report .probe-runs/V2/comparison.json
rtk proxy python3 -O -m unittest discover -s probes/published-spec -p 'test_compare*.py' -v
rtk proxy python3 -O probes/published-spec/compare_v2.py observations/V2/run --expected observations/V2/controls/corrupted-expectations.json --report .probe-runs/V2/negative.json
```

The final command must exit 1; the others must exit 0. `--resolve-b3` is only for
establishing the committed beta.3 locks and is not part of ordinary reproduction.
