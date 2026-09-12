# Q1 — Documented quickstarts against registry packages

**Disposition: bounded non-finding, 2026-09-12.** Both selected quickstarts'
complete executable sequences passed in **two fresh environments per language**:
Python CLI, optional direct API, strict CLI, JavaScript ESM and CommonJS dynamic
import. Ten documents passed semantic and installed-package checks. No
documentation correction or package-defect reproducer is warranted by these runs.

This is [testbed #42](https://github.com/agent-topology/agent-topology-testbed/issues/42)
under [#37](https://github.com/agent-topology/agent-topology-testbed/issues/37).
The [findings index](../../findings/README.md#dispositions-and-unresolved-evidence)
links this disposition. Historical beta.2 records remain unchanged.

## Question and fixed inputs

Do the getting-started instructions work against the published packages they tell
readers to install? The minimal input is the documentation's own **one-node greet
graph** plus framework START/END sentinels. No larger graph, model, API key, graph
invocation or service is needed. Evidence class is **static extraction of a compiled
definition**, with **callable** validation/canonical/hash checks and shell/CLI
execution receipts. It does not measure framework-managed graph execution.

Documentation is fixed at upstream commit
[eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe](https://github.com/agent-topology/agent-topology/tree/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe).
[Source references](source-references.json) record immutable URLs and SHA-256 for
both full pages and the inspected upstream coverage files. The original
[Python](source/docs/getting-started/python.md) and
[TypeScript/JavaScript](source/docs/getting-started/typescript.md) pages are retained.

[inputs.json](inputs.json) was written before setup and copied into both run
directories before installation. It records each fenced block's original line,
language, classification, extracted bytes and SHA-256. [blocks/](blocks/) preserves
all ten blocks. Extraction retains the content's trailing newline; fences are
retained in the full source snapshots. No API call or example body was changed.

| Page / block | Pre-execution classification and coverage |
| --- | --- |
| Python 1 | Execute complete venv creation, activation and pip installation. |
| Python 2 | Save unchanged as graph.py. |
| Python 3 | Execute export and JSON inspection; save output before overwrite. |
| Python inline alternative | Execute the documented python graph.py redirection. |
| Python 4 | Execute strict export as the last complete Python example. |
| TypeScript 1 | Execute npm init and the exact npm install requests. |
| TypeScript 2–3 | Save graph.mjs unchanged and execute its redirection command. |
| TypeScript 4–5 | Save graph.cjs unchanged and execute its redirection command. |
| TypeScript 6 | Illustrative type/interface definition: retain as node-count.ts, not executed or claimed type-checked. It defines nodeCount without an invocation, compiler installation/version or concrete configuration. |

The inline Python strict API/error-handling discussion is illustrative guidance
for other graphs, not a complete additional program. Windows activation is an
explicit platform alternative outside this macOS run. ESM/CommonJS explanatory
inline fragments are not separate programs. No compiler setup was silently added.

Before execution, the literal output oracle required graph ID main; exactly
__start__, greet and __end__; two direct edges START → greet → END; no joins;
complete status/empty gaps; and the separate dynamic-interrupts limitation.
Entry/exit IDs are independently asserted as well. Separate audits check spec
validation, full canonical serialization and recomputed structureHash through the
installed public APIs.

## Isolation, adaptations and versions

Each run uses separate new Python/npm project directories outside the checkout,
an empty HOME and npm cache, and a small runtime-only PATH. A bootstrap symlink
names the selected Python interpreter python, as the page assumes; it contains no
package source. Later captured shells reactivate the same venv because activation
cannot persist between subprocesses. Bash -e/-x adds fail-fast behavior and tracing.
All executable documentation blocks otherwise remain verbatim.

The environment is allowlisted: no PYTHONPATH, PYTHONHOME, NODE_PATH, NODE_OPTIONS,
inherited virtualenv, package-manager configuration or application credentials.
Python user site and pip configuration are disabled; its index is public PyPI.
PIP_REPORT records acquisition without changing package requests. Only wheels are
accepted. npm uses empty user/global configurations and the public registry;
lifecycle scripts, audit, funding and update requests are disabled. These are
explicit acquisition/isolation guards, not additional API setup. No graph code is
wrapped or instrumented. Separate audit scripts validate saved outputs after the
documented commands and cannot make those commands succeed.

| Component | Observed version, both runs |
| --- | --- |
| Runtime | Python 3.14.7; Node 22.16.0; npm 11.4.1; macOS 26.5.2 ARM64 |
| Python producer / spec | 0.1.0b2 / 0.1.0b2 |
| Python LangGraph | 1.2.11, resolved within the producer's dependency range |
| npm producer / spec | 0.1.0-beta.2 / 0.1.0-beta.2 |
| LangGraph.js | 1.4.14 |
| Module mode | Native .mjs ESM and .cjs CommonJS with asynchronous import; no TS build |

Both installations use the exact documented top-level versions. Transitives
resolve independently on each run, without local artifacts or reused environments.
Each run preserves fully pinned, hashed requirements.lock, package.json, npm
package-lock.json, pip installation report and installed-dependency output.
The locks and all **75 artifact identities per run** match. Downloaded wheel
SHA-256 and npm SRI are checked against actual registry bytes; URLs and SHA-256
are retained in artifacts.json. Artifact digest is distinct from structureHash.

Python audits check the real imported spec, producer and LangGraph paths inside
the venv, all distribution roots and absence of direct_url.json (including
editable installs). npm audits check real public import paths inside the new
node_modules; every lock entry must be a public registry artifact with no link,
and its resolved directory must remain inside node_modules. There is no workspace
resolution. Locks describe the recorded platform, not cross-platform availability.

## Results and raw receipts

- [Run 1 commands](run-1/commands.json), [provenance](run-1/provenance.json),
  [artifacts](run-1/artifacts.json), [Python audit](run-1/python-audit.json)
  and [JavaScript audit](run-1/typescript-audit.json).
- [Run 2 commands](run-2/commands.json), [provenance](run-2/provenance.json),
  [artifacts](run-2/artifacts.json), [Python audit](run-2/python-audit.json)
  and [JavaScript audit](run-2/typescript-audit.json).
- Both directories retain unmodified topology outputs, executed graph files,
  classified final TypeScript block, effective environment and resolved locks.
  Commands record cwd, arguments, timestamp, duration, exit, stdout and stderr.
- [Comparison](comparison.json): ten documents, all five entry points. Full
  documents compare equal within each language and across its two runs after
  removing **only provenance.generatedAt**. No arrays are reordered, IDs scrubbed
  or duplicates removed. Cross-language document equality is not asserted.
- Each run has 15 captured subprocesses, all exit 0. Subprocess time is **16.00 s**
  and **16.14 s**, excluding artifact redownload/verification and orchestration.
- [Verification](verification.json): saved-evidence audit under optimized Python
  and eight control tests covering duplicate edges, missing nodes, missing/failed
  commands, changed import receipts, corrupted hashes and excessive normalization.

[An initial harness failure](harness-failure/commands.json) is retained separately.
The harness omitted Bash's -c, so Bash treated the installation block as a filename
and exited 1 before installation. Only the shell invocation was corrected, followed
by fresh directories. This is neither a documentation failure nor a completed run.
No snippet correction was proposed/applied; no failed setup counts as a non-finding.

## Existing coverage and incremental boundary

All source links below use the same frozen upstream commit.

- [Public documentation guards](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/tests/test_public_docs.py)
  already check links, published installation selections, compatibility metadata
  and migration-guide discovery. They do not execute the entire ordered sequence.
- [Python installed producer smoke](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/scripts/smoke_langgraph_installation.py)
  already checks a minimal graph, public API, agt and canonical output.
  [Python package CI](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/.github/workflows/python-packages.yml)
  uses built wheels/sdists with local spec artifacts. Q1 adds the unchanged
  getting-started graph, exact registry requests, JSON inspection, optional direct
  invocation and final strict command.
- [TypeScript installed smoke](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/scripts/smoke_typescript_installation.mjs)
  **already extracts and executes both getting-started JavaScript blocks outside
  the checkout**, checking completeness/nodes, validation and recomputed hashes.
  [TypeScript package CI](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/.github/workflows/typescript-packages.yml)
  supplies locally packed tarballs on Node 20/22. Q1 adds the documentation's
  npm init/install registry boundary and ordered commands, two fresh resolutions,
  artifact identities and snippet hashes.
- [Spec packed-install smoke](https://github.com/agent-topology/agent-topology/blob/eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe/packages/typescript/spec/scripts/smoke-install.mjs)
  already compiles a separately authored consumer with TypeScript and Node types.
  Q1 does not replace that compiler coverage or add its toolchain to this page.
  Fixture parity and producer-consumer coverage under upstream #103 remain
  complementary, as described by parent #37 and local D1.

This supports the selected doc-to-registry path at the recorded versions, not
every page, runtime, dependency resolution or future release. Graph invocation
is absent from the documented source; this does not establish a general
no-side-effects guarantee for arbitrary graphs.

## Disposition, decision impact and handoff

No new format finding ID is appropriate. This increment leaves F1–F8, historical
release receipts and upstream contracts unchanged. No decisive evidence is missing
for the classified executable sequences. Windows, browsers, concrete TypeScript
compilation and other runtimes remain untested scope.

The minimal handoff candidate is a registry mode for the existing installed-package
smokes: freeze these two pages, extract/classify blocks, execute their published
install commands and check the five entry points. Input is the same one-node graph;
the oracle is literal structure/completeness plus public validation, canonical
output and hash recomputation. Measured command cost is about 16 seconds per fresh
pair here, not a CI duration guarantee.

Suggested owners are maintainers of the linked upstream clean-installations jobs
and smoke scripts. **Not graduated:** this evidence supplies no accepted ownership
link or upstream maintained check incorporating this registry sequence. Transfer
requires a concrete upstream check/commit, its maintained CI/verification-command
link and ownership/documentation link; opening an issue alone is insufficient.
No upstream publication was performed. Upon confirmed transfer, retire the duplicate
runner while preserving these historical inputs and receipts.

## Reproduction

From the repository root, with Python 3.14 and Node 22/npm available:

    rtk proxy python3 probes/registry-quickstarts/run.py --envs /tmp/q1-new-a --out /tmp/q1-evidence-a
    rtk proxy python3 probes/registry-quickstarts/run.py --envs /tmp/q1-new-b --out /tmp/q1-evidence-b
    rtk proxy python3 -O probes/registry-quickstarts/verify.py /tmp/q1-evidence-a /tmp/q1-evidence-b
    rtk proxy python3 -O -m unittest discover -s probes/registry-quickstarts -p test_verify.py -v

Use new paths; the runner rejects reused environment/output directories. The first
two commands intentionally repeat the documented resolution and retain new locks.
For exact artifact replay, install run-1/requirements.lock with pip --require-hashes
in a fresh venv, and run-1/package.json plus package-lock.json with npm ci in a fresh
npm project, against the recorded registries; then execute the saved graph
files/commands. That is a **locked artifact replay**, not re-execution of the
original installation instructions. No whole-site or unrelated framework suite runs.
