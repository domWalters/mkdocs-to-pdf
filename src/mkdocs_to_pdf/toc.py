from bs4 import PageElement, Tag

from .options import Options
from .utils.soup_util import clone_element


def make_indexes(soup: PageElement, options: Options) -> None:
    """ Generate ordered chapter number and TOC of document.

    Arguments:
        soup {BeautifulSoup} -- DOM object of Document.
        options {Options} -- The options of this sequence.
    """

    # Step 1: (re)ordered headings
    _inject_heading_order(soup, options)

    # Step 2: generate toc page
    level = options.toc_level
    if level < 1 or level > 6:
        return

    options.logger.info(
        f'Generate a table of contents up to heading level {level}.')

    def makeLink(h: Tag) -> Tag:
        li = soup.new_tag('li')
        ref = h.get('id', '')
        a = soup.new_tag('a', href=f'#{ref}')
        for el in h.contents:
            if el.name == 'a':
                a.append(el.contents[0])
            else:
                a.append(clone_element(el))
        li.append(a)
        options.logger.debug(f"| [{h.get_text(separator=' ')}]({ref})")
        return li

    toc = soup.new_tag('article', id='doc-toc')
    title = soup.new_tag('h1')
    title.append(soup.new_string(options.toc_title))
    toc.append(title)

    h1ul = soup.new_tag('ul')
    toc.append(h1ul)

    # The currently open `ul`/`li` per heading level (indices 1-6).
    # `ul_parent[n]` remembers which `li` the level-`n` list hangs off, so a
    # new list is only created when its ancestor changes.
    uls: list[Tag | None] = [None] * 7
    lis: list[Tag | None] = [None] * 7
    ul_parent: list[Tag | None] = [None] * 7
    uls[1] = h1ul
    ul_parent[1] = h1ul

    # Level of the closest heading listed in `excludes_children`. Headings
    # deeper than it are omitted until a heading at the same or a shallower
    # level is reached.
    exclude_depth: int | None = None

    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for h in headings:
        depth = int(h.name[1])
        if depth > level:
            continue

        if exclude_depth is not None:
            if depth > exclude_depth:
                continue
            exclude_depth = None

        if depth == 1:
            parent: Tag | None = h1ul
        else:
            parent = next(
                (lis[p] for p in range(depth - 1, 0, -1) if lis[p]), None)
        if parent is None:
            # No shallower heading has been included yet, so there is nothing
            # to nest this heading under. Skipping keeps the TOC well-formed
            # even when heading levels are not used strictly.
            continue

        # A new heading invalidates any open lists at deeper levels.
        for deeper in range(depth + 1, 7):
            uls[deeper] = lis[deeper] = ul_parent[deeper] = None

        target = uls[depth]
        if target is None or ul_parent[depth] is not parent:
            target = soup.new_tag('ul')
            parent.append(target)
            uls[depth] = target
            ul_parent[depth] = parent

        li = makeLink(h)
        target.append(li)
        lis[depth] = li

        if _is_exclude(h.get('id', None), options):
            exclude_depth = depth

    soup.body.insert(0, toc)


def _inject_heading_order(soup: Tag, options: Options) -> None:

    level = options.ordered_chapter_level
    if level < 1 or level > 6:
        return

    options.logger.info(f'Number headings up to level {level}.')

    counts = [0] * 7
    exclude_depth: int | None = None

    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for h in headings:
        depth = int(h.name[1])
        if depth > level:
            continue

        if exclude_depth is not None:
            if depth > exclude_depth:
                continue
            exclude_depth = None

        counts[depth] += 1
        for deeper in range(depth + 1, 7):
            counts[deeper] = 0

        number = '.'.join(str(counts[n]) for n in range(1, depth + 1))
        prefix = f'{number}. ' if depth == 1 else f'{number} '

        options.logger.debug(
            f"| [{prefix} {h.text}]({h.get('id', '(none)')})")

        nm_tag = soup.new_tag('span', **{'class': 'pdf-order'})
        nm_tag.append(prefix)
        h.insert(0, nm_tag)

        if _is_exclude(h.get('id', None), options):
            exclude_depth = depth


def _is_exclude(url: str, options: Options) -> bool:
    if not url:
        return False

    if url in options.excludes_children:
        options.logger.info(f"|  (exclude '{url}')")
        return True

    return False
