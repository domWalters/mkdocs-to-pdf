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

### Advanced Rendering Hooks (Experimental)

You can hook the PDF rendering process by creating a `pdf_event_hook.py`(or `pdf_event_hook/__init__.py`) in your working directory _(usually the same directory as` mkdocs.yml`)_.  
_**since**: `v0.8.2`_

#### Sample `pdf_event_hook.py` (or `pdf_event_hook/__init__.py`)

```python
import logging

from bs4 import BeautifulSoup
from mkdocs.structure.pages import Page


def inject_link(html: str, href: str,
                page: Page, logger: logging) -> str:
    """Adding PDF View button on navigation bar(using material theme)"""

    def _pdf_icon():
        _ICON = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<path d="M128,0c-17.6,0-32,14.4-32,32v448c0,17.6,14.4,32,32,32h320c17.6,0,32-14.4,32-32V128L352,0H128z" fill="#E2E5E7"/>
<path d="m384 128h96l-128-128v96c0 17.6 14.4 32 32 32z" fill="#B0B7BD"/>
<polygon points="480 224 384 128 480 128" fill="#CAD1D8"/>
<path d="M416,416c0,8.8-7.2,16-16,16H48c-8.8,0-16-7.2-16-16V256c0-8.8,7.2-16,16-16h352c8.8,0,16,7.2,16,16  V416z" fill="#F15642"/>
<g fill="#fff">
<path d="m101.74 303.15c0-4.224 3.328-8.832 8.688-8.832h29.552c16.64 0 31.616 11.136 31.616 32.48 0 20.224-14.976 31.488-31.616 31.488h-21.36v16.896c0 5.632-3.584 8.816-8.192 8.816-4.224 0-8.688-3.184-8.688-8.816v-72.032zm16.88 7.28v31.872h21.36c8.576 0 15.36-7.568 15.36-15.504 0-8.944-6.784-16.368-15.36-16.368h-21.36z"/>
<path d="m196.66 384c-4.224 0-8.832-2.304-8.832-7.92v-72.672c0-4.592 4.608-7.936 8.832-7.936h29.296c58.464 0 57.184 88.528 1.152 88.528h-30.448zm8.064-72.912v57.312h21.232c34.544 0 36.08-57.312 0-57.312h-21.232z"/>
<path d="m303.87 312.11v20.336h32.624c4.608 0 9.216 4.608 9.216 9.072 0 4.224-4.608 7.68-9.216 7.68h-32.624v26.864c0 4.48-3.184 7.92-7.664 7.92-5.632 0-9.072-3.44-9.072-7.92v-72.672c0-4.592 3.456-7.936 9.072-7.936h44.912c5.632 0 8.96 3.344 8.96 7.936 0 4.096-3.328 8.704-8.96 8.704h-37.248v0.016z"/>
</g>
<path d="m400 432h-304v16h304c8.8 0 16-7.2 16-16v-16c0 8.8-7.2 16-16 16z" fill="#CAD1D8"/>
</svg>
'''  # noqa: E501
        return BeautifulSoup(_ICON, 'html.parser')

    logger.info(f'(hook on inject_link: {page.title})')
    soup = BeautifulSoup(html, 'html.parser')

    nav = soup.find(class_='md-header-nav')
    if not nav:
        # after 7.x
        nav = soup.find('nav', class_='md-header__inner')
    if nav:
        a = soup.new_tag('a', href=href, title='PDF',
                         **{'class': 'md-header__button md-header-nav__button md-icon'})
        a.append(_pdf_icon())
        nav.append(a)
        return str(soup)

    return html


# def pre_js_render(soup: BeautifulSoup, logger: logging) -> BeautifulSoup:
#     logger.info('(hook on pre_js_render)')
#     return soup


# def pre_pdf_render(soup: BeautifulSoup, logger: logging) -> BeautifulSoup:
#     logger.info('(hook on pre_pdf_render)')
#     tag = soup.find(lambda tag: tag.name ==
#                     'body' and 'data-md-color-scheme' in tag.attrs)
#     if tag:
#         tag['data-md-color-scheme'] = 'print'
#     return soup
```

... and check log:

```sh
$ mkdocs build
INFO    -  Found PDF rendering event hook module.
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /tmp/sample/site
INFO    -  (hook on inject_link: Home)
   ...
```

## Contributing

From reporting a bug to submitting a pull request: every contribution is appreciated and welcome. Report bugs, ask questions and request features using [Github issues][github-issues].
If you want to contribute to the code of this project, please read the [Contribution Guidelines][contributing].

[mkdocs-material]: https://github.com/squidfunk/mkdocs-material

[contributing]: https://github.com/domWalters/mkdocs-to-pdf/blob/master/CONTRIBUTING.md
[github-issues]: https://github.com/domWalters/mkdocs-to-pdf/issues
