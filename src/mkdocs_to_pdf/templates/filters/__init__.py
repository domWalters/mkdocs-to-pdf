"""Base class for Jinja2 template filters."""

from typing import TYPE_CHECKING

from mkdocs.config.base import Config

if TYPE_CHECKING:
    from mkdocs_to_pdf.options import Options


class _FilterBase:  # ruff: ignore[non-empty-init-module]
    """Shared options/config access for template filters."""

    def __init__(self, options: "Options", config: Config) -> None:
        """
        Store the plugin options and MkDocs config.

        Args:
            options: The plugin options.
            config: The MkDocs config.

        """
        self.__options = options
        self.__config = config

    @property
    def options(self) -> "Options":
        """The plugin options."""
        return self.__options

    @property
    def config(self) -> Config:
        """The MkDocs config."""
        return self.__config
