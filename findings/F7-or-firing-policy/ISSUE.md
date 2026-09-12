# Clarify the boundary for first-trigger/once-only OR convergence

CrewAI 1.15.21's saved minimal sequential Flow runs show an OR listener on
`a,b` firing before `b`, once total, with no second invocation after `b`.
When `b` never runs it still fires once. The paired AND cases wait for both
and do not fire when only `a` runs.

[F7 evidence and reproduction](https://github.com/agent-topology/agent-topology-testbed/tree/dc6e9a39fd62f66c091d677e0a04ed629e3428bd/findings/F7-or-firing-policy)
links the four paired execution records, static/callable evidence and hash audit.
This is an unposted draft; the evidence link is pinned to the merged testbed input.

At upstream `3715dd32a0efc3e7bd500d26d038774d6a37f4e6` and
`eb0e2d8a95cb2fd0e0daebba18507ab5acdd34fe`, the schema, consuming guide and
Python join helper agree that joins retain implicit AND semantics. Beta.2's
contract and ADR 0003 already distinguish all-source joins from independent
edges; the later helper is not a published beta.2 API.

Mapping OR to direct `a → join` and `b → join` edges preserves connectivity.
It does not select between firing for each trigger (two invocations on ordered
`a,b`) and firing only for the first trigger (one). The latter requires a
latch/reset policy not supplied by the inspected contract. Waiting for both
also contradicts the early-firing/only-a observations.

The narrow concern is **unrepresented OR firing policy**, not absence of join
semantics. This is a contract inspection and an authored consumer comparison,
not output of a CrewAI producer or a measured upstream execution. Exported
CrewAI static accessors expose AND/OR, but their documentation coverage remains
limited. Races, cycles and rearming are outside the observed cases.

Please clarify whether this policy is deliberately outside consumer scope,
or identify a normative mapping preserving early firing and suppression of the
later trigger, including its reset boundary. If richer interpretation is
desired, these four records supply minimal acceptance inputs. No particular
schema field, extension, release deadline or core change is requested.
