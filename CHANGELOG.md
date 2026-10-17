# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Verify support for properdocs, and prefer it (#109)
- Support extra variables in CSS styles (#121)
- Implement #75 and add missing docs / tests for exclusions

### Documentation
- Add page on various ways to render maths

## [0.12.1] - 2026-10-12

### Documentation
- Add documentation for #27

### Fixed
- Apply PR #101
- Avoid docs regression caused by weasyprint update (#122)

## [0.12.0] - 2026-10-11

### Added
- Make barcode and qrcode optional, add custom_template_path docs
- Support HTML in the copyright option
- Support Python 3.15
- Update weasyprint
- Add test and documentation for #47

### Changed
- Overhaul basic project setup
- Massive code cleanup

### Documentation
- Address #40

### Fixed
- Install fonts correctly in shell.nix
- Stop logger being used when it is None
- Allow headers to be used without their parent header (#95)
- Address #34, #35, #62, and #92 within our SCSS
- Address #116 by scaling the images to the page height
- Set the PDF metadata
- Address #88
- Address #85
- Sometimes chromium runs before the temp file actually flushes
- Address remaining concerns from #82
- Address #73

### Other
- Fix image style retrieval in fix_image_alignment function
- Merge pull request #113 from rocom-service/develop

Fix inline image style parsing in image alignment preprocessing

## [0.11.1] - 2026-04-28

### Fixed
- Add project to requirements files

## [0.11.0] - 2026-04-28

### Added
- Support nixos, move to python3.10 by default (#87)
- Add 'html_path' for further Epub conversion from combined html (#97)
- Drop python 3.9, add python 3.14
- Allow subtitle to be used in SCSS (#93)

### Documentation
- Update license year
- Delete CONTRIBUTING.md
- Delete CHANGELOG
- Remove stuff-to-migrate.md from the output docs
- Update copyright year
- General README updates

### Fixed
- PDF download link(material only) with pdf_event_hook.py #66 (#67)
- Remove download link example (#76)
- Avoid `AttributeError` caused by unset `self._cover_title` when `cover` is False (#83)
- Remove "None" when there is no author, copyright, or subtitle (#91)
- Change incorrect path in shell.nix
- Allow the local `copyright` variable to overwrite the top level one

### Other
- Merge pull request #110 from domWalters/refactor-basic-cleanup

## [0.10.1] - 2025-05-08

### Added
- Add more to pre-commit, add cSpell configuration (#56)
- Make package dependencies more flexible #64 (#69)

### Other
- Fix repo icon and update logo icon(PDF) (#61)

## [0.10.0] - 2025-03-16

### Added
- Change default font family to Roboto and Noto Sans (#24)
- Migrate to pyproject.toml (#28)
- Move to one makefile that build everything, and one .venv
- Regenerate mkdocs and mkdocs-material samples (#29)
- Integrate an experimental PDF download link using the download_link option #25 (#44)

### Changed
- Initial naive switch to pyproject.toml
- More with-pdf to to-pdf
- More with-pdf to to-pdf

### Documentation
- Update CHANGELOG
- Rewrite all documentation (#45)

### Fixed
- Change requirements files after samples moved
- Apply the minimum changes to get the project to compile
- Use `mkdocs-to-pdf` in `generate-requirements-full`
- Swap `make build` for something that works in POSIX
- Downgrade weasyprint and pydyf due to layout issues in the latest version (#43)

### Other
- Mkdocs-material custom checkbox overlap and ordered list alignment
- Mkdocs-material blockquote layout
- Merge pull request #18 from hkato/develop

fix: mkdocs-material custom checkbox overlap, ordered list alignment, and blockquote
- Merge pull request #38 from domWalters/develop-2

chore: actually merge the PR

## [0.9.4] - 2024-01-28

### Fixed
- Fixed issue 114, AttributeError
- Add CSS to realign mkdocs-material admonitions

### Other
- First commit.
- Added sample output PDFs.
- Update PiPy repository name.
- Ready to update.
- Update sample docs source.
- Fixed for the material theme's polyfill style.
- Update sample output.
- For Release v0.2.1
- Add page break rule for tabs.
- Move custom style source tree.
- For Release v0.2.2
- Update the dependent packages version.
- Fixed to skip empty pages.
- Update the sample output of mkdocs-material.
- Fixed some links in README.md
- For Release v0.2.3
- Update Pipfile.lock
- Fixed some bugs.
- Excluded form empty tags if it has image.
- For Release v0.2.4
- Bump lodash in /custum_style_src/material-polyfills

Bumps [lodash](https://github.com/lodash/lodash) from 4.17.15 to 4.17.19.
- [Release notes](https://github.com/lodash/lodash/releases)
- [Commits](https://github.com/lodash/lodash/compare/4.17.15...4.17.19)

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #5 from orzih/dependabot/npm_and_yarn/custum_style_src/material-polyfills/lodash-4.17.19

Bump lodash from 4.17.15 to 4.17.19 in /custum_style_src/material-polyfills
- Update README.md
- Fixed for the internal href transform.
- Modified debug logs for 'TOC'.
- Adds an anchor to the root of each page, fixes #3.
- Updated sample output of `mkdocs-material`, fixes #4.
- Add an option for page exclusion, issue #4.
- For Release v0.3.0
- Added special link processing for "index.html", issue #3.
- For Release v0.3.1
- Bump elliptic in /custum_style_src/material-polyfills

Bumps [elliptic](https://github.com/indutny/elliptic) from 6.5.2 to 6.5.3.
- [Release notes](https://github.com/indutny/elliptic/releases)
- [Commits](https://github.com/indutny/elliptic/compare/v6.5.2...v6.5.3)

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #7 from orzih/dependabot/npm_and_yarn/custum_style_src/material-polyfills/elliptic-6.5.3

Bump elliptic from 6.5.2 to 6.5.3 in /custum_style_src/material-polyfills
- (change vs-code settings)
- Fixed current page refs when `use_directory_urls=false`, issue #8
- For Release v0.3.2
- Fixed current page refs in subdirectories w/o directory-urls, issue #8
- For Release v0.3.3
- Update README.md
- Bump dependency versions.
- Fix mkdocs sample broken links.
- Update sample docs for `mkdocs material`.
- Add workaround converter for twemoji.
- Add a TOC title text option, issue #11.
- Change to an accurate test pattern.
- Fix testcase.
- Fixed `a[href]` and `anchor id` of internal link.
- Merge pull request #9 from orzih/hotfix/links

Fixed hrefs and anchors for internal links.
- (update samples)
- For Release v0.4.0
- Update README.md
- Fixed a bug that an error occurs when the `output_path` option is only a filename.
- Supports nested sections in `nav`.
- Fixed a bug that an exception occurs with `exclude_pages` option.
- Fixed few sequence and resources.
- Merge pull request #12 from orzih/feature/support-nested-sections

Supports nested sections in `nav`.
- Bump dependencies in /custum_style_src/material-polyfills.
- Add `Keyboard key` style in material-polyfills.
- Update workaround for twemoji.
- For Release v0.5.0
- Change the required version of python.
- Bump dependency versions.
- Update output sample of `mkdocs material`.
- Modified some 'page-break' settings.
- Add 'convert_iframe' option.
- Ready to support render with JS.
- For Release v0.6.0
- Bump dependencies in /custum_style_src/material-polyfills.
- Add the missing anchors if the document doesn't have first-level headings, issue #15
- Add a workaround converter for 'img[align]', issue #14
- For Release v0.6.1
- Update output sample of `mkdocs material`.
- Bump dependencies in /custum_style_src/material-polyfills.
- Modified some styles.
- Support two-columns layout.
- Wrapped tabbed-set contents.
- Bump dependency versions.
- Fix details icon style for material.
- Update README.md
- Update 'mkdocs-material' sample contents.
- Implement the polyfill-script builder for `material`.
- Implementation for the JS rendering.
- Modified for the settings of `material` sample.
- Merge pull request #16 from orzih/feature/use-headless-chrome

Supports the use of `Headless Chrome`.
- For Release v0.7.0
- For Release v0.7.1
- Bump dependencies in /custum_style_src/material-polyfills.
- Add Docker templates.
- Fixed links containing escape characters, issue #20
- For Release v0.7.2
- Fixed links hash that contains percent encoding, issue #20
- For Release v0.7.3
- Fixed links for `href` without a trailing slash, issue #21
- Add `show_anchors` option.
- For Release v0.7.4
- Change font of `tiny` docker image.
- Update Dockerfile for alpine.
- Bump dependency versions.
- Update 'mkdocs-material' sample contents.
- Fix links on sample 'mkdocs-material' content.
- Update output sample of `mkdocs material`.
- Fixed linter error
- Fixed links that contains percent encoding, issue #25
- Support for strict mode, issue #24
- For Release v0.7.5
- Allow user to set theme-path in localconf
- Merge pull request #27 from AbdealiJK/ajk-theme-dir

options: Allow user to set theme-path in localconf
- Update Dockerfile for debian.
- For Release v0.7.6
- Bump dependency versions.
- Update output sample of `mkdocs material`.
- Fixed not escaping single quotes in style, issue #29
- For Release v0.7.7
- Support for custom templates and stylesheets
- Default cover page with jinja
- Added shortcut to plugin_variables to use in jinja templates
- Do not compress css output when html_debug is enabled for better readability
- Added 'Custom cover page and document style' to README
- Merge pull request #32 from GreyRook/jinja

Basic templating / customization support based on Jinja
- Added warning detection during processing in bs4.
- Redefined the template handler.
- Added a logo on the cover page.
- Fixed a crash without `cover_logo` option.
- Fixed text escaping and jinja2 filters.
- Modified the jinja2 filters.
- Added back cover generation option.
- Merge pull request #33 from orzih/feature/support-jinja-template

Basic templating / customization support based on Jinja
- Added html unescaping process at variable strings.
- Update output sample of `mkdocs material`.
- For Release 0.8.0
- Update output sample of `mkdocs material`, issue #36

* Updated WeasyPrint version to v52.1.
- Removed compressed css output_style to avoid problems with umlauts
- Merge pull request #38 from GreyRook/no-compiled-css

removed compressed css output_style to avoid problems with umlauts
- For Release 0.8.1
- Bump dependency versions.
- Bump ini from 1.3.5 to 1.3.8 in /custum_style_src/material-polyfills

Bumps [ini](https://github.com/isaacs/ini) from 1.3.5 to 1.3.8.
- [Release notes](https://github.com/isaacs/ini/releases)
- [Commits](https://github.com/isaacs/ini/compare/v1.3.5...v1.3.8)

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #40 from orzih/dependabot/npm_and_yarn/custum_style_src/material-polyfills/ini-1.3.8

Bump ini from 1.3.5 to 1.3.8 in /custum_style_src/material-polyfills
- Bump dependencies in /custum_style_src/material-polyfills.
- Bump dependency versions.
- Update output sample of `mkdocs material`.
- Added headless-chrome launch options.
- README explains how to use ENABLE_PDF_EXPORT

This fleshes out the section on the `enabled_if_env` configuration
parameter with motivation and code examples that show how to run
`mkdocs build` and `mkdocs serve` in the common use case.

Fixes #41
- Merge pull request #43 from mikesamuel/issue-41-pr

README explains how to use ENABLE_PDF_EXPORT
- Bump cairosvg from 2.5.0 to 2.5.1

Bumps [cairosvg](https://github.com/Kozea/CairoSVG) from 2.5.0 to 2.5.1.
- [Release notes](https://github.com/Kozea/CairoSVG/releases)
- [Changelog](https://github.com/Kozea/CairoSVG/blob/master/NEWS.rst)
- [Commits](https://github.com/Kozea/CairoSVG/compare/2.5.0...2.5.1)

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #44 from orzih/dependabot/pip/cairosvg-2.5.1

Bump cairosvg from 2.5.0 to 2.5.1
- Bump dependency versions.
- Added highlighttable style for material.
- Added a rendering hook module handler.
- Changed to collect JS for each page.
- For Release 0.8.2
- Drop support for Python 3.5.
- (update README.md)
- Add .gitattributes
- Update README.md
- Bump dependency versions.
- Update output sample of `mkdocs material`.
- Supports mkdocs-material theme v7.x.
- Bump pillow from 8.1.0 to 8.1.1

Bumps [pillow](https://github.com/python-pillow/Pillow) from 8.1.0 to 8.1.1.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/8.1.0...8.1.1)

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #54 from orzih/dependabot/pip/pillow-8.1.1

Bump pillow from 8.1.0 to 8.1.1
- Bump dependencies in /custum_style_src/material-polyfills.
- Update output sample of `mkdocs material`.
- Bump browserslist in /custum_style_src/material-polyfills

Bumps [browserslist](https://github.com/browserslist/browserslist) from 4.16.3 to 4.16.6.
- [Release notes](https://github.com/browserslist/browserslist/releases)
- [Changelog](https://github.com/browserslist/browserslist/blob/main/CHANGELOG.md)
- [Commits](https://github.com/browserslist/browserslist/compare/4.16.3...4.16.6)

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #59 from orzih/dependabot/npm_and_yarn/custum_style_src/material-polyfills/browserslist-4.16.6

Bump browserslist from 4.16.3 to 4.16.6 in /custum_style_src/material-polyfills
- Bump dns-packet in /custum_style_src/material-polyfills

Bumps [dns-packet](https://github.com/mafintosh/dns-packet) from 1.3.1 to 1.3.4.
- [Release notes](https://github.com/mafintosh/dns-packet/releases)
- [Changelog](https://github.com/mafintosh/dns-packet/blob/master/CHANGELOG.md)
- [Commits](https://github.com/mafintosh/dns-packet/compare/v1.3.1...v1.3.4)

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #60 from orzih/dependabot/npm_and_yarn/custum_style_src/material-polyfills/dns-packet-1.3.4

Bump dns-packet from 1.3.1 to 1.3.4 in /custum_style_src/material-polyfills
- Bump dependencies in /custum_style_src/material-polyfills and Changed webpack configs.
- Bump pillow from 8.1.1 to 8.2.0

Bumps [pillow](https://github.com/python-pillow/Pillow) from 8.1.1 to 8.2.0.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/8.1.1...8.2.0)

---
updated-dependencies:
- dependency-name: pillow
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #62 from orzih/dependabot/pip/pillow-8.2.0

Bump pillow from 8.1.1 to 8.2.0
- Exclude pages recursively

Add get_excluded_pages() which will recursively expand user-excluded
paths and return a list of all pages to be excluded. The previous
implementation only looks at the exact paths provided in the
mkdocs.yaml whereas this implementation will work both for excluding
files and directories.

Possible improvement:
get_excluded_pages() is called once per is_excluded() which in turn is
called once per on_post_page(). Since self._options.exclude_pages will
not change between os_post_page() calls, this is inefficient and could
be an issue in very large projects.
Suggestions for how to make get_excluded_pages() only run once per
.pdf-generation are appreciated!

Closes #58
- Merge pull request #63 from ErikThorsell/feat/exclude_recursively

Exclude pages recursively
- Change page exclusion method from directory search to pattern matching #58.
- For Release 0.9.0
- Fixed a bug about `exclude_pages` option. #64
- For Release 0.9.1
- Fixed an issue when running on Python 3.6. #58
- For Release 0.9.2
- Updated README.md
- Bump dependencies in /custum_style_src/material-polyfills.
- Fixed a bug with number-only page titles. #67
- For Release 0.9.3
- Bump pillow from 8.2.0 to 8.3.2

Bumps [pillow](https://github.com/python-pillow/Pillow) from 8.2.0 to 8.3.2.
- [Release notes](https://github.com/python-pillow/Pillow/releases)
- [Changelog](https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst)
- [Commits](https://github.com/python-pillow/Pillow/compare/8.2.0...8.3.2)

---
updated-dependencies:
- dependency-name: pillow
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>
- Merge pull request #77 from orzih/dependabot/pip/pillow-8.3.2

Bump pillow from 8.2.0 to 8.3.2
- Download PDF missing with mkdocs-material 8
- Increase TOC levels to 6
- Switch from warn to info error level

This commit fixes #99
- Fixing wrong path format for Windows
- Indentation of list with mkdocs-material as theme
- Support for Mermaid Diagrams using ReLaXed JS

Add option to use 'ReLaXeD' JS renderer for PDF
instead of Headless Chrome.

option added: use_relaxed_js_renderer

option changed:
 - output_pdf_name: default 'document' as before
 - output_path:     contains now only directory name
                    not a file name

Issue #34
- Modified the options and processing of `ReLaXedJS`.
- Merge pull request #1 from domWalters/pre-release-v0.9.4

Pre Release v0.9.4

<!-- generated by git-cliff -->
