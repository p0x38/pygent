"""Built-in syntax handlers for Pygent."""

from __future__ import annotations

from dataclasses import dataclass

from pygent.syntax.base import SyntaxContext, SyntaxHandler, SyntaxResult
from pygent.syntax.registry import SyntaxRegistry


@dataclass(slots=True)
class MentionHandler(SyntaxHandler):
    """Handle ``@``-prefixed mentions."""

    prefix: str = "@"
    name: str = "mention"

    async def handle(
        self,
        value: str,
        context: SyntaxContext,
    ) -> SyntaxResult:
        """Return the mentioned target as structured metadata."""
        return SyntaxResult(
            text="",
            metadata={"type": "mention", "target": value},
        )


@dataclass(slots=True)
class CommandHandler(SyntaxHandler):
    """Handle ``/``-prefixed commands."""

    prefix: str = "/"
    name: str = "command"

    async def handle(
        self,
        value: str,
        context: SyntaxContext,
    ) -> SyntaxResult:
        """Return the command as structured metadata."""
        parts = value.split(maxsplit=1)
        command = parts[0]
        arguments = parts[1] if len(parts) > 1 else ""
        return SyntaxResult(
            text="",
            metadata={
                "type": "command",
                "command": command,
                "arguments": arguments,
            },
        )


class BuiltinSyntaxPlugin:
    """Register Pygent's default mention and command handlers."""

    def __init__(
        self,
        *,
        mention_prefix: str = "@",
        command_prefix: str = "/",
    ) -> None:
        self.mention_prefix = mention_prefix
        self.command_prefix = command_prefix

    def register_syntax(self, registry: SyntaxRegistry) -> None:
        """Register the built-in handlers with ``registry``."""
        registry.register(MentionHandler(prefix=self.mention_prefix))
        registry.register(CommandHandler(prefix=self.command_prefix))


def create_builtin_syntax_registry(
    *,
    mention_prefix: str = "@",
    command_prefix: str = "/",
) -> SyntaxRegistry:
    """Create a registry containing the built-in syntax handlers."""
    registry = SyntaxRegistry()
    BuiltinSyntaxPlugin(
        mention_prefix=mention_prefix,
        command_prefix=command_prefix,
    ).register_syntax(registry)
    return registry
