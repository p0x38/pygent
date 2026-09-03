"""Provider routing example."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from pygent import Agent
from pygent.providers.base import Provider
from pygent.routing import (
    FallbackStrategy,
    ProviderEntry,
    Router,
)
from pygent.types import Message, ModelResponse, ToolDefinition


class FixedProvider(Provider):
    def __init__(self, name: str, content: str) -> None:
        self.name = name
        self.content = content

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        return ModelResponse(content=f"{self.name}: {self.content}")


class FailingProvider(Provider):
    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        from pygent.exceptions import ProviderConnectionError

        raise ProviderConnectionError("primary unavailable")


async def main() -> None:
    router = Router(
        [
            ProviderEntry("primary", FailingProvider()),
            ProviderEntry("secondary", FixedProvider("secondary", "ok")),
        ],
        strategy=FallbackStrategy(),
    )
    agent = Agent(provider=router)
    response = await agent.run("hello")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
