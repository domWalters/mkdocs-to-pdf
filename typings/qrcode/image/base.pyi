from typing import IO

class BaseImage:
    def save(self, stream: IO[bytes], kind: str = ...) -> None: ...
