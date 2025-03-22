from abc import ABCMeta, abstractmethod

from ..options import Options


class PDFEngine(Options, metaclass=ABCMeta):
    """Base class for PDF engine."""

    @abstractmethod
    def __init__(self, options: Options):
        """Initialize PDF engine."""
        pass

    @abstractmethod
    def write_pdf(self, html_file: str, output_path: str):
        """Write PDF file from HTML file."""
        pass

    @abstractmethod
    def get_logger(self):
        """Get logger."""
        pass
