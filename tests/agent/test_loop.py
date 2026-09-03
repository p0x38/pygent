from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from pygent.agent.context import AgentContext
from pygent.agent.loop import AgentLoop
from pygent.exceptions import AgentLoopError
from pygent.providers.base import Provider
from pygent.tools import Tool, ToolRegistry
from pygent.types import Message, ModelResponse, ToolCall, ToolDefinition


class FakeProvider(Provider):
    def __init__(self, responses: Sequence[ModelResponse]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[list[Message], list[ToolDefinition]]] = []

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls.append((list(messages), list(tools)))
        return self.responses.pop(0)


class EchoTool(Tool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="echo",
            description="Echo a value.",
            parameters={"type": "object"},
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> Any:
        if context is None:
            return arguments["value"]
        return context.metadata["prefix"] + arguments["value"]


class FailingTool(Tool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="fail",
            description="Always fails.",
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> Any:
        raise ValueError("boom")


class SlowTool(Tool):
    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(name="slow", description="A concurrent test tool.")

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> Any:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(0)
            return arguments["value"]
        finally:
            self.active -= 1


class RequiredTool(Tool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="required",
            description="Requires a string value.",
            parameters={
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
                "additionalProperties": False,
            },
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> Any:
        return arguments["value"]


@pytest.mark.asyncio
async def test_returns_normal_response() -> None:
    provider = FakeProvider([ModelResponse(content="hello")])
    loop = AgentLoop(provider)
    messages = [Message(role="user", content="hi")]

    response = await loop.run(messages)

    assert response.content == "hello"
    assert len(provider.calls) == 1


@pytest.mark.asyncio
async def test_executes_tool_and_continues() -> None:
    call = ToolCall(id="call-1", name="echo", arguments={"value": "world"})
    provider = FakeProvider(
        [
            ModelResponse(content="", tool_calls=[call]),
            ModelResponse(content="The tool said world."),
        ]
    )
    tools = ToolRegistry()
    tools.register(EchoTool())
    loop = AgentLoop(provider, tools)
    messages = [Message(role="user", content="echo world")]

    response = await loop.run(messages)

    assert response.content == "The tool said world."
    assert len(provider.calls) == 2
    assert provider.calls[0][1] == [tools.get("echo").definition]
    assert messages[-1].role == "tool"
    assert messages[-1].content == "world"
    assert messages[-1].tool_call_id == "call-1"


@pytest.mark.asyncio
async def test_passes_context_to_tool() -> None:
    call = ToolCall(id="call-1", name="echo", arguments={"value": "world"})
    provider = FakeProvider(
        [ModelResponse(tool_calls=[call]), ModelResponse(content="done")]
    )
    tools = ToolRegistry()
    tools.register(EchoTool())
    loop = AgentLoop(provider, tools)
    messages = [Message(role="user", content="echo world")]
    context = AgentContext(metadata={"prefix": "hello "})

    await loop.run(messages, context=context)

    assert messages[-1].content == "hello world"


@pytest.mark.asyncio
async def test_executes_multiple_tool_calls_concurrently() -> None:
    calls = [
        ToolCall(id="call-1", name="slow", arguments={"value": "one"}),
        ToolCall(id="call-2", name="slow", arguments={"value": "two"}),
    ]
    provider = FakeProvider(
        [ModelResponse(tool_calls=calls), ModelResponse(content="done")]
    )
    tools = ToolRegistry()
    slow_tool = SlowTool()
    tools.register(slow_tool)
    loop = AgentLoop(provider, tools)
    messages = [Message(role="user", content="run both")]

    response = await loop.run(messages)

    assert response.content == "done"
    assert slow_tool.max_active == 2
    assert [message.content for message in messages[-2:]] == ["one", "two"]
    assert [message.tool_call_id for message in messages[-2:]] == [
        "call-1",
        "call-2",
    ]


@pytest.mark.asyncio
async def test_tool_failure_is_returned_to_model() -> None:
    call = ToolCall(id="call-1", name="fail")
    provider = FakeProvider(
        [
            ModelResponse(tool_calls=[call]),
            ModelResponse(content="I could not run it."),
        ]
    )
    tools = ToolRegistry()
    tools.register(FailingTool())
    loop = AgentLoop(provider, tools)
    messages = [Message(role="user", content="fail")]

    response = await loop.run(messages)

    assert response.content == "I could not run it."
    assert messages[-1].content == "boom"


@pytest.mark.asyncio
async def test_invalid_tool_arguments_are_returned_to_model() -> None:
    call = ToolCall(id="call-1", name="required", arguments={})
    provider = FakeProvider(
        [ModelResponse(tool_calls=[call]), ModelResponse(content="invalid")]
    )
    tools = ToolRegistry()
    tools.register(RequiredTool())
    loop = AgentLoop(provider, tools)
    messages = [Message(role="user", content="run it")]

    response = await loop.run(messages)

    assert response.content == "invalid"
    assert messages[-1].content == "missing required arguments: value"
    assert messages[-1].tool_call_id == "call-1"


@pytest.mark.asyncio
async def test_unknown_tool_is_returned_to_model() -> None:
    call = ToolCall(id="call-1", name="missing")
    provider = FakeProvider(
        [ModelResponse(tool_calls=[call]), ModelResponse(content="done")]
    )
    loop = AgentLoop(provider)
    messages = [Message(role="user", content="use missing")]

    response = await loop.run(messages)

    assert response.content == "done"
    assert messages[-1].content == "Unknown tool: missing"
    assert messages[-1].tool_call_id == "call-1"


@pytest.mark.asyncio
async def test_max_iterations_raises() -> None:
    call = ToolCall(id="call-1", name="echo", arguments={"value": "again"})
    provider = FakeProvider([ModelResponse(tool_calls=[call]) for _ in range(2)])
    tools = ToolRegistry()
    tools.register(EchoTool())
    loop = AgentLoop(provider, tools, max_iterations=2)

    with pytest.raises(AgentLoopError, match="maximum iterations") as exc_info:
        await loop.run([Message(role="user", content="loop")])

    assert exc_info.value.iterations == 2
