---
name: build-docs
description: Builds the MkDocs documentation site and its generated PDFs
---

## What I do

Build the repository documentation in `docs/` into `site/` with `mkdocs build`.
The `to-pdf` plugin is enabled in `mkdocs.yml`, so this also renders the
documentation PDF, which needs the `WeasyPrint` native libraries from the
project environment (`source ./settings.sh`).

The `hooks/publish-fixture-pdfs.py` hook also builds every `tests/fixtures/<name>`
site, copies its PDF to `site/fixtures/<name>.pdf`, and generates the
`Example PDFs` page (`site/examples/example-pdfs/`) that links to them.

## How to use

```bash
make docs
```
