from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from pygent.types import Message, ModelResponse, ToolDefinition


class Provider(ABC):
    """Base interface implemented by LLM providers."""

    @abstractmethod
    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        """Generate a response from a conversation."""
        raise NotImplementedError
