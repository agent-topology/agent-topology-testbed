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
