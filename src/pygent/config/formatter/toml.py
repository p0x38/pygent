"""TOML configuration formatter."""

from __future__ import annotations

from typing import Any

from .base import ConfigFormatter


class TomlFormatter(ConfigFormatter):
    """Format Pygent configuration as TOML."""

    def format(self, config: Any) -> str:
        """Format configuration as TOML."""
        raise NotImplementedError("TOML formatting is not implemented yet")
