---
search:
  exclude: true
---

# MkDocs to PDF

[![PyPi version](https://img.shields.io/pypi/v/mkdocs-to-pdf.svg)](https://pypi.org/project/mkdocs-to-pdf)
[![PyPi downloads](https://img.shields.io/pypi/dm/mkdocs-to-pdf.svg)](https://pypi.org/project/mkdocs-to-pdf)

---

`mkdocs-to-pdf` is an [`mkdocs`][mkdocs] plugin to generate a PDF from an `MkDocs` repository.

This repository is a fork of [`mkdocs-with-pdf`][mkdocs-with-pdf], which itself
was inspired by [mkdocs-pdf-export-plugin][mkdocs-pdf-export-plugin].

[mkdocs]: https://www.mkdocs.org/
[mkdocs-with-pdf]: https://github.com/orzih/mkdocs-with-pdf
[mkdocs-pdf-export-plugin]: https://github.com/zhaoterryy/mkdocs-pdf-export-plugin

## Features

- Supports [`mkdocs-material`][mkdocs-material].
- Supports [`pymdown-extensions`][pymdown-extensions].
- Automatically generated cover page and table of contents.
- Automatically numbered headings from h1 to h6.

[mkdocs-material]: https://squidfunk.github.io/mkdocs-material/
[pymdown-extensions]: https://facelessuser.github.io/pymdown-extensions/

## Samples

See the [`samples` directory](https://github.com/domWalters/mkdocs-to-pdf/tree/develop/samples)
for easily generated example PDF files showcasing standard Markdown syntax as
PDF.
