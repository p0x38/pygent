"""Conversation memory example."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from pygent import Agent
from pygent.memory import ConversationMemory
from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolDefinition


class ScriptedProvider(Provider):
    def __init__(self) -> None:
        self.calls = 0

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls += 1
        return ModelResponse(content=f"reply #{self.calls}")


async def main() -> None:
    memory = ConversationMemory()
    agent = Agent(provider=ScriptedProvider(), memory=memory)

    await agent.run("Hello!")
    await agent.run("How are you?")

    for message in memory.messages():
        print(f"{message.role}: {message.content}")


if __name__ == "__main__":
    asyncio.run(main())
