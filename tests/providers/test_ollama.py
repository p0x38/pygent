from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pytest

from pygent.providers.ollama import OllamaProvider
from pygent.types import Message, ToolCall, ToolDefinition, Usage


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


@dataclass
class FakeResponse:
    def __init__(
        self,
        message: FakeMessage,
        done_reason: str | None = None,
        prompt_eval_count: int | None = None,
        eval_count: int | None = None,
    ) -> None:
        self.message = message
        self.done_reason = done_reason
        self.prompt_eval_count = prompt_eval_count
        self.eval_count = eval_count


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []
        self.closed = False

    async def chat(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        return self.response

    async def aclose(self) -> None:
        self.closed = True


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
async def test_complete_maps_usage() -> None:
    client = FakeClient(
        FakeResponse(
            FakeMessage(content="hello"),
            prompt_eval_count=12,
            eval_count=5,
        )
    )
    provider = OllamaProvider("test-model", client=client)

    response = await provider.complete([Message(role="user", content="hi")])

    assert response.usage == Usage(
        input_tokens=12,
        output_tokens=5,
        total_tokens=17,
    )


@pytest.mark.asyncio
async def test_complete_omits_usage_when_counts_are_unavailable() -> None:
    client = FakeClient(FakeResponse(FakeMessage(content="hello")))
    provider = OllamaProvider("test-model", client=client)

    response = await provider.complete([Message(role="user", content="hi")])

    assert response.usage is None


@pytest.mark.asyncio
async def test_aclose_closes_client() -> None:
    client = FakeClient(FakeResponse(FakeMessage(content="ok")))
    provider = OllamaProvider("test-model", client=client)

    await provider.aclose()

    assert client.closed


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
