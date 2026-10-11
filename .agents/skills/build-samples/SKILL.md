---
name: build-samples
description: Builds the sample MkDocs projects and their generated PDFs
---

## What I do

Build the `samples/mkdocs` and `samples/mkdocs-material` sites. Each uses the
`to-pdf` plugin to render a PDF from a third-party documentation set, which
needs the `WeasyPrint` native libraries from the project environment
(`source ./settings.sh`).

## How to use

```bash
make samples
```
