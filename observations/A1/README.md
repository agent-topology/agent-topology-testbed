# A1: AutoGen programming-model topology boundaries

For [#17](https://github.com/agent-topology/agent-topology-testbed/issues/17),
[epic #1](https://github.com/agent-topology/agent-topology-testbed/issues/1), and
[M1](../../probes/README.md#common-question-matrix-m1).

**Result:** AutoGen AgentChat **0.7.5 GraphFlow is a positive control** for
public static extraction of this declared two-agent execution graph.
SelectorGroupChat exposes participant configuration, but that membership is
not a declared execution dependency graph. Its deterministic selector produces
different speaker orders from different supplied message state. The boundary
therefore depends on the programming model and inspected API, not just AutoGen's
brand. This is a local observation, not a producer or a universal semantics claim.

## Question and minimal input

Question: does a public explicit graph invalidate a framework-wide negative
static-extraction conclusion based on runtime speaker selection?
If neither model exposed dependencies, the candidate would remain scoped to
runtime observation or separately validated source analysis. If GraphFlow exposed
them, it would become a static-producer candidate for a supported subset.
Prior boundary probes cover different SDKs and cannot settle this question.

[expected.json](../../probes/boundaries/autogen/expected.json) was written before
extraction. Exactly two `AssistantAgent`s, named `alpha` and `beta`, each use a
supported `ReplayChatCompletionClient` with one fixed reply. Each case creates
fresh instances of those same two agent definitions. No tools, credentials,
network model, external inputs, or service are used. SelectorGroupChat also has
an empty replay client: any model fallback fails instead of contacting a model.

The selector reads the supplied first message (`forward` or `reverse`), chooses
an initial speaker, then chooses the other agent. GraphFlow declares only
`alpha → beta`. Both teams have `max_turns=2`; each run also has a 15-second
async timeout. Applying both inputs to both models distinguishes input-dependent
selection from fixed declarations with no extra agents.

| Case | Expected agent-message order | Expected replies | Expected stop |
| --- | --- | --- | --- |
| selector-forward | alpha, beta | alpha-reply, beta-reply | maximum 2 turns |
| selector-reverse | beta, alpha | beta-reply, alpha-reply | maximum 2 turns |
| graph-forward | alpha, beta | alpha-reply, beta-reply | graph complete |
| graph-reverse | alpha, beta | alpha-reply, beta-reply | graph complete |

Each result must also contain exactly one initial user message and two agent
messages, all `TextMessage`. Replay call counts must be one per agent and zero
for selector-model fallback. Recorded callback choices must match independently
expected message order. Nothing is deduplicated to make a case pass.

## Evidence classes and public API boundary

**Static:** construct teams and call public `dump_component()`, inspect its
participant/configuration metadata, and inspect `DiGraph.nodes`, node edges,
`get_start_nodes()` and `get_leaf_nodes()`. No `run()` or selector invocation;
all replay call counts and the selector-call list must be empty. The static-only
command is a separate process. Constructing Python definitions is permitted;
"static" does not mean arbitrary imports are side-effect free.

Both configurations contain `alpha`, `beta`, their model configurations and the
turn limit. SelectorGroupChat's serialized configuration contains neither a graph
nor `selector_func`; its public API explicitly documents omission of the callable.
A list of possible speakers does not tell which dependencies were declared.
This does not rule out inspecting a restricted user-authored selector with a
separately validated source analyzer.

GraphFlow exposes two named nodes, one unconditional `alpha → beta` edge,
root `alpha`, leaf `beta`, node activation `all`, and edge activation group
`beta` / condition `all`. The team configuration preserves the graph.
`dump_component()` omits null fields; the direct graph dump retains them.
These are **execution dependencies**, not a message routing graph: the tagged
guide states message filtering is a separate feature. No message-filter behavior
was measured.

**Execution:** public `team.run()` schedules the replay-backed agents and returns
messages and a stop reason. All four cases pass the literal expectations above.
A single outgoing edge is not a fan-out/convergence experiment, and a fixed
local sequential run proves neither production scheduling nor parallelism.

**Callable:** none separately collected. Selector-call instrumentation was
collected inside framework-managed execution, not by directly evaluating it.

## Released version and documentary review

AgentChat/Core/Ext **0.7.5**, CPython **3.11.16**, macOS arm64, uv **0.12.10**.
[PyPI release metadata](https://pypi.org/project/autogen-agentchat/0.7.5/)
records the released wheel uploaded on 2025-09-30 and Python >=3.10.
This is a selected released baseline, not a claim about the latest release.
The separate [hash lock](../../probes/boundaries/autogen/requirements.lock)
contains all 12 installed distributions; Ext has no live-model extras installed.

[source-review.json](source-review.json) records release filenames/hashes,
requirements, ten tagged source/document hashes, and byte equality of all eight
reviewed implementation files with installed packages. The matching documentation
is the notebook source at **python-v0.7.5**, not the issue's moving `/dev/` page.

| Version-specific reference | Interpretation and limitation |
| --- | --- |
| [GraphFlow guide](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/docs/src/user-guide/agentchat-user-guide/graph-flow.ipynb) | Declares GraphFlow experimental. Documents execution graph versus message graph, explicit sequential/parallel/conditional/looping patterns. Only the two-node unconditional chain was executed here. |
| [GraphFlow, DiGraph, nodes and edges](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_graph/_digraph_group_chat.py) and [public exports](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-agentchat/src/autogen_agentchat/teams/__init__.py) | Public exported API; experimental status explicitly warns of future changes. Node activation and edge activation groups/conditions are visible. Callable edge predicates are omitted from serialization: this simple graph does not validate a lossless exporter for every GraphFlow. |
| [SelectorGroupChat API](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_selector_group_chat.py) | Public team API, without GraphFlow's experimental warning in this class documentation; this is not a guarantee of future API stability. Configuration is an inventory/control configuration, and the custom selector is explicitly not serialized. |
| [Replay client](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-ext/src/autogen_ext/models/replay/_replay_chat_completion_client.py) | Public replay responses and `create_calls` avoid live models. These inputs do not test tool calls, handoff generation, or model-driven speaker selection. |
| [HITL guide](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/docs/src/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.ipynb), [UserProxyAgent](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-agentchat/src/autogen_agentchat/agents/_user_proxy_agent.py), [termination conditions](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-agentchat/src/autogen_agentchat/conditions/_terminations.py) | Blocking user input during a run differs from terminating and accepting input on the next run. `HandoffTermination` reacts to a target handoff message; a handoff/stop is not by itself a durable resumable interrupt. No human interaction or handoff executed. |
| [BaseGroupChat](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py), [messages](https://github.com/microsoft/autogen/blob/python-v0.7.5/python/packages/autogen-agentchat/src/autogen_agentchat/messages.py) | Public state save/load and experimental pause/resume exist. Pause behavior depends on agent hooks. Message IDs are generated UUIDs; private team/topic IDs are not exported as graph identities by this probe. State continuation and pause/resume are documentary only. |

The HITL guide's max-turns list omits GraphFlow, while the same tag's GraphFlow
API accepts it. The installed API and executed cap are used here; the stale list
is not treated as proof of missing support. Termination in this fixture does
not measure persistence, resumable HITL, or placement of structural interrupts.

## Seven-question answers

| ID | SelectorGroupChat 0.7.5 | GraphFlow 0.7.5 |
| --- | --- | --- |
| Q1 | **partial, static:** participant/configuration metadata available; no execution edges in this inspected configuration, selector callable omitted. | **support, static:** declared graph available through public DiGraph and component configuration without agent execution. |
| Q2 | **partial, static:** explicit participant names are membership, not execution dependencies. | **support, static:** two explicit nodes, one edge, root/leaf identity. Execution graph does not imply message routing. |
| Q3 | **partial, execution:** same membership yields alpha/beta or beta/alpha according to message state; one speaker per observed turn. No declared fan-out or concurrency measured. | **partial, static + execution:** the unconditional edge is preserved and both inputs execute alpha/beta. Parallel/conditional fan-out documented, unexecuted. |
| Q4 | **untested:** no multi-source join fixture or AND/OR policy comparison. | **partial, static + documentary:** activation/group/condition defaults exposed; all/any supported by documented API. A chain cannot test multi-source convergence, duplicate triggers or normative upstream join equivalence. |
| Q5 | **untested:** no nested team/opaque boundary fixture. | **untested:** no nested graph/ports fixture; two nodes establish no nesting semantics. |
| Q6 | **partial, static + execution + documentary:** max-turn configuration and stopping observed. UserProxy, handoff termination, state continuation and pause/resume are distinct documented concepts; resumable HITL and structural interrupt placement untested. | **partial, static + execution + documentary:** graph completion and configured turn cap observed. Same documented base APIs do not establish resumable graph-node HITL; no human node/interrupt fixture. |
| Q7 | **partial, static + execution:** authored alpha/beta names repeat across two processes; message UUIDs differ. No public run ID was collected, no private ID treated as structural. | **partial, static + execution:** node names/edge endpoints repeat across two processes; separate generated message UUIDs differ. No universal stability guarantee across code/version changes. |

## Reproduction

Inspect the minimal input, literal expectations, requirements and lock before
setup. Use a new isolated environment; no other framework checks are required.
Commands below run from repository root. Every command must succeed before an
output counts as evidence; setup/API failure is blocked evidence, never a
negative capability result.

```sh
cat probes/boundaries/autogen/{probe.py,expected.json,requirements.txt,requirements.lock}
uv venv --python 3.11.16 .venvs/autogen
uv pip sync --python .venvs/autogen/bin/python --require-hashes probes/boundaries/autogen/requirements.lock
uv pip check --python .venvs/autogen/bin/python
.venvs/autogen/bin/python probes/boundaries/autogen/probe.py --static-only --output .probe-runs/a1-static.json
for n in 1 2; do
  .venvs/autogen/bin/python probes/boundaries/autogen/probe.py --output .probe-runs/a1-$n.json
done
.venvs/autogen/bin/python probes/boundaries/autogen/verify.py .probe-runs/a1-1.json .probe-runs/a1-2.json
.venvs/autogen/bin/python -O probes/boundaries/autogen/probe.py --output .probe-runs/a1-optimized.json
.venvs/autogen/bin/python -O probes/boundaries/autogen/verify.py .probe-runs/a1-1.json .probe-runs/a1-optimized.json
.venvs/autogen/bin/python -m unittest discover -s probes/boundaries/autogen -p 'test_*.py' -v
```

Committed [static record](static.json), [run 1](run-1.json), and
[run 2](run-2.json) retain full component configuration and native messages.
The records include probe/verifier/test/expectation and dependency-input hashes.
The verifier checks all meaningful order, content, types, counts, stop reasons,
static declarations, versions and local source hashes before comparison.
Only generated message `id` and wall-clock `created_at` values are excluded
from semantic equality; timestamps must parse as UTC and remain in raw records.
Message list order is retained;
12 UUID4 message IDs per process must be unique and disjoint between processes.
All remaining fields compare unchanged, including message metadata/token usage.
No run UUID is fabricated. These are TaskResult messages, not a full internal
runtime-event trace. Two processes do not prove future identity stability.

Final verification passed: dependency compatibility (12 distributions), static
inspection, two fresh-process executions, normal and optimized comparisons, two
integrity tests (including five deliberate corruptions under normal and optimized
Python), local documentation links, and committed source/lock hashes.

Lock generation (already performed; regeneration is a reviewed change):

```sh
uv pip compile --python 3.11.16 --generate-hashes --output-file probes/boundaries/autogen/requirements.lock probes/boundaries/autogen/requirements.txt
```

During implementation, comparing the component graph dump to a full graph dump
failed because the former omits nulls. The comparison now explicitly uses
`exclude_none=True` for that serialization surface and retains the full direct
graph separately. The first two-run comparison also exposed generated `created_at` timestamps;
they are now explicitly normalized alongside message UUIDs, without reordering
messages. No dependency or agent-order expectation was weakened.
The first attempted tagged source URL used `_graph_flow.py` (404); the actual
released source is `_digraph_group_chat.py`. Neither failure is capability evidence.

## Disposition and decision relevance

**Supported observation / explicit non-finding:** this probe demonstrates a
programming-model extraction boundary; it does not reproduce a new topology
contract defect. Historical beta.2 findings, transcripts and gallery remain
unchanged. Final cross-framework reconciliation can consume A1 independently.

Revise the applicability criterion to ask whether a **specific programming model
and public definition surface** exposes the fact and preserves its meaning.
"Every model in a framework must statically expose this field" is too strong:
SelectorGroupChat's missing declarations cannot disqualify a core field that
GraphFlow can expose. Conversely, this positive control alone neither justifies
a new core field nor certifies vendor neutrality or normative join semantics.

GraphFlow is a **candidate for static extraction of an explicit supported subset**,
with experimental API/version handling, callable-predicate omissions and
execution-versus-message graph semantics carried as limitations. SelectorGroupChat
supports participant inventory and input-specific runtime observation here;
a static dependency producer requires additional explicit declarations or a
separately validated restricted source-analysis approach. Do not merge these
candidate assessments into one AutoGen answer. No producer, upstream publication,
contract change, release gate, or broad negative claim is authorized by A1.
