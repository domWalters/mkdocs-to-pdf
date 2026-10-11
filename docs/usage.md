# Usage

!!! warning "Theme support"

    `mkdocs-to-pdf` is primarily intended for use with the
    [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/) theme.
    Other themes can be used, but they are not officially supported and are
    used at your own risk.

## Initial Plugin

Enable the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - to-pdf
```

For more information on plugins within `mkdocs`, see the
[official `mkdocs` documentation][mkdocs-plugins].

[mkdocs-plugins]: http://www.mkdocs.org/user-guide/plugins

When building your repository with `mkdocs build`, you will now see the
following message at the end of your build output:

> Converting 10 articles to PDF took 7.1 s

## Options

### Headers and Footers

#### `author`

The author of the document. Used in the header / footer, and written to the
`Author` field of the PDF metadata.

Defaults to the `site_author`.

``` yaml
plugins:
  - to-pdf:
      author: John Smith
```

#### `copyright`

The copyright statement for the document. Used in the header / footer.

The value is parsed as HTML on the cover page. Any tags are stripped from the
plain-text page footer.

Defaults to the top level `copyright`.

``` yaml
plugins:
  - to-pdf:
      copyright: Copyright © <a href="https://example.com">John Smith</a> 2025
```

### Metadata

The plugin writes the `Author`, `Subject`, `Keywords`, `Creator`,
`CreationDate` and `ModDate` fields of the PDF metadata. `Author` comes from
[`author`](#author); the rest are configured under `metadata`. The `Producer`
is prefixed with `mkdocs-to-pdf <version>, `.

#### `metadata.description`

The summary of the document, written to the PDF `Subject`.

Defaults to the top level `site_description`. When neither is set, the
`Subject` is left empty.

#### `metadata.keywords`

A comma-separated list of keywords, written to the PDF `Keywords`.

By default no keywords are set.

``` yaml
plugins:
  - to-pdf:
      metadata:
        description: A complete reference for the plugin
        keywords: mkdocs, pdf, documentation
```

### Cover

#### `cover`

Covers generate by default.

Set `cover` to false if you don't want a cover to generate.

``` yaml
plugins:
  - to-pdf:
      cover: false
```

#### `cover_title`

The title on the cover page.

Defaults to the `site_name`.

``` yaml
plugins:
  - to-pdf:
      cover_title: Title for the Cover Page
```

#### `cover_subtitle`

The subtitle on the cover page.

By default there is no subtitle.

``` yaml
plugins:
  - to-pdf:
      cover_subtitle: Subtitle for the Cover Page
```

#### `cover_logo`

The logo to use on the cover page. URL or relative path to `docs`.

By default these is no logo.

``` yaml
plugins:
  - to-pdf:
      cover_logo: https://commons.wikimedia.org/wiki/File:Octicons-mark-github.svg
```

#### `back_cover`

Back covers don't generate by default.

Set to true if you want a back cover to generate.

``` yaml
plugins:
  - to-pdf:
      back_cover: true
```

#### `back_cover_qrcode`

Whether to add a QR code to the back cover. Off by default.

``` yaml
plugins:
  - to-pdf:
      back_cover: true
      back_cover_qrcode: true
```

#### `back_cover_qr_url`

The URL encoded in the back cover QR code. When empty, the `site_url` (or
`repo_url`) is used.

``` yaml
plugins:
  - to-pdf:
      back_cover: true
      back_cover_qrcode: true
      back_cover_qr_url: https://example.com
```

#### `back_cover_barcode`

Whether to add a barcode to the back cover. Off by default.

``` yaml
plugins:
  - to-pdf:
      back_cover: true
      back_cover_barcode: true
      back_cover_barcode_value: "123456789012"
      back_cover_barcode_kind: code128
```

#### `back_cover_barcode_value`

The value encoded in the back cover barcode. No barcode is drawn when empty.

#### `back_cover_barcode_kind`

The barcode type, a `python-barcode` kind (for example `code39`, `code128`,
`ean13`). Defaults to `code128`.

### Customizing the PDF

The recommended way to change how the generated PDF looks — fonts, colours,
heading sizes, underlines, and the page headers and footers — is a custom
`styles.scss` file. It is compiled with [Sass][sass] and appended to the
built-in styles, so you can use variables, nesting and `@import`, and your
rules override the defaults.

By default the plugin loads `styles.scss` from a `templates` directory at the
root of your project, so creating `templates/styles.scss` is enough:

``` scss
// templates/styles.scss

