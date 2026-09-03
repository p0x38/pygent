from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from pygent.providers.ollama import OllamaProvider
from pygent.types import Message, ToolCall, ToolDefinition


class FakeFunction:
    def __init__(self, name: str, arguments: Mapping[str, Any]) -> None:
        self.name = name
        self.arguments = dict(arguments)


class FakeToolCall:
    def __init__(self, name: str, arguments: Mapping[str, Any]) -> None:
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(
        self,
        content: str | None = None,
        tool_calls: Sequence[FakeToolCall] = (),
    ) -> None:
        self.content = content
        self.tool_calls = list(tool_calls)


class FakeResponse:
    def __init__(self, message: FakeMessage, done_reason: str | None = None) -> None:
        self.message = message
        self.done_reason = done_reason


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    async def chat(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        return self.response


@pytest.mark.asyncio
async def test_complete_maps_response() -> None:
    client = FakeClient(
        FakeResponse(
            FakeMessage(
                content="hello",
                tool_calls=[FakeToolCall("echo", {"value": "world"})],
            ),
            done_reason="stop",
        )
    )
    provider = OllamaProvider("qwen2.5-coder:3b", client=client)

    response = await provider.complete([Message(role="user", content="hi")])

    assert response.content == "hello"
    assert response.finish_reason == "stop"
    assert response.tool_calls == [
        ToolCall(
            id="ollama-call-1",
            name="echo",
            arguments={"value": "world"},
        )
    ]


@pytest.mark.asyncio
async def test_complete_maps_messages_and_tools() -> None:
    client = FakeClient(FakeResponse(FakeMessage(content="ok")))
    provider = OllamaProvider("test-model", client=client)
    messages = [
        Message(role="system", content="You are helpful."),
        Message(role="user", content="hello"),
    ]
    tools = [
        ToolDefinition(
            name="echo",
            description="Echo a value.",
            parameters={
                "type": "object",
                "properties": {"value": {"type": "string"}},
            },
        )
    ]

    await provider.complete(messages, tools=tools)

    call = client.calls[0]
    assert call["model"] == "test-model"
    assert call["stream"] is False
    assert call["messages"] == [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "hello"},
    ]
    assert call["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Echo a value.",
                "parameters": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                },
            },
        }
    ]


def test_empty_model_is_rejected() -> None:
    with pytest.raises(ValueError, match="model must not be empty"):
        OllamaProvider("")
