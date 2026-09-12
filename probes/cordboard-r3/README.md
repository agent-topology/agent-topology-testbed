# Cordboard R3 document-policy experiment

This is a literal model of **ADR-0007 Action 4**, not an implementation of
Cordboard or a safety test. The [observation](../../observations/cordboard-r3/README.md)
and [consumer reconciliation](../../findings/consumer-reconciliation.md) define
the question, source authority and bounded disposition.

The four recipes in `cases.json` and their expected model matches were authored
before extraction. All share three user nodes, START/END, a compiled name and
depth zero. Direct/conditional routing and compile-time interrupts are the only
structural factors. Conditional callbacks share declared destinations but return
different values when called directly after extraction. Every node body and any
router call during extraction raises; no graph is invoked.

`model.py` reads only ordinary direct edges and immediate target interrupts,
exactly as Action 4 specifies. A nonmatch means **not-rejected**, never safe.
Dynamic declarations, downstream searches, runtime policy and persistent override
presentation are outside this model. The override is a separate boolean input.
`verify.py` checks literal input facts before checking decisions; it never calls
the model to construct expectations. Its comparison removes only generatedAt.

From the repository root, using new output paths for every attempt:

```sh
rtk proxy python3 probes/cordboard-r3/setup.py --env .probe-runs/cordboard-r3/venv --out observations/cordboard-r3/setup
rtk proxy python3 probes/cordboard-r3/run.py --python .probe-runs/cordboard-r3/venv/bin/python --out observations/cordboard-r3/run
rtk proxy python3 probes/cordboard-r3/verify.py observations/cordboard-r3/run
rtk proxy python3 -m unittest discover -s probes/cordboard-r3 -p 'test_*.py' -v
```

Setup uses the unchanged [D1 lock](../published-producer/locks/requirements.txt),
hash-checked binary PyPI artifacts and an isolated venv. It records install
reports, commands, exit codes, stdout and stderr. Measurement saves input bytes
and source hashes before launching eight fresh isolated Python processes. Setup
and run refuse existing output directories; failures exit nonzero and remain
inspectable. The tests above inspect the committed observation; new runs can be
checked by passing their path to `verify.py`.

No application stack, network service, credentials, graph execution or release
gate is involved. Package installation is the only required network operation.
