from collections.abc import Callable
from typing import Any, TypeAlias

from bs4 import BeautifulSoup

OptionsStub: TypeAlias = Any
OptionsFactory: TypeAlias = Callable[..., OptionsStub]
SoupFactory: TypeAlias = Callable[..., BeautifulSoup]
