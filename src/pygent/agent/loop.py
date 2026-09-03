from __future__ import annotations

from pygent.exceptions import AgentLoopError
from pygent.providers.base import Provider
from pygent.tools.calls import execute_tool_call
from pygent.tools.registry import ToolRegistry
from pygent.types import Message, ModelResponse


class AgentLoop:
    """Run the model/tool interaction loop for an agent."""

    def __init__(
        self,
        provider: Provider,
        tools: ToolRegistry | None = None,
        *,
        max_iterations: int = 8,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.max_iterations = max_iterations

    async def run(self, messages: list[Message]) -> ModelResponse:
        """Run until the model produces a response without tool calls."""
        for iteration in range(1, self.max_iterations + 1):
            response = await self.provider.complete(
                messages,
                tools=self.tools.definitions(),
            )

            if not response.tool_calls:
                return response

            messages.append(
                Message(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            for call in response.tool_calls:
                result = await execute_tool_call(self.tools, call)
                messages.append(
                    Message(
                        role="tool",
                        content=str(result.content),
                        tool_call_id=result.tool_call_id,
                        name=result.name,
                    )
                )

        raise AgentLoopError(
            f"Agent loop exceeded maximum iterations ({self.max_iterations})",
            iterations=iteration,
        )
