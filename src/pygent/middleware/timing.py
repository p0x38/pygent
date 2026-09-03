from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from pygent.middleware.base import Middleware
from pygent.types import Message, ModelResponse, ToolDefinition


class TimingMiddleware(Middleware):
    """Record the wall-clock duration of each completion call."""

    def __init__(self) -> None:
        self.last_duration: float | None = None
        self.durations: list[float] = []

    async def complete(
        self,
        call: Callable[..., Awaitable[ModelResponse]],
        messages: list[Message],
        *,
        tools: list[ToolDefinition],
    ) -> ModelResponse:
        start = time.perf_counter()
        try:
            return await call(messages, tools=tools)
        finally:
            self.last_duration = time.perf_counter() - start
            self.durations.append(self.last_duration)
