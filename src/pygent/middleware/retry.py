from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable

from pygent.middleware.base import Middleware
from pygent.types import Message, ModelResponse, ToolDefinition


class RetryMiddleware(Middleware):
    """Retry a completion call with exponential backoff on retryable errors."""

    def __init__(
        self,
        *,
        max_attempts: int = 3,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        jitter: float = 0.1,
        retry_on: tuple[type[BaseException], ...] = (Exception,),
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.retry_on = retry_on
        self._sleep = sleep or asyncio.sleep

    async def complete(
        self,
        call: Callable[..., Awaitable[ModelResponse]],
        messages: list[Message],
        *,
        tools: list[ToolDefinition],
    ) -> ModelResponse:
        attempt = 0
        while True:
            try:
                return await call(messages, tools=tools)
            except self.retry_on:
                attempt += 1
                if attempt >= self.max_attempts:
                    raise
                delay = min(
                    self.max_delay,
                    self.initial_delay * (2 ** (attempt - 1)),
                )
                if self.jitter:
                    delay += random.uniform(0, self.jitter) * delay
                await self._sleep(delay)
