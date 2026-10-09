from . import constants as constants
from . import image as image
from .image.base import BaseImage

class QRCode:
    def __init__(
        self,
        *,
        version: int | None = ...,
        error_correction: int = ...,
        box_size: int = ...,
        border: int = ...,
        image_factory: type[BaseImage] | None = ...,
        mask_pattern: int | None = ...,
    ) -> None: ...
    def add_data(self, data: str, optimize: int = ...) -> None: ...
    def make_image(self) -> BaseImage: ...
