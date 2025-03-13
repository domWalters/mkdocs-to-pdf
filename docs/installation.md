# Installation

`mkdocs-to-pdf` is available on [PyPi](https://pypi.io/project/mkdocs-to-pdf):

```bash
pip install mkdocs-to-pdf
```

The `[dev]` extras supply the dependencies for the examples in the
[`samples` directory](https://github.com/domWalters/mkdocs-to-pdf/tree/develop/samples):

```bash
pip install mkdocs-to-pdf[dev]
```

## WeasyPrint

`mkdocs-to-pdf` depends on [`weasyprint`][weasyprint].

`weasyprint` has OS specific dependencies. Follow the guidance in the
[`weasyprint` documentation][weasyprint-install].

[weasyprint]: http://weasyprint.org/
[weasyprint-install]: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
