---
name: build-fixture
description: Builds a tests/fixtures/<name>/ MkDocs site and prints the generated artifact paths
---

## What I do

Copy a `tests/fixtures/<name>/` site to a temporary directory and build it with
a real `mkdocs build` (as the end-to-end tests do), then print the generated
`site/`, combined HTML and PDF paths so they can be inspected.

Renders a PDF, so run it inside the project environment
(`source ./settings.sh`).

## How to use

```bash
make sync-venv
.venv/bin/python scripts/bin/build-fixture base
.venv/bin/python scripts/bin/build-fixture issue-95
```

Available fixtures are the directories under `tests/fixtures/`.
