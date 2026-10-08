import logging
from types import SimpleNamespace
from typing import Never

import pytest
from _types import OptionsFactory, SoupFactory

from mkdocs_to_pdf.cover import make_cover


class FakeTemplate:
    """Minimal stand-in for `mkdocs_to_pdf.templates.Template`."""

    def __init__(
        self,
        renders: dict[str, object],
        keywords: dict[str, object] | None = None,
    ) -> None:
        """Store the render sources keyed by template name."""
        self.keywords = keywords or {}
        self._renders = renders

    def select(self, names: list[str]) -> SimpleNamespace:
        """Return the first matching render source as a template-like object."""
        for name in names:
            if name in self._renders:
                value = self._renders[name]
                render = value if callable(value) else (lambda _kw, v=value: v)
                return SimpleNamespace(name=name, render=render)
        msg = f"no template for {names}"
        raise AssertionError(msg)


def test_make_cover_inserts_at_top(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Insert the cover article before all other content."""
    options = make_options(
        cover=True,
        back_cover=False,
        template=FakeTemplate(
            {"cover": '<article id="doc-cover"><h1>Cover</h1></article>'},
        ),
    )
    soup = make_soup("<article id='doc-content'>body</article>")

    make_cover(soup, options)

    cover = soup.find("article", id="doc-cover")
    assert cover is not None
    body = soup.body
    assert body is not None
    assert body.contents[0] is cover
    assert soup.find("article", id="doc-back_cover") is None


def test_make_cover_appends_back_cover(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Append the back cover article after all other content."""
    options = make_options(
        cover=True,
        back_cover=True,
        template=FakeTemplate(
            {
                "cover": '<article id="doc-cover">c</article>',
                "back_cover": '<article id="doc-back_cover">b</article>',
            },
        ),
    )
    soup = make_soup("<article id='doc-content'>body</article>")

    make_cover(soup, options)

    assert soup.find("article", id="doc-cover") is not None
    back = soup.find("article", id="doc-back_cover")
    assert back is not None
    body = soup.body
    assert body is not None
    assert body.contents[-1] is back


def test_make_cover_disabled(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Emit no cover or back cover when both are disabled."""
    options = make_options(
        cover=False,
        back_cover=False,
        template=FakeTemplate({"cover": '<article id="doc-cover"/>'}),
    )
    soup = make_soup("<article id='doc-content'>body</article>")

    make_cover(soup, options)

    assert soup.find("article", id="doc-cover") is None
    assert soup.find("article", id="doc-back_cover") is None


def test_make_cover_swallows_render_errors(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log and continue when a cover template fails to render."""
    options = make_options(
        cover=True,
        back_cover=False,
        template=FakeTemplate({"cover": _boom}),
    )
    soup = make_soup("<article id='doc-content'>body</article>")

    with caplog.at_level(logging.ERROR, logger="mkdocs_to_pdf.test"):
        make_cover(soup, options)

    assert soup.find("article", id="doc-cover") is None
    assert "Failed to generate the cover page" in caplog.text


def _boom(_kw: object) -> Never:
    """Raise unconditionally, simulating a template render failure."""
    msg = "kaboom"
    raise RuntimeError(msg)
