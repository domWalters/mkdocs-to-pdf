"""Resolve stable paths for navigation sections."""

from base64 import b32encode
from uuid import uuid4
from weakref import WeakKeyDictionary

from mkdocs.structure.nav import Section

_slug_cache: WeakKeyDictionary[Section, str] = WeakKeyDictionary()


def get_section_path(section: Section) -> str:
    """
    Return the slash-terminated path for a navigation section.

    Args:
        section: The section.

    Returns:
        The section path.

    Raises:
        TypeError: If the given item is not a section.

    """
    if not section.is_section:
        msg = "not a section"
        raise TypeError(msg)

    slugs = [
        _section_slug(sec) for sec in section.ancestors if isinstance(sec, Section)
    ]
    slugs.reverse()
    slugs.append(_section_slug(section))

    return "/".join(slugs) + "/"


def _section_slug(section: Section) -> str:
    if not section.is_section:
        msg = "not a section"
        raise TypeError(msg)

    cached = _slug_cache.get(section)
    if cached is not None:
        return cached

    title = section.title.strip()
    title = title or str(uuid4())
    slug = b32encode(title.encode("utf-8")).rstrip(b"=").decode()
    _slug_cache[section] = slug

    return slug
