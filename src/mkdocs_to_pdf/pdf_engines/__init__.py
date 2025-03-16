from .base import PDFEngine
from .weasyprint import WeasyPrint
from .chromium import Chromium


def get_pdf_engine(engine: str) -> 'PDFEngine':
    """Get PDF engine."""
    if engine == 'weasyprint':
        engine = WeasyPrint()
    elif engine == 'chromium':
        engine = Chromium()
    else:
        raise ValueError(f'PDF engine {engine} is not supported.')
    return engine
