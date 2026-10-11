"""URL Jinja2 filter."""

import pathlib
import sys
from urllib.parse import urlparse

from . import _FilterBase


class URLFilter(_FilterBase):
    """Find a matching filename in some directories and return its URL."""

    def __call__(self, pathname: str) -> str:
        """
        Resolve a pathname to a URL, searching known directories.

        Args:
            pathname: The pathname to resolve.

        Returns:
            The resolved URL, or the pathname unchanged if not found.

        """
        if not pathname:
            return ""

        # Check for URL(eg. 'https://...')
        target_url = urlparse(pathname)
        if target_url.scheme or target_url.netloc:
            return pathname

        # Search image file in below directories:
        dirs = [
            self.options.custom_template_path,
            self.config["theme"].custom_dir,
            self.config["docs_dir"],
            ".",
        ]

        for d in dirs:
            if not d:
                continue
            path = (pathlib.Path(d) / pathname).resolve()
            if path.is_file():
                if sys.platform == "win32":
                    return "file:///" + path.as_posix()
                return "file://" + str(path)

        # not found?
        return pathname
