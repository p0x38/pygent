from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from pygent.agent.context import AgentContext
from pygent.agent.events import AgentEvent
from pygent.exceptions import AgentLoopError
from pygent.production import CancellationToken, RetryPolicy, cancellable_gather, retry_async
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
        max_tool_calls: int | None = None,
        total_timeout: float | None = None,
        max_context_messages: int | None = None,
        retry_policy: RetryPolicy | None = None,
        cancellation: CancellationToken | None = None,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        if max_tool_calls is not None and max_tool_calls < 1:
            raise ValueError("max_tool_calls must be at least 1 when set")
        if total_timeout is not None and total_timeout <= 0:
            raise ValueError("total_timeout must be positive when set")
        if max_context_messages is not None and max_context_messages < 2:
            raise ValueError("max_context_messages must be at least 2 when set")
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.max_iterations = max_iterations
        self.max_tool_calls = max_tool_calls
        self.total_timeout = total_timeout
        self.max_context_messages = max_context_messages
        self.retry_policy = retry_policy
        self.cancellation = cancellation

    def _check_cancelled(self) -> None:
        if self.cancellation is not None and self.cancellation.cancelled:
            raise asyncio.CancelledError("agent cancellation requested")

    def _prepare_messages(self, messages: list[Message]) -> list[Message]:
        """Keep the system prompt and newest messages within the configured bound."""
        if self.max_context_messages is None or len(messages) <= self.max_context_messages:
            return messages
        system = [message for message in messages if message.role == "system"]
        non_system = [message for message in messages if message.role != "system"]
        keep = self.max_context_messages - len(system)
        if keep <= 0:
            return system[: self.max_context_messages]
        return [*system, *non_system[-keep:]]

    def _too_many_tool_calls(self, count: int) -> bool:
        return self.max_tool_calls is not None and count >= self.max_tool_calls

    async def _provider_call(self, messages: list[Message]) -> ModelResponse:
        self._check_cancelled()
        prepared = self._prepare_messages(messages)
        coroutine = lambda: self.provider.complete(
            prepared,
            tools=self.tools.definitions(),
        )
        if self.total_timeout is None:
            return await retry_async(
                coroutine,
                policy=self.retry_policy,
                cancellation=self.cancellation,
            )
        return await asyncio.wait_for(
            retry_async(
                coroutine,
                policy=self.retry_policy,
                cancellation=self.cancellation,
            ),
            timeout=self.total_timeout,
        )

    async def aclose(self) -> None:
        """Release provider resources."""
        await self.provider.aclose()

    async def run(
        self,
        messages: list[Message],
        *,
        context: AgentContext | None = None,
    ) -> ModelResponse:
        """Run until the model produces a response without tool calls."""
        tool_call_count = 0
        for iteration in range(1, self.max_iterations + 1):
            self._check_cancelled()
            response = await self._provider_call(messages)

            if not response.tool_calls:
                return response

            tool_call_count += len(response.tool_calls)
            if self._too_many_tool_calls(tool_call_count):
                raise AgentLoopError(
                    f"Agent loop exceeded maximum tool calls ({self.max_tool_calls})",
                    iterations=iteration,
                )

            messages.append(
                Message(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            results = await cancellable_gather(
                *(execute_tool_call(self.tools, call, context=context) for call in response.tool_calls),
                cancellation=self.cancellation,
            )
            messages.extend(
                Message(
                    role="tool",
                    content=str(result.content),
                    tool_call_id=result.tool_call_id,
                    name=result.name,
                )
                for result in results
            )

        raise AgentLoopError(
            f"Agent loop exceeded maximum iterations ({self.max_iterations})",
            iterations=self.max_iterations,
        )

    async def stream(
        self,
        messages: list[Message],
        *,
        context: AgentContext | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """Stream :class:`AgentEvent` instances from a complete run."""
        tool_call_count = 0
        for iteration in range(1, self.max_iterations + 1):
            self._check_cancelled()
            yield AgentEvent(type="iteration_start", iteration=iteration)
            try:
                response = await self._provider_call(messages)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                yield AgentEvent(type="error", iteration=iteration, error=str(exc))
                return

            if response.content:
                yield AgentEvent(type="text_delta", iteration=iteration, text_delta=response.content)

            if not response.tool_calls:
                yield AgentEvent(type="completion", iteration=iteration, response=response)
                return

            tool_call_count += len(response.tool_calls)
            if self._too_many_tool_calls(tool_call_count):
                yield AgentEvent(
                    type="error",
                    iteration=iteration,
                    error=f"Agent loop exceeded maximum tool calls ({self.max_tool_calls})",
                )
                return

            messages.append(
                Message(role="assistant", content=response.content, tool_calls=response.tool_calls)
            )

            results = await cancellable_gather(
                *(execute_tool_call(self.tools, call, context=context) for call in response.tool_calls),
                cancellation=self.cancellation,
            )
            for call, result in zip(response.tool_calls, results, strict=False):
                yield AgentEvent(
                    type="tool_result",
                    iteration=iteration,
                    tool_call=call,
                    tool_result={
                        "name": result.name,
                        "tool_call_id": result.tool_call_id,
                        "content": result.content,
                        "is_error": result.is_error,
                    },
                )
            messages.extend(
                Message(
                    role="tool",
                    content=str(result.content),
                    tool_call_id=result.tool_call_id,
                    name=result.name,
                )
                for result in results
            )
            yield AgentEvent(type="iteration_end", iteration=iteration)

        yield AgentEvent(
            type="error",
            iteration=self.max_iterations,
            error=f"Agent loop exceeded maximum iterations ({self.max_iterations})",
        )
