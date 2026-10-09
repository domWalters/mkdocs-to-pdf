from collections.abc import Mapping
from typing import IO

class Barcode:
    def __init__(
        self,
        code: str,
        writer: object | None = ...,
        **options: object,
    ) -> None: ...
    def write(
        self,
        fp: IO[bytes],
        options: Mapping[str, object] | None = ...,
    ) -> None: ...

def get_barcode_class(name: str) -> type[Barcode]: ...
