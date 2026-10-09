"""Normalize hrefs and ids for the combined document."""

import os
import pathlib
import re
from urllib.parse import quote, urljoin, urlparse


def transform_href(href: str, rel_url: str) -> str:
    """
    Transform an href for the single combined document.

    Normalizes the href to ``#foo/bar/section:id``.

    Args:
        href: A linked URL string in the document.
        rel_url: The current page URL (like a base URL).

    Returns:
        The transformed URL string.

    """

    def transform() -> str:
        target_url = urlparse(href)

        if target_url.scheme or target_url.netloc:
            # do not care, will be not reachable
            return href

        fragment = target_url.fragment
        target = urljoin(rel_url, target_url.path)

        if target in {"/", ".", "index.html"}:
            return f"#.:{fragment}"

        if target.endswith(".png"):
            return href
        if target.endswith("index.html"):
            target = re.sub(r"index\.html$", "", target)
        else:
            target = re.sub(r"\.(html|md)$", "/", target)

        if not target.endswith("/"):
            target += "/"

        return f"#{quote(target)}:{fragment}"

    return transform()


def transform_id(element_id: str, rel_url: str) -> str:
    """
    Normalize an id to ``foo/bar/section:id``.

    Args:
        element_id: The element id.
        rel_url: The current page URL.

    Returns:
        The normalized id.

    """
    if rel_url in {".", "index.html"}:
        return f".:{element_id}"

    head, tail = os.path.split(rel_url)
    section = pathlib.PurePosixPath(tail).stem

    def normalize(path: str) -> str:
        if len(path) == 0 or path == "index":
            return ""
        return path + "/"

    head = normalize(head)
    section = normalize(section)

    return f"{head}{section}:{element_id}"
