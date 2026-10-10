---
name: build-package
description: Builds the mkdocs-to-pdf Python package using the Hatchling build backend
---

## What I do

Build the `mkdocs-to-pdf` wheel and source distribution.

## How to use

```bash
make build
```

This runs `uv lock` and `uv build`, producing artifacts in `dist/`.
