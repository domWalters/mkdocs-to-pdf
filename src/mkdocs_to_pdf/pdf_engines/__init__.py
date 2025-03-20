from ..options import Options
from .base import PDFEngine


def get_pdf_engine(options: Options) -> 'PDFEngine':
    """Get PDF engine."""
    engine = options.pdf_engine
    if engine == 'weasyprint':
        from .weasyprint import WeasyPrint
        engine = WeasyPrint(options)
    elif engine == 'chromium':
        from .chromium import Chromium
        engine = Chromium(options)
    else:
        raise ValueError(f'PDF engine {engine} is not supported.')
    return engine
