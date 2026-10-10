---
name: use-python
description: Runs a Python command with mkdocs_to_pdf importable from the project venv
---

## What I do

Run an ad-hoc Python snippet with the project's dependencies and the
`mkdocs_to_pdf` package importable.

## How to use

```bash
make sync-venv
.venv/bin/python -c "<python-code>"
```
