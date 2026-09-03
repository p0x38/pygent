from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Provider(Protocol):
    async def generate(self, prompt: str) -> str:
        """Generate a response for a prompt."""


@dataclass(slots=True)
class AgentResponse:
    """The result returned by an agent run."""

    text: str


class Agent:
    """High-level entry point for running an AI agent."""

    def __init__(self, provider: Provider) -> None:
        self.provider = provider

    async def run(self, prompt: str) -> AgentResponse:
        """Run the agent for a single prompt."""
        text = await self.provider.generate(prompt)
        return AgentResponse(text=text)
