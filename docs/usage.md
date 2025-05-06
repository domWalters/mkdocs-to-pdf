# Usage

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

The author of the document. Used in the header / footer.

Defaults to the `site_author`.

``` yaml
plugins:
  - to-pdf:
      author: John Smith
```

#### `copyright`

The copyright statement for the document. Used in the header / footer.

Defaults to the top level `copyright`.

``` yaml
plugins:
  - to-pdf:
      copyright: Copyright © John Smith 2025
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

Defaults to `3`.

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

