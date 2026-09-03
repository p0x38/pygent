from __future__ import annotations

import json
import math
from typing import Any

import httpx
import pytest

from pygent.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
)
from pygent.providers.compatible import OpenAICompatibleProvider
from pygent.types import Message, ToolCall, ToolDefinition, Usage


def _make_response(
    status_code: int = 200,
    body: Any = None,
) -> httpx.Response:
    request = httpx.Request("POST", "https://example.com/chat/completions")
    if body is None:
        body = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "hello"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 4,
                "completion_tokens": 7,
                "total_tokens": 11,
            },
        }
    return httpx.Response(
        status_code=status_code,
        json=body,
        request=request,
    )


class _StubTransport(httpx.AsyncBaseTransport):
    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = list(responses)
        self.calls: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        if not self.responses:
            raise AssertionError("no more responses queued")
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_complete_parses_response_with_tool_calls() -> None:
    body = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "echo",
                                "arguments": json.dumps({"value": "world"}),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {
            "prompt_tokens": 2,
            "completion_tokens": 3,
            "total_tokens": 5,
        },
    }
    transport = _StubTransport([_make_response(body=body)])
    client = httpx.AsyncClient(transport=transport, base_url="https://api.example/v1")
    provider = OpenAICompatibleProvider("test-model", api_key="key", client=client)

    response = await provider.complete(
        [Message(role="user", content="hi")],
        tools=[
            ToolDefinition(
                name="echo",
                description="Echo a value.",
                parameters={
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                },
            )
        ],
    )

    assert response.content is None
    assert response.finish_reason == "tool_calls"
    assert response.tool_calls == [
        ToolCall(id="call-1", name="echo", arguments={"value": "world"})
    ]
    assert response.usage == Usage(input_tokens=2, output_tokens=3, total_tokens=5)

    sent = transport.calls[0]
    payload = json.loads(sent.content)
    assert payload["model"] == "test-model"
    assert payload["messages"] == [{"role": "user", "content": "hi"}]
    assert payload["tools"][0]["function"]["name"] == "echo"


@pytest.mark.asyncio
async def test_complete_serialises_tool_messages() -> None:
    transport = _StubTransport([_make_response()])
    client = httpx.AsyncClient(transport=transport, base_url="https://api.example/v1")
    provider = OpenAICompatibleProvider("m", client=client)

    messages = [
        Message(role="system", content="You are helpful."),
        Message(role="user", content="hi"),
        Message(
            role="assistant",
            content=None,
            tool_calls=[ToolCall(id="c1", name="echo", arguments={})],
        ),
        Message(role="tool", content="done", name="echo", tool_call_id="c1"),
    ]
    await provider.complete(messages)

    sent = transport.calls[0]
    payload = json.loads(sent.content)
    assert payload["messages"] == [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "hi"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "c1",
                    "type": "function",
                    "function": {"name": "echo", "arguments": "{}"},
                }
            ],
        },
        {
            "role": "tool",
            "content": "done",
            "tool_call_id": "c1",
            "name": "echo",
        },
    ]


@pytest.mark.asyncio
async def test_authentication_error() -> None:
    transport = _StubTransport(
        [_make_response(status_code=401, body={"error": "unauthorized"})]
    )
    client = httpx.AsyncClient(transport=transport, base_url="https://api.example/v1")
    provider = OpenAICompatibleProvider("m", client=client)

    with pytest.raises(ProviderAuthenticationError):
        await provider.complete([Message(role="user", content="hi")])


@pytest.mark.asyncio
async def test_rate_limit_error() -> None:
    transport = _StubTransport([_make_response(status_code=429, body={})])
    client = httpx.AsyncClient(transport=transport, base_url="https://api.example/v1")
    provider = OpenAICompatibleProvider("m", client=client)

    with pytest.raises(ProviderRateLimitError):
        await provider.complete([Message(role="user", content="hi")])


@pytest.mark.asyncio
async def test_request_error_includes_status_code() -> None:
    transport = _StubTransport([_make_response(status_code=500, body={})])
    client = httpx.AsyncClient(transport=transport, base_url="https://api.example/v1")
    provider = OpenAICompatibleProvider("m", client=client)

    with pytest.raises(ProviderRequestError) as exc_info:
        await provider.complete([Message(role="user", content="hi")])
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_connection_error_is_normalised() -> None:
    class _FailingTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("boom", request=request)

    client = httpx.AsyncClient(
        transport=_FailingTransport(), base_url="https://api.example/v1"
    )
    provider = OpenAICompatibleProvider("m", client=client)

    with pytest.raises(ProviderConnectionError):
        await provider.complete([Message(role="user", content="hi")])


@pytest.mark.asyncio
async def test_response_error_on_missing_choices() -> None:
    transport = _StubTransport([_make_response(body={"choices": []})])
    client = httpx.AsyncClient(transport=transport, base_url="https://api.example/v1")
    provider = OpenAICompatibleProvider("m", client=client)

    with pytest.raises(ProviderResponseError):
        await provider.complete([Message(role="user", content="hi")])


def test_empty_model_is_rejected() -> None:
    with pytest.raises(ValueError, match="model must not be empty"):
        OpenAICompatibleProvider("")


def test_empty_base_url_is_rejected() -> None:
    with pytest.raises(ValueError, match="base_url must not be empty"):
        OpenAICompatibleProvider("m", base_url="")


@pytest.mark.asyncio
async def test_extra_body_is_merged() -> None:
    transport = _StubTransport([_make_response()])
    client = httpx.AsyncClient(transport=transport, base_url="https://api.example/v1")
    provider = OpenAICompatibleProvider(
        "m",
        client=client,
        extra_body={"temperature": 0.5, "metadata": {"trace": "abc"}},
    )

    await provider.complete([Message(role="user", content="hi")])

    sent = transport.calls[0]
    payload = json.loads(sent.content)
    assert math.isclose(payload["temperature"], 0.5)
    assert payload["metadata"] == {"trace": "abc"}
