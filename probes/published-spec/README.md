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

`generated/` adds E1: an independently locked Hypothesis generator, two persistent
beta.2 batch adapters, validity-preserving shrinking, fresh V1 one-shot replays
and a saved-evidence repeat audit. See [E1 reproduction and disposition](../../observations/E1/README.md).
The original V1 adapters, locks and saved evidence remain unchanged.

`run_v2.py` and `compare_v2.py` add V2's isolated beta.2→beta.3 transition
without changing that historical runner. They reuse the beta.2 locks unchanged,
add independent `py-b3` / `js-b3` locks, and compare validation, full canonical
bytes and complete structure-hash tuples separately. See
[V2 evidence and reproduction](../../observations/V2/README.md).

`replay_e2.py`, `compare_e2.py` and `verify_e2.py` add E2 without rerunning the
E1 generator. They verify and stream E1's exact saved population through V2's
four lock-only installations, replay every minimum individually, keep unsafe
integer compatibility boundaries separate, and compare two fresh captures. See
[E2 evidence and reproduction](../../observations/E2/README.md).
