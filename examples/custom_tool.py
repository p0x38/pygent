"""Custom tool example.

This example registers a tiny ``reverse`` tool with an agent and shows the
conversation between the agent and the tool.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from typing import Any

from pygent import Agent
from pygent.providers.base import Provider
from pygent.tools import Tool, ToolRegistry
from pygent.types import Message, ModelResponse, ToolDefinition


class ReverseTool(Tool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="reverse",
            description="Reverse the characters of a string.",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            },
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: Any = None,
    ) -> Any:
        return arguments["text"][::-1]


class ScriptedProvider(Provider):
    """Provider that decides when to call the tool and then summarises."""

    def __init__(self) -> None:
        self.calls = 0

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls += 1
        if self.calls == 1:
            return ModelResponse(
                content=None,
                tool_calls=[
                    {
                        "id": "c1",
                        "name": "reverse",
                        "arguments": {"text": "hello"},
                    }
                ],
            )
        last_tool = next(
            (m for m in reversed(messages) if m.role == "tool"),
            None,
        )
        return ModelResponse(
            content=f"reversed: {last_tool.content if last_tool else ''}"
        )


async def main() -> None:
    registry = ToolRegistry()
    registry.register(ReverseTool())
    agent = Agent(provider=ScriptedProvider(), tools=registry)
    response = await agent.run("Reverse the word hello.")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
