---
name: dump-pdf
description: Prints metadata, outline, destinations and links from a generated PDF
---

## What I do

Print a summary of a generated PDF using `pypdf`: page count, metadata, the
outline (bookmarks), named destinations and link-annotation count.

Building a fixture renders a PDF, so run it inside the project environment
(`source ./settings.sh`) when passing a fixture name.

## How to use

Build a fixture and summarise its PDF:

```bash
make sync-venv
.venv/bin/python scripts/bin/dump-pdf base
```

Or point at an existing PDF (e.g. the one printed by the `build-fixture` skill):

```bash
.venv/bin/python scripts/bin/dump-pdf /tmp/mkdocs-to-pdf-base-XXXX/site/pdf/document.pdf
```

Add `--text` to also print the extracted text of every page.
