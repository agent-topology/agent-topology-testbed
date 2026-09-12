# Reproduce P0

Run from the repository root in a POSIX shell. Verified environment: macOS arm64,
CPython **3.11.16**, `uv 0.12.10`. The locks resolve for this platform; other OSes
and Python versions are not verified. The scripts reject other Python patch or
framework versions. Report installation/API failures without changing the pins.
No agent-topology package, renderer build, scheduler, or service is required.

## Inspect before setup

Read [Airflow smoke input](airflow/smoke.py), [Dagster smoke input](dagster/smoke.py),
their literal expectations, and [P0's question/limitations](../observations/P0/README.md).
Inspect the direct requirements, full resolved pins/hashes, and vendored official
Airflow constraints **before** installing. Locks include transitive runtime
dependencies; source distributions may need a compiler/build tools. They do not
pin an OS image or build-tool environment.

```sh
cat probes/airflow/requirements.txt probes/airflow/constraints-3.11.txt
cat probes/airflow/requirements.lock
cat probes/dagster/requirements.txt probes/dagster/requirements.lock
uv --version
uv python install 3.11.16
```

## Airflow setup

Use a new `.venvs/airflow` directory for clean reproduction. Do not reuse an
environment with unrelated packages. `sync` installs the committed lock without
re-resolving dependencies; `--require-hashes` verifies downloaded distributions.

```sh
uv venv --python 3.11.16 .venvs/airflow
uv pip sync --python .venvs/airflow/bin/python --require-hashes probes/airflow/requirements.lock
uv pip check --python .venvs/airflow/bin/python
```

## Airflow run

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/airflow/bin/python probes/airflow/smoke.py --mode static --output .probe-runs/airflow-static-$n.json > .probe-runs/airflow-static-$n.log 2>&1
  .venvs/airflow/bin/python probes/airflow/smoke.py --mode execution --output .probe-runs/airflow-$n.json > .probe-runs/airflow-$n.log 2>&1
done
cmp .probe-runs/airflow-static-1.json .probe-runs/airflow-static-2.json
cmp .probe-runs/airflow-1.json .probe-runs/airflow-2.json
```

Each command clears inherited Airflow settings before importing it, changes into
a fresh temporary directory, and removes that state afterwards. Execution first
runs `python -m airflow db migrate` against its own SQLite database, then
`dag.test()` at the fixed logical date `2024-01-02T00:00:00Z`.

## Airflow branch/join run (P1)

Same `.venvs/airflow` environment as above; no separate install. Read
[the branch/join probe](airflow/branch.py) and [P1's question/expected states](../observations/P1/README.md)
before running.

```sh
set -eu
mkdir -p .probe-runs
for case in single multiple none; do
  for n in 1 2; do
    .venvs/airflow/bin/python probes/airflow/branch.py --case "$case" --mode static \
      --output ".probe-runs/branch-$case-static-$n.json" > ".probe-runs/branch-$case-static-$n.log" 2>&1
    .venvs/airflow/bin/python probes/airflow/branch.py --case "$case" --mode callable \
      --output ".probe-runs/branch-$case-callable-$n.json" > ".probe-runs/branch-$case-callable-$n.log" 2>&1
    .venvs/airflow/bin/python probes/airflow/branch.py --case "$case" --mode execution \
      --output ".probe-runs/branch-$case-$n.json" > ".probe-runs/branch-$case-$n.log" 2>&1
  done
  cmp ".probe-runs/branch-$case-static-1.json" ".probe-runs/branch-$case-static-2.json"
  cmp ".probe-runs/branch-$case-callable-1.json" ".probe-runs/branch-$case-callable-2.json"
  cmp ".probe-runs/branch-$case-1.json" ".probe-runs/branch-$case-2.json"
done
```

Each case builds DAG `p1_branch` with the router's callback hardcoded to that
case's return value, then isolates state exactly as the P0 Airflow run does.
`--mode execution` also produces the `static` and `callable` sections; the
standalone `static`/`callable` modes skip `airflow db migrate` and `dag.test()`
entirely, so they carry no execution evidence.

## Airflow grouping/roots/join run (P3)

Same `.venvs/airflow` environment as above; no separate install. Read
[the grouping probe](airflow/grouping.py) and [P3's question/expected facts](../observations/P3/README.md)
before running.

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/airflow/bin/python probes/airflow/grouping.py --mode static \
    --output ".probe-runs/grouping-static-$n.json" > ".probe-runs/grouping-static-$n.log" 2>&1
  .venvs/airflow/bin/python probes/airflow/grouping.py --mode execution \
    --output ".probe-runs/grouping-$n.json" > ".probe-runs/grouping-$n.log" 2>&1
done
cmp .probe-runs/grouping-static-1.json .probe-runs/grouping-static-2.json
cmp .probe-runs/grouping-1.json .probe-runs/grouping-2.json
```

Builds DAG `p3_grouping`: one `TaskGroup` with two parallel members, a
predecessor and successor crossing its boundary, and a two-source convergence
join reusing P1's `none_failed_min_one_success` rule, then isolates state
exactly as the P0 Airflow run does. `--mode execution` also produces the
`static` section; the standalone `static` mode skips `airflow db migrate` and
`dag.test()` entirely, so it carries no execution evidence. This probe runs one
case, not P1's matrix, because it reuses P1's trigger-rule evidence rather than
retesting it — see P3's README for why.

## Dagster setup

```sh
uv venv --python 3.11.16 .venvs/dagster
uv pip sync --python .venvs/dagster/bin/python --require-hashes probes/dagster/requirements.lock
uv pip check --python .venvs/dagster/bin/python
```

## Dagster run

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/dagster/bin/python probes/dagster/smoke.py --mode static --output .probe-runs/dagster-static-$n.json > .probe-runs/dagster-static-$n.log 2>&1
  .venvs/dagster/bin/python probes/dagster/smoke.py --mode execution --output .probe-runs/dagster-$n.json > .probe-runs/dagster-$n.log 2>&1
done
cmp .probe-runs/dagster-static-1.json .probe-runs/dagster-static-2.json
cmp .probe-runs/dagster-1.json .probe-runs/dagster-2.json
```

Each process clears inherited Dagster settings and uses a new temporary home and
working directory. Execution uses `DagsterInstance.ephemeral(tempdir=home)` and
`execute_in_process(raise_on_error=True)`, with in-memory output storage.

## Dagster conditional-outputs run (P2)

Same `.venvs/dagster` environment as above; no separate install. Read
[the conditional-outputs probe](dagster/conditional.py) and
[P2's question/expected states](../observations/P2/README.md) before running.

```sh
set -eu
mkdir -p .probe-runs
for case in none single multiple; do
  for n in 1 2; do
    .venvs/dagster/bin/python probes/dagster/conditional.py --case "$case" --mode static \
      --output ".probe-runs/conditional-$case-static-$n.json" > ".probe-runs/conditional-$case-static-$n.log" 2>&1
    .venvs/dagster/bin/python probes/dagster/conditional.py --case "$case" --mode execution \
      --output ".probe-runs/conditional-$case-$n.json" > ".probe-runs/conditional-$case-$n.log" 2>&1
  done
  cmp ".probe-runs/conditional-$case-static-1.json" ".probe-runs/conditional-$case-static-2.json"
  cmp ".probe-runs/conditional-$case-1.json" ".probe-runs/conditional-$case-2.json"
done
```

Each case runs job `p2_conditional` with `conditional_source`'s op config
hardcoded to that case's emitted-output list, then isolates state exactly as
the P0 Dagster run does (`DagsterInstance.ephemeral(tempdir=home)`, fresh
`DAGSTER_HOME`). `--mode execution` also produces the `static` section; the
standalone `static` mode never calls `execute_in_process()`, so it carries no
execution evidence.

## Dagster nested boundaries/convergence run (P4)

Use the same isolated Dagster setup and unchanged lock above. Read
[the nested input and literal expectations](dagster/nested.py) and
[P4's question/API limitations](../observations/P4/README.md) first.

```sh
set -eu
mkdir -p .probe-runs
for n in 1 2; do
  .venvs/dagster/bin/python probes/dagster/nested.py --mode static \
    --output ".probe-runs/nested-static-$n.json" > ".probe-runs/nested-static-$n.log" 2>&1
  .venvs/dagster/bin/python probes/dagster/nested.py --mode execution \
    --output ".probe-runs/nested-$n.json" > ".probe-runs/nested-$n.log" 2>&1
done
cmp .probe-runs/nested-static-1.json .probe-runs/nested-static-2.json
cmp .probe-runs/nested-1.json .probe-runs/nested-2.json
.venvs/dagster/bin/python probes/dagster/test_nested.py
```

Graph `p4_nested` invokes the same two-op child as `left` and `right`, with
top-level inputs `1` and `2`, then passes both outputs to `consume`. Five op
steps execute; the two graph invocations have mapped outputs, not separate op
step states. The standalone static mode never creates or executes a job.
Execution uses a fresh temporary home and an ephemeral instance, as in P0/P2.
`test_nested.py` checks that identity/edge loss, a crossed boundary mapping,
wrong execution input, and an unsupported version exit nonzero under `-O`;
it also prevents execution entry points in a standalone static run.

## Failure interpretation

All commands must exit zero before records count as evidence. Assertions raise
explicit exceptions even with Python `-O`; missing dependencies, wrong versions,
database/API failures, and output errors also exit nonzero. `cmp` returns nonzero
on differences. Read the corresponding `.log` on failure; never use a stale JSON
file as a pass. Raw logs include transient timestamps, paths, PIDs, and run IDs;
JSON contains the normalized facts described in [P0](../observations/P0/README.md).

## Lock provenance and deliberate regeneration

`airflow/constraints-3.11.txt` is the unmodified
[Airflow 2.10.5 official Python 3.11 constraint file](https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt).
The direct inputs are `apache-airflow==2.10.5` and `dagster==1.13.22`, separately.
The following commands generated the locks using uv 0.12.10; regeneration is a
reviewed dependency change, **not** a reproduction step. Inspect the resulting
pins and hashes again before installation, then rerun both observations for the
affected framework and record new provenance.

```sh
uv pip compile probes/airflow/requirements.txt --constraint probes/airflow/constraints-3.11.txt --python-version 3.11.16 --generate-hashes --output-file probes/airflow/requirements.lock
uv pip compile probes/dagster/requirements.txt --python-version 3.11.16 --generate-hashes --output-file probes/dagster/requirements.lock
```
