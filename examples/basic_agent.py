"""Minimal Pygent agent example using a stub provider.

Run with::

    python examples/basic_agent.py

This example wires a stub ``Provider`` so it runs without network access.
Swap in :class:`pygent.providers.OllamaProvider` or
:class:`pygent.providers.OpenAIProvider` to talk to a real model.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from pygent import Agent
from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolDefinition


class EchoProvider(Provider):
    """A trivial provider that always echoes the user's last message."""

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        last_user = next(
            (m for m in reversed(messages) if m.role == "user"),
            None,
        )
        content = (last_user.content if last_user else "") or ""
        return ModelResponse(content=f"echo: {content}")


async def main() -> None:
    agent = Agent(provider=EchoProvider())
    response = await agent.run("Hello, Pygent!")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
