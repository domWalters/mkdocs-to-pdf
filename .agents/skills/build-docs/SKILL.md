---
name: build-docs
description: Builds the MkDocs documentation site, including its generated PDF
---

## What I do

Build the repository documentation in `docs/` into `site/` with `mkdocs build`.
The `to-pdf` plugin is enabled in `mkdocs.yml`, so this also renders the
documentation PDF, which needs the `WeasyPrint` native libraries from the
project environment (`source ./settings.sh`).

## How to use

```bash
make docs
```
