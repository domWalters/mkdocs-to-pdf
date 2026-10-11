# `mkdocs-to-pdf`

## What is it?

An [`mkdocs`](https://www.mkdocs.org/) plugin that renders a whole MkDocs
repository into a single PDF.

The plugin collects every page during the build, assembles them into one
combined HTML document, rewrites cross-page links into in-document anchors, and
renders the result with [`WeasyPrint`](https://weasyprint.org/). It supports
the [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/) theme,
cover and back-cover pages, an automatically numbered table of contents and
`pymdown-extensions`.

This repository is a fork of
[`mkdocs-with-pdf`](https://github.com/orzih/mkdocs-with-pdf).

```yaml
plugins:
  - to-pdf
```

## Directory Layout

```txt
docs/
    installation.md             - Installation instructions
    usage.md                    - Reference for every plugin option
    examples/                   - MkDocs Material feature showcase pages
    stylesheets/                - Extra CSS for the documentation site
hooks/
    generate-agents-skills.py   - Pre-commit hook that syncs the skills listing in AGENTS.md
samples/
    mkdocs/                     - Sample site that renders the mkdocs docs to PDF
    mkdocs-material/            - Sample site that renders the mkdocs-material docs to PDF
scripts/
    settings-venv.sh            - Create / sync the venv and activate it
    settings-post-venv.sh       - Put scripts/bin on PATH
    update_version.sh           - Cut a release branch, bump the version and tag
src/mkdocs_to_pdf/
    plugin.py                   - MkDocs plugin entry point (WithPdfPlugin)
    options.py                  - Plugin config scheme and resolved Options
    generator.py                - Collects pages and renders the combined PDF
    cover.py                    - Renders the cover and back cover
    toc.py                      - Builds the table of contents and heading numbering
    drivers/                    - Optional JavaScript rendering drivers
    preprocessor/               - Rewrite hrefs / ids and absolutize asset URLs
    styles/                     - SCSS compiled to the print stylesheet
    templates/                  - Jinja2 cover templates and filters
    themes/                     - Per-theme handlers (generic, mkdocs, material)
    utils/                      - BeautifulSoup helpers (sections, emoji, iframes, images, ...)
tests/
    conftest.py                 - Fixtures: make_options, make_soup, built_<fixture>
    fixtures/                   - Minimal MkDocs sites used by the end-to-end tests
    test_*.py                   - Unit and end-to-end tests
.agents/skills/                 - Agent skills (sanctioned commands) for this repository
```

## Commands

As soon as you've finished reading this file, read the following skills:

<!-- BEGIN_SKILLS -->
```txt
.agents/skills
├── build-docs                 - Builds the MkDocs documentation site and its generated PDFs
├── build-fixture              - Builds a tests/fixtures/<name>/ MkDocs site and prints the generated artifact paths
├── build-package              - Builds the mkdocs-to-pdf Python package using the Hatchling build backend
├── build-samples              - Builds the sample MkDocs projects and their generated PDFs
├── check-modified-files       - Runs pre-commit checks against modified files that aren't yet committed
├── check-whole-repo           - Runs pre-commit checks across the entire mkdocs-to-pdf repository
├── dump-html                  - Prints the combined HTML generated for a tests/fixtures/<name>/ site
├── dump-pdf                   - Prints metadata, outline, destinations and links from a generated PDF
├── run-one-test               - Runs a single pytest test file or test case against the project venv
├── run-tests                  - Runs the full test suite with hatch across all supported Python versions
└── use-python                 - Runs a Python command with mkdocs_to_pdf importable from the project venv
```
<!-- END_SKILLS -->

## Environment

`WeasyPrint` needs native libraries (GLib/GObject, Pango and Fontconfig) that
are pinned by `shell.nix`. Enter the environment before any command that
renders a PDF (`make docs`, `make samples`, and the `build-fixture`,
`dump-html`, `dump-pdf` and `run-tests` skills); otherwise rendering fails with
`cannot load library 'gobject-2.0-0'`.

```bash
source ./settings.sh
```

`settings.sh` enters the `nix-shell`, syncs the venv and puts `scripts/bin` on
`PATH`. If you are already inside the shell, source `scripts/settings-venv.sh`
instead. For a one-off, non-interactive run:

```bash
nix-shell --run "<command>"
```

## Always do

- Use relevant skills where possible, before running arbitrary commands
- Run the test suite after making changes
- Fix test errors
- Run the lints after making changes
- Fix linting errors
- Add docstrings to new public classes, functions, methods, etc.
- Keep tests as simple as possible
- Add a `tests/fixtures/<name>/` MkDocs site (or a `make_soup` snippet) that
  reproduces any new behaviour, and assert on the combined HTML
- Document any new plugin option in `docs/usage.md`
- Check for manually made local changes by a developer working on the code base
  at the same time as you

## Never do

- Run `pytest` manually; always use the `run-one-test` / `run-tests` skills
- Run `make all`, `make publish` or `make distclean` unless explicitly asked
- Destructive `git` actions
- Commit generated artifacts (`site/`, `dist/`, `.venv`, `.coverage*`,
  `.htmlcov/`, `.junit.xml`, `samples/*/gen/`)
- Edit the contents of the `samples/mkdocs/mkdocs` or
  `samples/mkdocs-material/mkdocs-material` submodules
- Use the `Any` type, unless it is for `args` or `kwargs`
- Use commands that leave this repository; except to use the `/tmp` directory

## Key Conventions

- Python `>= 3.11`; typing is strict (`mypy` in `strict` mode, `ty` with
  `all = "error"`)
- `ruff` is configured with `select = ["ALL"]`; add targeted ignores using the
  `# ruff: ignore[error-code]` style
- HTML is processed with `BeautifulSoup`; styles are written as SCSS and
  compiled through `libsass`; the PDF is rendered by `WeasyPrint`
- Plugin options are declared in `Options.config_scheme` in
  `src/mkdocs_to_pdf/options.py` and resolved in `Options.__init__`
- Theme-specific behaviour lives in a per-theme module under
  `src/mkdocs_to_pdf/themes/`
- Tests live in `tests/` and are named `test_*.py`; reuse the `make_options` and
  `make_soup` fixtures from `tests/conftest.py`, and the session-scoped
  `built_<fixture>` fixtures generated from `tests/fixtures/<dir>`
- Prefer small, pure transform functions that take a `BeautifulSoup` and mutate
  it, so they can be unit-tested with `make_soup`

## Common Agent Tasks

- Add a plugin option:

    1. Add it to `Options.config_scheme` and resolve it in `Options.__init__`
    1. Thread it through `Generator`, the relevant theme module, or `styles` as
       needed
    1. Document it in `docs/usage.md`
    1. Add or extend a test under `tests/` (`make_options` / `make_soup`, or a
       `tests/fixtures/<name>/` site for end-to-end behaviour)
    1. Run the `run-tests` and `check-modified-files` skills

- Fix a rendering bug:

    1. Add a minimal `tests/fixtures/<name>/` MkDocs site, or an HTML snippet
       via `make_soup`, that reproduces the issue
    1. Add a failing test in `tests/` that captures the expected output
    1. Fix the transform in `src/mkdocs_to_pdf/`
    1. Run the `run-tests` and `check-modified-files` skills
