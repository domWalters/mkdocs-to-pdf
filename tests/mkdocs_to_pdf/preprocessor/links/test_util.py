from mkdocs_to_pdf.preprocessor.links.util import is_absolute_url
from mkdocs_to_pdf.preprocessor.links.util import iri_to_uri


def test_is_absolute_url():
    assert is_absolute_url('http://localhost:8000')
    assert is_absolute_url('https://github.com/domWalters/mkdocs-to-pdf')
    assert not is_absolute_url('site/pdf/document.pdf')
    assert not is_absolute_url('/home/username/site/pdf/document.pdf')
    assert not is_absolute_url('file:///path/to/document')


def test_iri_to_uri():
    assert (
        iri_to_uri('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        == '/Applications/Google%20Chrome.app/Contents/MacOS/Google%20Chrome'
    )
    assert (
        iri_to_uri('file:///home/username/myproject/site/テスト')
        == 'file:///home/username/myproject/site/%E3%83%86%E3%82%B9%E3%83%88'
    )
    assert (
        iri_to_uri('file:///home/username/作業/プロジェクト/site/テスト')
        == 'file:///home/username/%E4%BD%9C%E6%A5%AD/%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88/site/%E3%83%86%E3%82%B9%E3%83%88'
    )
    assert (
        iri_to_uri('https://ja.wikipedia.org/wiki/電子文書')
        == 'https://ja.wikipedia.org/wiki/%E9%9B%BB%E5%AD%90%E6%96%87%E6%9B%B8'
    )
