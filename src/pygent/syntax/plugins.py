"""Plugin injection helpers for Pygent syntax."""

from __future__ import annotations

from typing import Protocol

from pygent.syntax.registry import SyntaxRegistry


class SyntaxPlugin(Protocol):
    """Protocol implemented by extensions that provide syntax handlers."""

    def register_syntax(self, registry: SyntaxRegistry) -> None:
        """Inject syntax handlers into a registry."""


def inject_syntax_plugin(
    registry: SyntaxRegistry,
    plugin: SyntaxPlugin,
) -> SyntaxRegistry:
    """Inject a syntax plugin and return the registry for fluent setup."""
    plugin.register_syntax(registry)
    return registry
