from __future__ import annotations

import asyncio
from collections.abc import Sequence

import pytest

from pygent.agent import Agent
from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse


class BlockingProvider(Provider):
    def __init__(self) -> None:
        self.started = 0
        self.active = 0
        self.max_active = 0

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools=(),
    ) -> ModelResponse:
        self.started += 1
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(0)
            return ModelResponse(content="ok")
        finally:
            self.active -= 1


@pytest.mark.asyncio
async def test_concurrent_runs_are_serialized() -> None:
    provider = BlockingProvider()
    agent = Agent(provider)

    await asyncio.gather(agent.run("one"), agent.run("two"))

    assert provider.started == 2
    assert provider.max_active == 1
