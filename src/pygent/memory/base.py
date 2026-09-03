from __future__ import annotations

from abc import ABC, abstractmethod

from pygent.types import Message


class Memory(ABC):
    """A store of conversation history for an agent."""

    @abstractmethod
    def add(self, message: Message) -> None:
        """Append a message to the store."""
        raise NotImplementedError

    @abstractmethod
    def messages(self) -> list[Message]:
        """Return a snapshot of the stored messages."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Reset the memory store."""
        raise NotImplementedError
