from __future__ import annotations

from typing import Any

import pytest

from pygent.providers.ollama import OllamaProvider
from pygent.types import Message, ToolCall, ToolDefinition


class FakeFunction:
    def __init__(self, name: str, arguments: dict[str, Any]) -> None:
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, name: str, arguments: dict[str, Any]) -> None:
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(
        self,
        content: str | None = None,
        tool_calls: list[FakeToolCall] | None = None,
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls or []


class FakeResponse:
    def __init__(self, message: FakeMessage, done_reason: str = "stop") -> None:
        self.message = message
        self.done_reason = done_reason


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.kwargs: dict[str, Any] | None = None

    async def chat(self, **kwargs: Any) -> FakeResponse:
        self.kwargs = kwargs
        return self.response


@pytest.mark.asyncio
async def test_complete_maps_response() -> None:
    client = FakeClient(
        FakeResponse(
            FakeMessage(
                content="hello",
                tool_calls=[FakeToolCall("echo", {"value": "world"})],
            )
        )
    )
    provider = OllamaProvider("test-model", client=client)

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
    client = FakeClient(FakeResponse(FakeMessage("done")))
    provider = OllamaProvider("test-model", client=client)
    tool = ToolDefinition(
        name="echo",
        description="Echo a value.",
        parameters={
            "type": "object",
            "properties": {"value": {"type": "string"}},
        },
    )

    await provider.complete(
        [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="hello"),
        ],
        tools=[tool],
    )

    assert client.kwargs == {
        "model": "test-model",
        "messages": [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "hello"},
        ],
        "tools": [
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
        ],
        "stream": False,
    }


def test_empty_model_is_rejected() -> None:
    with pytest.raises(ValueError, match="model must not be empty"):
        OllamaProvider("")
