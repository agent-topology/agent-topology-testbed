# Published consumer compatibility boundaries

The framework-free K1 runner tests six controlled single-field mutations of V1's
minimal accepted document, plus one direct hash-computation-boundary call, through
the same four published spec installations V1 already established. See
[K1 evidence and reproduction](../../observations/K1/README.md) for the obligation
table, question, exact commands, compatibility matrix and limitations.

`mutate.py` builds the six document cases from
[`observations/V1/inputs/minimal.json`](../../observations/V1/inputs/minimal.json);
`generate_cases.py` fixed them once into `observations/K1/cases/` with their
independent, before-extraction expected outcomes in `observations/K1/cases.json`.
`run.py` reuses [V1's adapters](../published-spec/adapter.py) and
[locked installations](../published-spec/locks/) unchanged -- this probe pins no
second, potentially drifting copy of the same four packages -- and adds
`hash_adapter.py`/`hash_adapter.mjs`, which call `compute_structure_hash` /
`computeStructureHash` directly with an out-of-range `algorithm_version`,
bypassing `validate_document` entirely, to isolate the hash-computation boundary
from structural validation. `compare.py` builds the versioned compatibility
matrix against the fixed oracle. `test_mutate.py` and `test_compare.py` exercise
the mutation and classification logic on saved fixtures.

Dependencies are the ones already locked under `../published-spec/locks/`. No
framework, producer, renderer suite, combined CI or upstream publication is
involved.
