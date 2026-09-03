from __future__ import annotations

from dataclasses import dataclass

from pygent.agent.context import AgentContext
from pygent.agent.loop import AgentLoop
from pygent.agent.messages import user_message
from pygent.providers.base import Provider
from pygent.tools.registry import ToolRegistry


@dataclass(slots=True)
class AgentResponse:
    """The result returned by an agent run."""

    text: str


class Agent:
    """High-level entry point for running an AI agent."""

    def __init__(
        self,
        provider: Provider,
        *,
        tools: ToolRegistry | None = None,
        max_iterations: int = 8,
    ) -> None:
        self.loop = AgentLoop(
            provider,
            tools,
            max_iterations=max_iterations,
        )

    async def run(
        self,
        prompt: str,
        *,
        context: AgentContext | None = None,
    ) -> AgentResponse:
        """Run the agent for a single prompt."""
        response = await self.loop.run([user_message(prompt)], context=context)
        return AgentResponse(text=response.content or "")
