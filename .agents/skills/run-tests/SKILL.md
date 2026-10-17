---
name: run-tests
description: Runs the test suite with hatch for the local Python or all supported versions
---

## What I do

Run the `pytest` suite through `hatch test`, running the MkDocs and ProperDocs
backends concurrently (each capped to half the available CPUs).

The end-to-end tests render PDFs, so run this inside the project environment
(`source ./settings.sh`).

## How to use

Run against the local interpreter:

```bash
make tests
```

Run across every supported Python version (3.11 through 3.15):

```bash
make tests-all
```

To target a single Python version:

```bash
make tests PY=3.11
```

This passes `-i py=3.11` to `hatch test`.

For fast iteration on one test file or case, prefer the `run-one-test` skill.
