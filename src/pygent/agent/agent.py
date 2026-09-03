from __future__ import annotations

from dataclasses import dataclass

from pygent.agent.context import AgentContext
from pygent.agent.messages import user_message
from pygent.providers.base import Provider
from pygent.types import Message


@dataclass(slots=True)
class AgentResponse:
    """The result returned by an agent run."""

    text: str


class Agent:
    """High-level entry point for running an AI agent."""

    def __init__(self, provider: Provider) -> None:
        self.provider = provider

    async def run(
        self,
        prompt: str,
        *,
        context: AgentContext | None = None,
    ) -> AgentResponse:
        """Run the agent for a single prompt."""
        del context  # Reserved for tool execution and middleware.
        messages: list[Message] = [user_message(prompt)]
        response = await self.provider.complete(messages)
        return AgentResponse(text=response.content or "")
