from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pygent.agent.context import AgentContext
from pygent.agent.loop import AgentLoop
from pygent.agent.messages import user_message
from pygent.memory.base import Memory
from pygent.production import CancellationToken, RetryPolicy
from pygent.providers.base import Provider
from pygent.tools.registry import ToolRegistry
from pygent.types import Message


@dataclass(slots=True)
class AgentResponse:
    """The result returned by an agent run."""

    text: str
    messages: list[Message]


class Agent:
    """High-level entry point for running an AI agent."""

    def __init__(
        self,
        provider: Provider,
        *,
        tools: ToolRegistry | None = None,
        max_iterations: int = 8,
        max_tool_calls: int | None = None,
        total_timeout: float | None = None,
        max_context_messages: int | None = None,
        retry_policy: RetryPolicy | None = None,
        cancellation: CancellationToken | None = None,
        memory: Memory | None = None,
    ) -> None:
        self.loop = AgentLoop(
            provider,
            tools,
            max_iterations=max_iterations,
            max_tool_calls=max_tool_calls,
            total_timeout=total_timeout,
            max_context_messages=max_context_messages,
            retry_policy=retry_policy,
            cancellation=cancellation,
        )
        self.memory = memory

    async def aclose(self) -> None:
        """Release resources owned by the agent's provider."""
        await self.loop.aclose()

    async def __aenter__(self) -> Agent:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def run(
        self,
        prompt: str | Message,
        *,
        context: AgentContext | None = None,
    ) -> AgentResponse:
        """Run the agent for a single prompt, optionally using memory."""
        new_message: Message = (
            user_message(prompt) if isinstance(prompt, str) else prompt
        )

        history: list[Message]
        if self.memory is not None:
            history = list(self.memory.messages())
            self.memory.add(new_message)
            history.append(new_message)
        else:
            history = [new_message]

        response = await self.loop.run(history, context=context)

        assistant_message = Message(
            role="assistant",
            content=response.content,
            tool_calls=response.tool_calls,
        )
        if self.memory is not None:
            self.memory.add(assistant_message)
            return AgentResponse(
                text=response.content or "",
                messages=list(self.memory.messages()),
            )

        return AgentResponse(
            text=response.content or "",
            messages=[new_message, assistant_message],
        )

    async def chat(
        self,
        prompt: str | Message,
        **kwargs: Any,
    ) -> AgentResponse:
        """Alias for :meth:`run` for chat-style integrations."""
        return await self.run(prompt, **kwargs)
