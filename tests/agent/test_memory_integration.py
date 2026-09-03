from __future__ import annotations

import pytest

from pygent.agent import Agent
from pygent.memory import ConversationMemory
from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolDefinition


class _StubProvider(Provider):
    def __init__(self, responses: list[ModelResponse]) -> None:
        self.responses = list(responses)
        self.received: list[list[Message]] = []

    async def complete(
        self,
        messages: list[Message],
        *,
        tools: list[ToolDefinition] = (),
    ) -> ModelResponse:
        self.received.append(list(messages))
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_agent_uses_memory_history() -> None:
    memory = ConversationMemory()
    memory.seed(
        [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Earlier question"),
            Message(role="assistant", content="Earlier answer"),
        ]
    )
    provider = _StubProvider([ModelResponse(content="new answer")])
    agent = Agent(provider, memory=memory)

    response = await agent.run("follow up")

    assert response.text == "new answer"
    assert [m.content for m in provider.received[0]] == [
        "You are helpful.",
        "Earlier question",
        "Earlier answer",
        "follow up",
    ]
    assert [m.role for m in memory.messages()] == [
        "system",
        "user",
        "assistant",
        "user",
        "assistant",
    ]


@pytest.mark.asyncio
async def test_agent_without_memory_does_not_share_state() -> None:
    provider = _StubProvider([ModelResponse(content="hi")])
    agent = Agent(provider)

    response = await agent.run("hello")

    assert response.text == "hi"
    assert [m.content for m in response.messages] == ["hello", "hi"]
