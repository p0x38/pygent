from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TypeVar

from pygent.types import Message, ModelResponse, ToolDefinition

T = TypeVar("T")


class Middleware(ABC):
    """Composable wrapper around :meth:`Provider.complete`."""

    @abstractmethod
    async def complete(
        self,
        call: Callable[..., Awaitable[ModelResponse]],
        messages: list[Message],
        *,
        tools: list[ToolDefinition],
    ) -> ModelResponse:
        """Invoke the next stage of the pipeline."""
        raise NotImplementedError


class MiddlewareChain:
    """Compose multiple middleware into a single callable."""

    def __init__(self, middlewares: list[Middleware] | None = None) -> None:
        self.middlewares: list[Middleware] = list(middlewares or [])

    def use(self, middleware: Middleware) -> None:
        self.middlewares.append(middleware)

    def wrap(
        self,
        provider_call: Callable[..., Awaitable[ModelResponse]],
    ) -> Callable[..., Awaitable[ModelResponse]]:
        def call(
            messages: list[Message],
            *,
            tools: list[ToolDefinition],
        ) -> Awaitable[ModelResponse]:
            return self._run(provider_call, messages, tools=tools, index=0)

        return call

    async def _run(
        self,
        provider_call: Callable[..., Awaitable[ModelResponse]],
        messages: list[Message],
        *,
        tools: list[ToolDefinition],
        index: int,
    ) -> ModelResponse:
        if index >= len(self.middlewares):
            return await provider_call(messages, tools=tools)
        middleware = self.middlewares[index]

        async def next_stage(
            inner_messages: list[Message],
            *,
            tools: list[ToolDefinition],
        ) -> ModelResponse:
            return await self._run(
                provider_call, inner_messages, tools=tools, index=index + 1
            )

        return await middleware.complete(next_stage, messages, tools=tools)
