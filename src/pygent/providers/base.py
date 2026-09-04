from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence

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

    async def aclose(self) -> None:
        """Release provider resources owned by the implementation."""

    async def __aenter__(self) -> Provider:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
    async def stream(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[ModelResponse]:
        """Yield response snapshots for a streaming completion.

        Providers with native streaming support should override this method.
        The default implementation preserves compatibility by yielding the
        result of :meth:`complete` as one final snapshot.
        """
        yield await self.complete(messages, tools=tools)
