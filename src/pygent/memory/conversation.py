from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pygent.memory.base import Memory
from pygent.types import Message


def _message_list_factory() -> list[Message]:
    return []


def _message_history_factory() -> dict[str, list[Message]]:
    return {}


class ConversationMemory(Memory, BaseModel):
    """Simple in-memory conversation store with conversation IDs.

    Implements :class:`Memory` and also tracks the current conversation ID,
    allowing applications to maintain multiple disjoint histories.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    conversation_id: str = "default"
    history: dict[str, list[Message]] = Field(default_factory=_message_history_factory)
    current_messages: list[Message] = Field(default_factory=_message_list_factory)

    def add(self, message: Message) -> None:
        self.current_messages.append(message)
        self.history.setdefault(self.conversation_id, []).append(message)

    def messages(self) -> list[Message]:
        return list(self.current_messages)

    def all_messages(self) -> list[Message]:
        """Return the full history of the current conversation."""
        return list(self.history.get(self.conversation_id, ()))

    def clear(self) -> None:
        self.current_messages = []
        self.history.pop(self.conversation_id, None)

    def set_conversation(self, conversation_id: str) -> None:
        """Switch the active conversation, loading any prior history."""
        self.conversation_id = conversation_id
        self.current_messages = list(self.history.get(conversation_id, ()))

    def reset_conversation(self, conversation_id: str) -> None:
        """Clear a stored conversation (no-op if it does not exist)."""
        self.history.pop(conversation_id, None)
        if self.conversation_id == conversation_id:
            self.current_messages = []

    def seed(self, messages: Iterable[Message]) -> None:
        """Replace the current conversation with the provided messages."""
        self.current_messages = list(messages)
        self.history[self.conversation_id] = list(messages)

    def __len__(self) -> int:
        return len(self.current_messages)

    def __contains__(self, item: Any) -> bool:
        return item in self.current_messages
