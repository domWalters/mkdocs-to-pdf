from abc import ABCMeta, abstractmethod


class PDFEngine(metaclass=ABCMeta):
    """Base class for PDF engine."""
    @abstractmethod
    def write_pdf(self, html_file: str, output_path: str):
        """Write PDF file from HTML file."""
        pass

    @abstractmethod
    def get_logger(self):
        """Get logger."""
        pass
