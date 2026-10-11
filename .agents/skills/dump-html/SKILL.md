---
name: dump-html
description: Prints the combined HTML generated for a tests/fixtures/<name>/ site
---

## What I do

Build a `tests/fixtures/<name>/` site and print the assembled single-file HTML
(`single.html`) to stdout. This is the primary artifact for debugging page
collection, link/anchor rewriting and heading numbering.

Building a fixture renders a PDF, so run it inside the project environment
(`source ./settings.sh`).

## How to use

```bash
make sync-venv
.venv/bin/python scripts/bin/dump-html base
```

Print only the path to the generated file:

```bash
.venv/bin/python scripts/bin/dump-html base --path
```

An existing `.html` file can be passed instead of a fixture name.
