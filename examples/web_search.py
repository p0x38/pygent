"""Web search skill example with a stub provider.

This example wires the ``WebSearchSkill`` into a tool registry and uses a
scripted provider to demonstrate the conversation.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from pygent import Agent
from pygent.providers.base import Provider
from pygent.skills.web_search import WebSearchSkill
from pygent.tools import ToolRegistry
from pygent.types import Message, ModelResponse, ToolCall, ToolDefinition


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
        if self.calls == 1:
            return ModelResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="c1",
                        name="web_search",
                        arguments={"query": "pygent"},
                    )
                ],
            )
        last_tool = next(
            (m for m in reversed(messages) if m.role == "tool"),
            None,
        )
        return ModelResponse(
            content=f"search results: {last_tool.content if last_tool else ''}"
        )


async def main() -> None:
    registry = ToolRegistry()
    skill = WebSearchSkill(provider=_StubSearch())
    skill.register_into(registry)
    agent = Agent(provider=ScriptedProvider(), tools=registry)
    response = await agent.run("Look up pygent on the web.")
    print(response.text)


class _StubSearch:
    async def search(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        return [
            {
                "title": f"Result for {query}",
                "href": "https://example.com",
                "body": f"About {query}",
            }
        ]


if __name__ == "__main__":
    asyncio.run(main())