// The defaults use grey headings and red underlines; plain black suits paper.
article h1,
article h2,
article h3 {
  color: #000 !important;
  border-bottom-color: #a9a9a9 !important;
}
```

To keep the file elsewhere, point
[`custom_template_path`](#custom_template_path) at its directory.

[sass]: https://sass-lang.com/

#### `custom_template_path`

A directory containing the custom `styles.scss` and optional custom cover
templates. Defaults to `templates`.

It may contain any of:

- `styles.scss`: print styles, compiled and appended *after* the built-in
  styles, so your rules win. Use `!important` to override theme rules that
  have higher specificity.
- `cover.html.j2` and/or `back_cover.html.j2`: custom cover templates.

``` yaml
plugins:
  - to-pdf:
      custom_template_path: docs/assets/stylesheets
```

This is the path to the **directory**, not to `styles.scss` itself.

To see the styles you can override, browse the installed package's
`mkdocs_to_pdf/styles/*.scss` and `mkdocs_to_pdf/themes/*.scss`.

!!! note
    A relative `custom_template_path` is resolved against the *working
    directory*, not the directory containing `mkdocs.yml`. Use an absolute
    path, or run `mkdocs` from the directory containing your config (for
    example, `mkdocs build -f path/to/mkdocs.yml` resolves relative paths
    differently than running it from that directory).

#### Common style changes

Change the heading colours and underlines:

``` scss
article {
  h1 {
    border-bottom: 2px solid #0000ff !important;
  }

  h2 {
    border-bottom: 1px solid #000099 !important;
  }
}
```

Make `h4`–`h6` the same size and weight as the body text:

``` scss
article h4,
article h5,
article h6 {
  color: #000 !important;
  font-size: 1em !important;
  font-weight: normal !important;
}
```

Stop inline code shrinking below the body font size:

``` scss
pre,
code,
var,
samp,
kbd,
tt {
  font-size: 1em;
}
```

Recolour the page header and footer with the CSS `@page` rule:

``` scss
@page {
  color: #000;
}
```

### Template filters

Custom cover templates can use these Jinja2 filters:

- `qrcode(value, ...)`: encode `value` as an SVG QR code data URI.
- `barcode(value, kind, ...)`: encode `value` as an SVG barcode data URI,
  where `kind` is a `python-barcode` type (for example `code39`, `code128`,
  `ean13`).

For example, in a custom `back_cover.html.j2`:

``` html
<img src="{{ 'https://example.com' | qrcode }}"/>
<img src="{{ '1234567890' | barcode('code39') }}"/>
```

### Headings and Table of Contents

#### `toc_title`

The title for the Table of Contents.

Defaults to `"Table of Contents"`.

``` yaml
plugins:
  - to-pdf:
      toc_title: "Table of Contents"
```

#### `toc_level`

The depth of headings to show in the Table of Contents. 1 to 6.

Defaults to `2`.

``` yaml
plugins:
  - to-pdf:
      toc_level: 2
```

#### `ordered_chapter_level`

The depth of headings to provide numbers to. Headings deeper than this number
will not receive a section number.

Defaults to `3`.

``` yaml
plugins:
  - to-pdf:
      ordered_chapter_level: 2
```

#### `heading_shift`

Heading shifts are enabled by default. Set to false to disable heading shifting.

When false, all headings will use the same font and size, no matter how deep
they are.

``` yaml
plugins:
  - to-pdf:
      heading_shift: false
```

### Output

#### `output_path`

The path to write the PDF to. The root of this path is the `site` directory.

Default is `"pdf/document.pdf"`.

``` yaml
plugins:
  - to-pdf:
      output_path: document.pdf
```

#### `html_path`

If set, output HTML to a file, which can be used for Epub conversion.
The root of this path is the `site` directory.

Default is `""`.

``` yaml
plugins:
  - to-pdf:
      html_path: single.html
```

#### `enabled_if_env`

PDFs will only be build if the environment variable referenced here is set to
"1".

``` yaml
plugins:
  - to-pdf:
      enabled_if_env: ENABLE_PDF_EXPORT
```

Then `mkdocs serve` won't build them anymore:

```console
$ mkdocs serve
INFO    -  Browser Connected: http://127.0.0.1:8000/
INFO    -  Running task: builder (delay: None)
INFO    -  Building documentation...
WARNING -  without generate PDF(set environment variable ENABLE_PDF_EXPORT to 1 to enable)
... 2 seconds later ...
INFO    -  Reload 1 waiters: /.../index.md
```

And `mkdocs build` can be called with the appropriate environment variable:

```console
$ ENABLE_PDF_EXPORT=1 mkdocs build
...
INFO    -  Converting 10 articles to PDF took 7.1s
INFO    -  Documentation built in 8.29 seconds
```

### Debug

#### `verbose`

Set to true to see all WeasyPrint debug messages during build.

``` yaml
plugins:
  - to-pdf:
      verbose: true
```

#### `debug_html`

Set to true to output HTML to `stdout` during build

``` yaml
plugins:
  - to-pdf:
      debug_html: true
```
