"""Provider contract tests.

Each provider must implement the same minimal contract: respond to user
messages, convert tool calls, and surface usage information. These tests
verify the contract using a small set of synthetic responses.
"""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolDefinition, Usage


class _CallableProvider(Provider):
    """A provider that returns responses produced by a script."""

    def __init__(self, script: list[ModelResponse]) -> None:
        self.script = list(script)
        self.calls: list[list[Message]] = []

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls.append(list(messages))
        return self.script.pop(0)


def _contract_assertions(
    provider: Provider,
    response: ModelResponse,
    expected_content: str,
) -> None:
    assert isinstance(response, ModelResponse)
    assert response.content == expected_content
    assert response.tool_calls == []


@pytest.mark.asyncio
async def test_provider_returns_model_response() -> None:
    provider = _CallableProvider([ModelResponse(content="hello")])
    response = await provider.complete([Message(role="user", content="hi")])
    _contract_assertions(provider, response, "hello")


@pytest.mark.asyncio
async def test_provider_surfaces_tool_calls() -> None:
    provider = _CallableProvider([ModelResponse(content=None, tool_calls=[])])
    response = await provider.complete([Message(role="user", content="hi")])
    assert isinstance(response, ModelResponse)
    assert response.tool_calls == []


@pytest.mark.asyncio
async def test_provider_surfaces_usage() -> None:
    provider = _CallableProvider(
        [
            ModelResponse(
                content="ok",
                usage=Usage(input_tokens=3, output_tokens=4, total_tokens=7),
            )
        ]
    )
    response = await provider.complete([Message(role="user", content="hi")])
    assert response.usage == Usage(input_tokens=3, output_tokens=4, total_tokens=7)
