from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from pydantic import BaseModel

from pygent.agent import (
    AgentLoop,
    StructuredOutputError,
    parse_structured_output,
    tool_arguments,
    user_message,
)
from pygent.providers.base import Provider
from pygent.tools import Tool, ToolRegistry
from pygent.types import Message, ModelResponse, ToolCall, ToolDefinition, Usage


class _StubProvider(Provider):
    def __init__(self, responses: list[ModelResponse]) -> None:
        self.responses = list(responses)

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        return self.responses.pop(0)


class _EchoTool(Tool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="echo",
            description="Echo",
            parameters={
                "type": "object",
                "properties": {"value": {"type": "string"}},
            },
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: Any = None,
    ) -> Any:
        return arguments["value"]


@pytest.mark.asyncio
async def test_stream_emits_text_delta() -> None:
    provider = _StubProvider(
        [
            ModelResponse(
                content="hello",
                usage=Usage(input_tokens=1, output_tokens=1, total_tokens=2),
            )
        ]
    )
    loop = AgentLoop(provider)

    events = [event async for event in loop.stream([user_message("hi")])]

    assert any(e.type == "iteration_start" for e in events)
    assert any(e.type == "text_delta" and e.text_delta == "hello" for e in events)
    assert any(e.type == "completion" for e in events)


@pytest.mark.asyncio
async def test_stream_reports_tool_results() -> None:
    call = ToolCall(id="c1", name="echo", arguments={"value": "x"})
    provider = _StubProvider(
        [
            ModelResponse(content=None, tool_calls=[call]),
            ModelResponse(content="done"),
        ]
    )
    registry = ToolRegistry()
    registry.register(_EchoTool())
    loop = AgentLoop(provider, registry)

    events = [event async for event in loop.stream([user_message("hi")])]
    tool_results = [e for e in events if e.type == "tool_result"]
    assert tool_results and tool_results[0].tool_result is not None
    assert tool_results[0].tool_result["content"] == "x"


class _Recipe(BaseModel):
    name: str
    servings: int


def test_parse_structured_output_from_plain_json() -> None:
    recipe = parse_structured_output('{"name": "pasta", "servings": 4}', _Recipe)
    assert recipe.name == "pasta"
    assert recipe.servings == 4


def test_parse_structured_output_from_prose() -> None:
    text = 'Here you go: {"name": "cake", "servings": 8} enjoy!'
    assert parse_structured_output(text, _Recipe) == _Recipe(name="cake", servings=8)


def test_parse_structured_output_rejects_empty() -> None:
    with pytest.raises(StructuredOutputError):
        parse_structured_output("", _Recipe)


def test_tool_arguments_validates_payload() -> None:
    validated = tool_arguments({"name": "cake", "servings": 2}, _Recipe)
    assert validated.servings == 2

    with pytest.raises(StructuredOutputError):
        tool_arguments({"name": "cake"}, _Recipe)
