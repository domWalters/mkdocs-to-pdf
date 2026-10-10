---
name: run-one-test
description: Runs a single pytest test file or test case against the project venv
---

## What I do

Run `pytest` with arbitrary arguments using the project `.venv`, in-process
(`-n 0`) and without coverage for fast iteration.

Tests that render PDFs (e.g. `tests/test_build_pdf.py`) need the `WeasyPrint`
native libraries from the project environment (`source ./settings.sh`).

## How to use

```bash
scripts/bin/run-one-test tests/test_toc.py
scripts/bin/run-one-test tests/test_toc.py -k test_make_indexes
```

All arguments are passed straight through to `pytest`.
