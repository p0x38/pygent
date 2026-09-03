"""Middleware example: timing, usage tracking, and retry."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

from pygent import Agent
from pygent.exceptions import ProviderConnectionError
from pygent.middleware import (
    LoggingMiddleware,
    MiddlewareChain,
    RetryMiddleware,
    TimingMiddleware,
    UsageTrackingMiddleware,
)
from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolDefinition, Usage


class FlakyProvider(Provider):
    def __init__(self) -> None:
        self.calls = 0

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls += 1
        if self.calls == 1:
            raise ProviderConnectionError("transient")
        return ModelResponse(
            content="ok",
            usage=Usage(input_tokens=2, output_tokens=3, total_tokens=5),
        )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    chain = MiddlewareChain(
        [
            LoggingMiddleware(),
            RetryMiddleware(
                max_attempts=3,
                initial_delay=0.0,
                max_delay=0.0,
            ),
            TimingMiddleware(),
            UsageTrackingMiddleware(),
        ]
    )
    provider = FlakyProvider()
    wrapped = chain.wrap(provider.complete)
    agent = Agent(provider=_Adapter(wrapped))

    response = await agent.run("hello")
    print(response.text)

    usage_mw = chain.middlewares[3]
    assert isinstance(usage_mw, UsageTrackingMiddleware)
    print(f"total tokens: {usage_mw.total.total_tokens}")

    timing_mw = chain.middlewares[2]
    assert isinstance(timing_mw, TimingMiddleware)
    print(f"timing: {timing_mw.last_duration:.4f}s")


class _Adapter(Provider):
    def __init__(self, call: Any) -> None:
        self._call = call

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        return await self._call(list(messages), tools=list(tools))


if __name__ == "__main__":
    asyncio.run(main())
