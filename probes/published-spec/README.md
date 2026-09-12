# Published spec comparison

The framework-free V1 runner consumes nine immutable JSON inputs through four
published spec installations. See [V1 evidence and reproduction](../../observations/V1/README.md)
for the question, inspected constraints, exact commands, results and limitations.

`run.py` installs into new isolated directories and saves commands/exits, artifact
digests, identities and two fresh-process observations per input and installation.
`adapter.py` and `adapter.mjs` use public package APIs. `compare.py` separates
acceptance, algorithm transitions, structure hashes and full canonical bytes.
`test_compare.py` exercises failure/classification controls on temporary copies
of saved records. This internal JSON shape is not a public protocol.

Dependencies are pinned independently under `locks/`. No framework, producer,
renderer suite, combined CI or upstream publication is involved.
