"""Localized configuration display labels."""

from __future__ import annotations

from pygent.i18n import Translator


class ConfigLabels:
    """Provide localized labels for configuration display."""

    def __init__(self, translator: Translator) -> None:
        self._translator = translator

    @property
    def translator(self) -> Translator:
        """Return the underlying translator."""
        return self._translator

    def section(self, name: str) -> str:
        """Translate a configuration section name."""
        return self._translator(
            f"config.section.{name}",
            default=name,
        )

    def field(self, name: str) -> str:
        """Translate a configuration field name."""
        return self._translator(
            f"config.field.{name}",
            default=name,
        )

    def value(self, name: str) -> str:
        """Translate a configuration value."""
        return self._translator(
            f"config.value.{name}",
            default=name,
        )

    def source(self, name: str) -> str:
        """Translate a configuration source name."""
        return self._translator(
            f"config.source.{name}",
            default=name,
        )

    def unit(self, name: str) -> str:
        """Translate a configuration unit name."""
        return self._translator(
            f"config.unit.{name}",
            default=name,
        )
