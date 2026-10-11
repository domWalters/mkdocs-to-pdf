"""Collect the `<script>` elements that a combined page must replay."""

import pathlib
import re
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup, Tag

from .soup_util import get_attribute

# A remote script (`https://...`, `http://...` or protocol-relative `//...`)
# already carries a URL the JavaScript driver can fetch from the temp document.
_REMOTE_SRC = re.compile(r"^(?:https?:)?//")


def _resolve_src(src: str, base_dir: pathlib.Path) -> str | None:
    """
    Resolve a script `src` to a URL loadable from the combined document.

    Remote and already-absolute sources are returned unchanged. Local sources
    are resolved relative to `base_dir` and rewritten to a `file://` URL,
    because the JavaScript driver writes the combined document to a temporary
    directory where the site's relative paths no longer resolve. Sources that
    do not exist are dropped.

    Args:
        src: The script source attribute.
        base_dir: Directory the source is relative to (the page's site dir).

    Returns:
        The resolved URL, or None when the local file is missing.

    """
    if _REMOTE_SRC.match(src):
        return src

    parsed = urllib.parse.urlparse(src)
    if parsed.scheme:
        if parsed.scheme == "file":
            path = pathlib.Path(urllib.request.url2pathname(parsed.path))
            return src if path.is_file() else None
        return src

    candidate = (base_dir / src).resolve()
    if not candidate.is_file():
        return None
    return candidate.as_uri()


def collect_page_scripts(
    soup: BeautifulSoup,
    base_dir: pathlib.Path,
) -> tuple[list[Tag], str]:
    """
    Return a page's body scripts and its concatenated inline JavaScript.

    Local scripts are kept (with their `src` rewritten to a `file://` URL) so
    that theme scripts and configurations such as Material's
    `javascripts/mathjax.js` survive into the combined document. Dropping them
    meant inline MathJax (`$...$`) never rendered in the PDF (#85).

    Args:
        soup: The parsed rendered page.
        base_dir: Directory the page's relative script sources resolve against.

    Returns:
        A ``(scripts, inline)`` tuple, where ``scripts`` are the replayable
        `<script>` tags and ``inline`` is the joined JavaScript of every inline
        body script.

    """
    scripts: list[Tag] = []
    inline: list[str] = []

    for script in soup.select("body > script"):
        if script.has_attr("src"):
            resolved = _resolve_src(get_attribute(script, "src"), base_dir)
            if resolved is None:
                continue
            script["src"] = resolved
            scripts.append(script)
        else:
            text = script.get_text()
            if text:
                inline.append(text)

    return scripts, ";".join(inline)
