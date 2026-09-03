"""Session-local syntax configuration for Pygent chat sessions."""

from __future__ import annotations

from dataclasses import dataclass, field

from pygent.config import SyntaxConfig
from pygent.syntax.builtin import BuiltinSyntaxPlugin
from pygent.syntax.discovery import load_syntax_plugins
from pygent.syntax.processor import SyntaxProcessor
from pygent.syntax.registry import SyntaxRegistry


@dataclass(slots=True)
class SyntaxSession:
    """Manage syntax for one interactive session.

    Changes made through this object are intentionally session-local and are
    not written to the user's persistent configuration file.
    """

    config: SyntaxConfig
    registry: SyntaxRegistry = field(init=False)

    def __post_init__(self) -> None:
        self._rebuild()

    def _rebuild(self) -> None:
        self.registry = SyntaxRegistry()
        if not self.config.enabled:
            return

        BuiltinSyntaxPlugin(
            mention_prefix=self.config.prefixes.get("mention", "@"),
            command_prefix=self.config.prefixes.get("command", "/"),
        ).register_syntax(self.registry)
        load_syntax_plugins(self.registry)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable syntax for the current session."""
        self.config.enabled = enabled
        self._rebuild()

    def set_prefix(self, kind: str, prefix: str) -> None:
        """Change a built-in syntax prefix for the current session."""
        if kind not in {"mention", "command"}:
            raise ValueError(f"Unknown syntax prefix: {kind}")
        if not prefix or any(character.isspace() for character in prefix):
            raise ValueError("Syntax prefix must be non-empty and contain no spaces")

        self.config.prefixes[kind] = prefix
        self._rebuild()

    def reset(self) -> None:
        """Restore built-in syntax defaults for the current session."""
        self.config.enabled = True
        self.config.prefixes = {"mention": "@", "command": "/"}
        self._rebuild()

    def processor(self) -> SyntaxProcessor:
        """Return a processor for the current registry."""
        return SyntaxProcessor(self.registry)


__all__ = ["SyntaxSession"]
