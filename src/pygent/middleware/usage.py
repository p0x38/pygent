from __future__ import annotations

from collections.abc import Awaitable, Callable

from pygent.middleware.base import Middleware
from pygent.types import Message, ModelResponse, ToolDefinition, Usage


class UsageTrackingMiddleware(Middleware):
    """Accumulate token usage from every completion call."""

    def __init__(self) -> None:
        self.total = Usage()
        self.calls: list[Usage] = []

    async def complete(
        self,
        call: Callable[..., Awaitable[ModelResponse]],
        messages: list[Message],
        *,
        tools: list[ToolDefinition],
    ) -> ModelResponse:
        response = await call(messages, tools=tools)
        usage = response.usage or Usage()
        self.total = Usage(
            input_tokens=self.total.input_tokens + usage.input_tokens,
            output_tokens=self.total.output_tokens + usage.output_tokens,
            total_tokens=self.total.total_tokens + usage.total_tokens,
        )
        self.calls.append(usage)
        return response

    def reset(self) -> None:
        self.total = Usage()
        self.calls = []
