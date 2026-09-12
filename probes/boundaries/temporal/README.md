# Temporal boundary inspection (T1)

Question: can public SDK definition inspection expose the invocation structure
of a two-activity linear workflow versus an input-dependent activity choice?

Read [T1's evidence record](../../../observations/T1/README.md) for the result,
public-API search, all seven matrix answers, and exact setup/run commands.

`fixtures.py` is the complete tiny input; `expected.json` contains independent
literal expectations. `inspect_definitions.py` inspects Python metadata and
public SDK schemas without a Worker, private accessors, or workflow/activity
body invocation. `test_inspection.py` checks evidence integrity. Dependencies
are isolated in `requirements.txt` / `requirements.lock` and `.venvs/temporal`.

This is a static inspection demonstration, not a Temporal execution, a graph
exporter, or a topology producer.
