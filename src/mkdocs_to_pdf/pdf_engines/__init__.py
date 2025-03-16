from .base import PDFEngine


def get_pdf_engine(engine: str) -> 'PDFEngine':
    """Get PDF engine."""
    if engine == 'weasyprint':
        from .weasyprint import WeasyPrint
        engine = WeasyPrint()
    elif engine == 'chromium':
        from .chromium import Chromium
        engine = Chromium()
    else:
        raise ValueError(f'PDF engine {engine} is not supported.')
    return engine
