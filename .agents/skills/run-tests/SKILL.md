---
name: run-tests
description: Runs the full test suite with hatch across all supported Python versions
---

## What I do

Run the full `pytest` suite through `hatch test` for every supported Python
version (3.11 through 3.14).

The end-to-end tests render PDFs, so run this inside the project environment
(`source ./settings.sh`).

## How to use

```bash
make tests
```

To run against a single Python version:

```bash
make tests PY=3.11
```

This passes `-i py=3.11` to `hatch test` instead of `--all`.

For fast iteration on one test file or case, prefer the `run-one-test` skill.
