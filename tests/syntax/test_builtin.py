from __future__ import annotations

import pytest

from pygent.syntax import SyntaxContext
from pygent.syntax.builtin import (
    CommandHandler,
    MentionHandler,
    create_builtin_syntax_registry,
)


@pytest.mark.asyncio
async def test_mention_handler() -> None:
    result = await MentionHandler().handle("agent:coder", SyntaxContext())

    assert result.handled
    assert result.text == ""
    assert result.metadata == {
        "type": "mention",
        "target": "agent:coder",
    }


@pytest.mark.asyncio
async def test_command_handler() -> None:
    result = await CommandHandler().handle("help", SyntaxContext())

    assert result.handled
    assert result.text == ""
    assert result.metadata == {
        "type": "command",
        "command": "help",
    }


def test_builtin_plugin_uses_default_prefixes() -> None:
    registry = create_builtin_syntax_registry()

    assert registry.get("@").name == "mention"
    assert registry.get("/").name == "command"


def test_builtin_plugin_accepts_custom_prefixes() -> None:
    registry = create_builtin_syntax_registry(
        mention_prefix="::",
        command_prefix="!",
    )

    assert registry.get("::").name == "mention"
    assert registry.get("!").name == "command"
