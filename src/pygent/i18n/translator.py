"""Translation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from .catalog import load_catalog


class Translator:
    """Translate message keys using a catalog."""

    def __init__(
        self,
        translations: Mapping[str, str],
        *,
        fallback: Translator | None = None,
    ) -> None:
        self._translations = dict(translations)
        self._fallback = fallback

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        *,
        fallback: Translator | None = None,
    ) -> Translator:
        """Create a translator from a TOML catalog."""
        return cls(
            load_catalog(path),
            fallback=fallback,
        )

    def get(
        self,
        key: str,
        *,
        default: str | None = None,
    ) -> str:
        """Return a translated message."""
        if key in self._translations:
            return self._translations[key]

        if self._fallback is not None:
            return self._fallback.get(key, default=default)

        return key if default is None else default

    def translate(
        self,
        key: str,
        *,
        default: str | None = None,
        **parameters: object,
    ) -> str:
        """Translate and format a message."""
        message = self.get(key, default=default)

        if not parameters:
            return message

        try:
            return message.format(**parameters)
        except (KeyError, IndexError, ValueError):
            return message

    def has(self, key: str) -> bool:
        """Return whether a translation exists."""
        if key in self._translations:
            return True

        return self._fallback is not None and self._fallback.has(key)

    def with_fallback(
        self,
        fallback: Translator,
    ) -> Translator:
        """Return a translator using another translator as fallback."""
        return Translator(
            self._translations,
            fallback=fallback,
        )

    def __call__(
        self,
        key: str,
        *,
        default: str | None = None,
        **parameters: object,
    ) -> str:
        """Translate a message."""
        return self.translate(
            key,
            default=default,
            **parameters,
        )
