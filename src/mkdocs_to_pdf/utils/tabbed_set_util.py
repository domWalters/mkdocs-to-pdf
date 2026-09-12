import itertools
from logging import Logger

from bs4 import PageElement, Tag


def wrap_tabbed_set_content(soup: PageElement, logger: Logger = None):
    for ts in list(soup.select('div.tabbed-set')):
        labels_div = ts.find('div', class_='tabbed-labels')
        content_div = ts.find('div', class_='tabbed-content')

        # Modern pymdownx.tabbed format (tabbed-labels + tabbed-content)
        if labels_div and content_div:
            labels = [el for el in labels_div.children if isinstance(el, Tag) and el.name == 'label']
            blocks = [el for el in content_div.children if isinstance(el, Tag) and 'tabbed-block' in el.get('class', [])]
            if not blocks:
                blocks = [el for el in content_div.children if isinstance(el, Tag)]

            new_wrappers = []
            for label, block in itertools.zip_longest(labels, blocks):
                wrapper = soup.new_tag('div', **{'class': 'tabbed-content--wrap'})
                if label:
                    heading = soup.new_tag('p', **{'class': 'tabbed-label'})
                    heading.extend(list(label.contents))
                    wrapper.append(heading)
                if block:
                    block_div = soup.new_tag('div', **{'class': 'tabbed-content'})
                    block_div.extend(list(block.contents))
                    wrapper.append(block_div)
                new_wrappers.append(wrapper)

            ts.clear()
            for w in new_wrappers:
                ts.append(w)

        else:
            # Legacy pymdownx structure: alternating inputs/labels/contents
            inputs = ts.select('input')
            if inputs:
                for radio in inputs:
                    els = [i for i in itertools.takewhile(
                        lambda x: getattr(x, 'name', None) not in ['input'],
                        radio.next_siblings)]
                    wrapper = soup.new_tag('div', **{'class': 'tabbed-content--wrap'})
                    radio.wrap(wrapper)
                    for tag in els:
                        wrapper.append(tag)

    for d in soup.select('details'):
        d['open'] = ''

