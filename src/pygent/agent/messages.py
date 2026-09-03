from __future__ import annotations

from pygent.types import Message


def user_message(content: str) -> Message:
    """Create a user message."""
    return Message(role="user", content=content)


def system_message(content: str) -> Message:
    """Create a system message."""
    return Message(role="system", content=content)
