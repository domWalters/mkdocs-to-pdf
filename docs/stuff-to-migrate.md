---
search:
  exclude: true
---

You may customize the plugin by passing options in `mkdocs.yml`:

```yaml
plugins:
    - to-pdf:
        #custom_template_path: TEMPLATES PATH
        #
        #excludes_children:
        #    - 'release-notes/:upgrading'
        #    - 'release-notes/:changelog'
        #
        #exclude_pages:
        #    - 'bugs/'
        #    - 'appendix/contribute/'
        #convert_iframe:
        #    - src: IFRAME SRC
        #      img: POSTER IMAGE URL
        #      text: ALTERNATE TEXT
        #    - src: ...
        #two_columns_level: 3
        #
        #render_js: true
        #headless_chrome_path: headless-chromium
        #
        #show_anchors: true
```

#### Options

##### for Heading and TOC

* `excludes_children`

    Set the page `id` of `nav` url. If the `id` matches in this list, it will be excluded from the heading number addition and table of contents.  
    **default**: `[]`

##### for Page

* `exclude_pages`

    Set the page `id` of `nav` url. If the `id` matches in this list, it will be excluded page contents.  
    **default**: `[]`  
    _**since**: `v0.3.0`_

* `convert_iframe`

    List of `iframe` to `a` conversions. Every `iframe` that matches a `src` in this list will be replace to `a` contains each `img` and/or `text`. it's using for such as embedded VIDEO.  
    **default**: `[]`  
    _**since**: `v0.6.0`_

    @see [Sample of _MkDocs Material_](https://github.com/domWalters/mkdocs-to-pdf/blob/master/samples/mkdocs-material/)

* `two_columns_level` (Experimental)

    Set the heading level of **_Two Column Layout_**. Currently only `0`(disable) or `3` is valid for this value. So slow processing, but a little nice.  

    **default**: `0`  
    _**since**: `v0.7.0`_

    @see [Sample of _MkDocs Material_](https://github.com/domWalters/mkdocs-to-pdf/blob/master/samples/mkdocs-material/)

##### Renderer for JavaScript

* `render_js`

    Set the value to `true` if you're using '[MathJax](https://www.mathjax.org/)', '[Twemoji](https://twemoji.twitter.com/)' or any more.  
    Require "Chrome" which has "headless" mode.  

    **default**: `false`  
    _**since**: `v0.7.0`_

* `headless_chrome_path`

    Set the "Headless Chrome" program path.  
    If `render_js` is _`false`_, this value will be ignored.  

    **default**: `chromium-browser`

> Check on your system:
>
> ```
> $ <PROGRAM_PATH> --headless \
>    --disable-gpu \
>    --dump-dom \
>    <ANY_SITE_URL(eg. 'https://google.com')>
> ```

* `relaxedjs_path`

    Set the value to execute command of relaxed if you're using e.g. '[Mermaid](https://mermaid-js.github.io) diagrams and Headless Chrome is not working for you.
    Require "ReLaXed" Javascript PDF renderer to be installed on your system. See: '[ReLaXed](https://github.com/RelaxedJS/ReLaXed)'.

    Please use 'theme_handler_path' option to specify custom JS sources and CSS Stylesheets which covers your needs. E.g. for Material
    theme it would be **material.py**. See: **mkdocs-to-pdf/src/mkdocs_to_pdf/themes/material.py** for implementation details.
    **default**: `None`
    _**since**: `v0.7.0`_

> Install on your system:
> ```
> $ npm i -g relaxedjs
> $ relaxed --version
> ```

##### ... and more

* `custom_template_path`

    The path where your custom `cover.html` and/or `styles.scss` are located.
    **default**: `templates`  
    _**since**: `v0.8.0`_

* `show_anchors`

    Setting this to `true` will list out of anchor points provided during the build as info message.  
    **default**: `false`  
    _**since**: `v0.7.4`_

## Custom cover page and document style

It is possible to create a custom cover page for the document.
You can also add a custom style sheet to modify the whole document.

To do so, add a `templates` folder at the root level of your `mkdocs` project and place a `cover.html` and/or a `styles.scss` inside.
Alternatively, you can specify a different location with the `custom_template_path` option.

### Custom cover page

Using [jinja2](https://jinja.palletsprojects.com/en/2.11.x/templates/) syntax, you can access all data from your `mkdocs.yml`.
To make template creation easier, you can use `plugin_some_plugin` to access variables from plugins.
E.g. use `{{ author }}` to get the author from your `mkdocs.yml` that looks like:

```yaml
plugins:
    - to-pdf:
        author: WHO
```

You can use custom variables [`extra:` in your `mkdocs.yml`](https://www.mkdocs.org/user-guide/configuration/#extra)
And, you can check it in the log if run with `verbose` or `debug_html` options.

### Custom stylesheet

Since your stylesheet is appended to the default ones, you can override every setting from them.

Tip: setting the `debug_html` option to `true` to get the generated html that is passed to `weasyprint` can help you determine the html tags, classes or identifiers you want to modify in your stylesheet.

## Contributing

From reporting a bug to submitting a pull request: every contribution is appreciated and welcome. Report bugs, ask questions and request features using [Github issues][github-issues].
If you want to contribute to the code of this project, please read the [Contribution Guidelines][contributing].

[mkdocs-material]: https://github.com/squidfunk/mkdocs-material

[contributing]: https://github.com/domWalters/mkdocs-to-pdf/blob/master/CONTRIBUTING.md
[github-issues]: https://github.com/domWalters/mkdocs-to-pdf/issues
