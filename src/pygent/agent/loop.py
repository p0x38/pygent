from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable

from pygent.agent.context import AgentContext
from pygent.agent.events import AgentEvent
from pygent.exceptions import AgentLoopError
from pygent.production import (
    CancellationToken,
    RetryPolicy,
    cancellable_gather,
    retry_async,
)
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
        """Build a truncated copy of ``messages`` safe for the provider.

        Tool-call exchanges (assistant ``tool_calls`` and their matching
        ``tool`` results) are kept atomically: a ``tool`` message is never
        sent without its corresponding assistant tool call, and an
        assistant tool-call message is never sent without **all** of its
        corresponding tool results (including when an assistant emits
        multiple tool calls in one response).

        System messages are preserved first, mirroring the previous
        behavior. The original ``messages`` list is never mutated.
        """
        if self.max_context_messages is None:
            return list(messages)

        # Fast path: when the messages already fit the budget *and* are
        # tool-call-safe, return a shallow copy without further work.
        if len(messages) <= self.max_context_messages:
            candidate = list(messages)
            if _is_tool_call_safe(candidate):
                return candidate
            # Otherwise fall through to the safe truncation path: the
            # conversation is internally inconsistent (orphan tool
            # messages / unanswered tool calls) and needs cleanup.

        system = [message for message in messages if message.role == "system"]
        non_system = [message for message in messages if message.role != "system"]

        keep = self.max_context_messages - len(system)
        if keep <= 0:
            # No room for any non-system message after the system slice;
            # never return an incomplete tool exchange.
            return list(system[: self.max_context_messages])

        prepared_non_system = self._truncate_non_system(non_system, keep)
        return [*system, *prepared_non_system]

    @staticmethod
    def _truncate_non_system(non_system: list[Message], keep: int) -> list[Message]:
        """Return a tool-call-aware suffix of ``non_system``.

        The algorithm walks ``non_system`` backwards and tracks the
        ``tool_call_id`` set that must remain paired. When a budget cut
        would orphan a tool call or tool result, the offending exchange
        is dropped atomically from the *front* of the kept window so the
        trailing messages stay self-consistent.
        """
        if keep <= 0 or not non_system:
            return []

        # First pass: take the newest ``keep`` messages, but expand backward
        # whenever a tool message or assistant tool-call message would be
        # left without its counterpart(s). This guarantees the kept slice
        # is internally consistent before we apply the budget cap.
        consistent = _ToolExchangeWindow.from_tail(non_system)

        # Second pass: if the consistent window is still longer than the
        # budget, drop complete exchanges from the front until we fit. We
        # never split an exchange here.
        window = list(consistent)
        while len(window) > keep:
            if not _drop_oldest_exchange(window):
                # Defensive: should not happen because ``consistent`` is
                # already exchange-aligned, but bail out safely.
                break
        return window

    def _too_many_tool_calls(self, count: int) -> bool:
        return self.max_tool_calls is not None and count >= self.max_tool_calls

    async def _provider_call(self, messages: list[Message]) -> ModelResponse:
        self._check_cancelled()
        prepared = self._prepare_messages(messages)

        def coroutine():
            return self.provider.complete(
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
                *(
                    execute_tool_call(self.tools, call, context=context)
                    for call in response.tool_calls
                ),
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
                yield AgentEvent(
                    type="text_delta", iteration=iteration, text_delta=response.content
                )

            if not response.tool_calls:
                yield AgentEvent(
                    type="completion", iteration=iteration, response=response
                )
                return

            tool_call_count += len(response.tool_calls)
            if self._too_many_tool_calls(tool_call_count):
                yield AgentEvent(
                    type="error",
                    iteration=iteration,
                    error=(
                        f"Agent loop exceeded maximum tool calls "
                        f"({self.max_tool_calls})"
                    ),
                )
                return

            messages.append(
                Message(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            results = await cancellable_gather(
                *(
                    execute_tool_call(self.tools, call, context=context)
                    for call in response.tool_calls
                ),
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


def _is_tool_call_safe(messages: list[Message]) -> bool:
    """Return ``True`` iff every tool message has a parent assistant
    tool call and every assistant tool call has a matching tool
    result, with no nested assistant tool-call messages.

    Used by the fast path in :meth:`AgentLoop._prepare_messages` so a
    safe conversation that already fits the budget isn't rewritten.
    """
    pending_assistant_calls: set[str] = set()
    for message in messages:
        if message.role == "assistant" and message.tool_calls:
            call_ids = {call.id for call in message.tool_calls}
            if call_ids & pending_assistant_calls:
                return False
            pending_assistant_calls = set(call_ids)
        elif message.role == "tool":
            if not pending_assistant_calls:
                return False
            if message.tool_call_id not in pending_assistant_calls:
                return False
            pending_assistant_calls.discard(message.tool_call_id)
    return not pending_assistant_calls


def _drop_oldest_exchange(window: list[Message]) -> bool:
    """Drop the oldest exchange from ``window`` in place.

    An "exchange" starts at the oldest message that begins a logical
    unit of conversation: either a ``user`` message, an assistant
    message with ``tool_calls``, an orphan ``tool`` message, or any
    other non-system message. Messages belonging to the same exchange
    (its assistant tool-call message and all of its tool results) are
    dropped together so the remainder stays self-consistent.

    Returns ``True`` if a message was removed, ``False`` if the window
    is empty.
    """
    if not window:
        return False

    front = window[0]

    # Orphan tool message at the head: nothing to pair it with above.
    # Drop only the orphaned tool(s) until we find a message that can
    # anchor an exchange.
    if front.role == "tool":
        del window[0]
        return True

    # Find the end index (exclusive) of the oldest exchange starting at
    # index 0. The exchange is:
    #   - a user message (length 1),
    #   - an assistant message without tool_calls (length 1), or
    #   - an assistant(tool_calls=[...]) followed by all of its tool
    #     results, possibly followed by additional non-tool text from
    #     the same assistant turn.
    end = _exchange_end(window, 0)
    if end <= 0:
        # Should not happen, but stay defensive.
        del window[0]
        return True
    del window[:end]
    return True


def _exchange_end(window: list[Message], start: int) -> int:
    """Return the exclusive index of the message after the exchange at
    ``start``.

    If the exchange starts with an assistant message carrying
    ``tool_calls``, the exchange includes every following ``tool``
    message whose ``tool_call_id`` matches one of those calls.
    """
    if start >= len(window):
        return start
    head = window[start]
    if head.role != "assistant" or not head.tool_calls:
        return start + 1
    expected = {call.id for call in head.tool_calls}
    end = start + 1
    while end < len(window) and window[end].role == "tool":
        if window[end].tool_call_id in expected:
            end += 1
        else:
            break
    return end


class _ToolExchangeWindow:
    """Build a tool-call-aware suffix of non-system messages.

    Walking backwards from the tail, we track two sets:

    * ``pending_results``: ``tool_call_id`` values for which we still
      need to find a matching ``tool`` message (because we've seen the
      assistant tool call but not its result yet).
    * ``orphan_tools``: ``tool_call_id`` values for ``tool`` messages
      that have no preceding assistant tool call in the kept window.

    The walk finishes when both sets are empty (a self-consistent
    suffix) or when we exhaust the input. The resulting slice is then
    returned in its original order.
    """

    __slots__ = ("_messages",)

    def __init__(self, messages: list[Message]) -> None:
        self._messages = messages

    @classmethod
    def from_tail(cls, messages: Iterable[Message]) -> list[Message]:
        window = cls(list(messages))
        return window._build()

    def _build(self) -> list[Message]:
        kept: list[Message] = []
        pending_results: set[str] = set()
        orphan_tools: set[str] = set()
        for message in reversed(self._messages):
            role = message.role
            if role == "tool":
                tool_call_id = message.tool_call_id
                if tool_call_id is None:
                    # A ``tool`` message without an id can never be
                    # matched. Keep it (best-effort) but never let it
                    # drag more messages with it.
                    kept.append(message)
                    continue
                if tool_call_id in pending_results:
                    pending_results.discard(tool_call_id)
                    kept.append(message)
                    continue
                # We have not yet seen the parent assistant tool call.
                # Stash as an orphan; we'll either find the parent as
                # we walk further back, or drop the orphan if we don't.
                orphan_tools.add(tool_call_id)
                kept.append(message)
                continue
            if role == "assistant" and message.tool_calls:
                call_ids = {call.id for call in message.tool_calls}
                if call_ids <= pending_results:
                    # Every tool call already has a matching result.
                    pending_results -= call_ids
                    kept.append(message)
                    continue
                if call_ids <= orphan_tools:
                    # The orphan tool messages we kept belong to this
                    # assistant. They are now paired and stop being
                    # orphans.
                    orphan_tools -= call_ids
                    kept.append(message)
                    continue
                # This assistant refers to tool calls we have not seen
                # at all (they were already truncated from the front of
                # the conversation). Drop the assistant *and* any orphan
                # tool messages that referenced it.
                orphan_tools -= call_ids
                kept = [
                    m
                    for m in kept
                    if not (m.role == "tool" and m.tool_call_id in call_ids)
                ]
                continue
            # user / assistant without tool_calls / anything else.
            kept.append(message)

        # Defensive: if we somehow still have unresolved ids, drop the
        # matching orphan tool messages so the result is self-consistent.
        if orphan_tools:
            kept = [
                m
                for m in kept
                if not (m.role == "tool" and m.tool_call_id in orphan_tools)
            ]
        if pending_results:
            # Assistant tool calls without results. Drop the offending
            # assistant message so the provider never sees an unanswered
            # tool call.
            kept = [
                m
                for m in kept
                if not (
                    m.role == "assistant"
                    and m.tool_calls
                    and {c.id for c in m.tool_calls} & pending_results
                )
            ]

        kept.reverse()
        return kept
