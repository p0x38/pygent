"""Tool-call-aware context truncation for :class:`AgentLoop`."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from typing import Any

from pygent.agent.context import AgentContext
from pygent.agent.loop import AgentLoop
from pygent.providers.base import Provider
from pygent.tools import Tool, ToolRegistry
from pygent.types import Message, ModelResponse, ToolCall, ToolDefinition


class _CaptureProvider(Provider):
    """Provider that records every ``complete`` call it receives."""

    def __init__(self) -> None:
        self.calls: list[list[Message]] = []

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls.append(list(messages))
        return ModelResponse(content="done")


class _NoopTool(Tool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(name="noop", description="no-op")

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> Any:
        return "ok"


def _assistant_with_calls(*ids: str) -> Message:
    return Message(
        role="assistant",
        content="",
        tool_calls=[ToolCall(id=call_id, name="noop", arguments={}) for call_id in ids],
    )


def _tool_result(call_id: str, content: str = "ok") -> Message:
    return Message(role="tool", content=content, tool_call_id=call_id, name="noop")


def _summarize(messages: list[Message]) -> list[tuple[str, str | None, str | None]]:
    """Compact view for assertions: ``(role, content, tool_call_id)``."""
    return [(m.role, m.content, m.tool_call_id) for m in messages]


def _assert_tool_pairing(messages: list[Message]) -> None:
    """Assert the prepared message list is safe for a provider.

    Every ``tool`` message must reference an assistant tool call id
    that appears in the immediately preceding assistant message (with
    no nested assistant tool-call messages in between), and every
    assistant tool call id must be matched by exactly one tool result.
    """
    pending_assistant_calls: set[str] = set()
    for message in messages:
        if message.role == "assistant" and message.tool_calls:
            call_ids = {call.id for call in message.tool_calls}
            assert not (call_ids & pending_assistant_calls), (
                "nested assistant tool calls without an intervening user turn"
            )
            pending_assistant_calls = call_ids
        elif message.role == "tool":
            assert pending_assistant_calls, (
                "tool message has no preceding assistant tool call"
            )
            assert message.tool_call_id in pending_assistant_calls, (
                f"tool message id {message.tool_call_id!r} does not match "
                f"any assistant tool call {sorted(pending_assistant_calls)!r}"
            )
            pending_assistant_calls.discard(message.tool_call_id)
    assert not pending_assistant_calls, (
        f"unanswered assistant tool calls: {sorted(pending_assistant_calls)!r}"
    )


def _run_with_history(
    messages: list[Message], *, max_context_messages: int
) -> tuple[ModelResponse, list[Message]]:
    """Run the loop once and return ``(response, sent_messages)``.

    The provider immediately returns a text response (no tool calls),
    so the loop exits after a single provider call. The slice it sent
    is captured for assertion.
    """
    provider = _CaptureProvider()
    tools = ToolRegistry()
    tools.register(_NoopTool())
    loop = AgentLoop(provider, tools, max_context_messages=max_context_messages)
    response = asyncio.run(loop.run(list(messages)))
    return response, provider.calls[0]


def test_returns_unmodified_when_under_limit() -> None:
    messages = [Message(role="user", content="hi")]
    _, sent = _run_with_history(messages, max_context_messages=10)

    _assert_tool_pairing(sent)
    assert _summarize(sent) == _summarize(messages)


def test_does_not_mutate_input_messages() -> None:
    messages = [
        Message(role="system", content="sys"),
        _assistant_with_calls("a"),
        _tool_result("a"),
        Message(role="user", content="follow up"),
    ]
    snapshot = _summarize(messages)
    _, _ = _run_with_history(messages, max_context_messages=3)

    assert _summarize(messages) == snapshot


def test_preserves_all_system_messages_first() -> None:
    messages = [
        Message(role="system", content="sys-1"),
        Message(role="system", content="sys-2"),
        Message(role="user", content="hi"),
        Message(role="assistant", content="hello"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=4)

    _assert_tool_pairing(sent)
    assert [m.role for m in sent[:2]] == ["system", "system"]
    assert [m.content for m in sent[:2]] == ["sys-1", "sys-2"]
    assert len(sent) == 4


def test_keeps_tool_exchange_together_when_truncating() -> None:
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="first"),
        _assistant_with_calls("a"),
        _tool_result("a"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=3)

    _assert_tool_pairing(sent)
    # The standalone "first" user turn is dropped first; the trailing
    # complete exchange (assistant + tool result) fits in 2 slots.
    assert _summarize(sent) == [
        ("system", "sys", None),
        ("assistant", "", None),
        ("tool", "ok", "a"),
    ]


def test_drops_only_orphan_tool_messages() -> None:
    """An orphan tool at the head must be dropped, not kept dangling."""
    messages = [
        _tool_result("orphan"),  # no matching assistant anywhere
        _assistant_with_calls("a"),
        _tool_result("a"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=2)

    _assert_tool_pairing(sent)
    assert _summarize(sent) == [
        ("assistant", "", None),
        ("tool", "ok", "a"),
    ]


def test_drops_orphaned_assistant_when_tool_results_missing() -> None:
    messages = [
        Message(role="user", content="old"),
        _assistant_with_calls("a"),
        Message(role="user", content="follow up"),
        # No tool result for ``a`` -- this assistant is "unanswered".
    ]
    _, sent = _run_with_history(messages, max_context_messages=2)

    _assert_tool_pairing(sent)
    # The unanswered assistant should be dropped, leaving the second
    # user message intact at the tail.
    assert _summarize(sent) == [
        ("user", "old", None),
        ("user", "follow up", None),
    ]


def test_handles_multiple_tool_calls_in_one_assistant() -> None:
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="ask"),
        _assistant_with_calls("a", "b", "c"),
        _tool_result("a"),
        _tool_result("b"),
        _tool_result("c"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=5)

    _assert_tool_pairing(sent)
    assert len(sent) == 5
    assert sent[-1].tool_call_id == "c"


def test_keeps_full_exchange_when_budget_cuts_across_two() -> None:
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="u1"),
        _assistant_with_calls("a"),
        _tool_result("a"),
        Message(role="user", content="u2"),
        _assistant_with_calls("b"),
        _tool_result("b"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=5)

    _assert_tool_pairing(sent)
    # System + u2 + assistant(b) + tool(b) = 4 messages; the first
    # exchange (u1, assistant(a), tool(a)) is dropped atomically
    # because it doesn't fit.
    assert _summarize(sent) == [
        ("system", "sys", None),
        ("user", "u2", None),
        ("assistant", "", None),
        ("tool", "ok", "b"),
    ]


def test_handles_budget_too_small_for_one_exchange() -> None:
    """Budget only allows 2 non-system messages but a complete
    exchange requires 3 (assistant + 2 tools). Drop the standalone
    user turn first, then the trailing exchange as a unit so we
    never return an orphan assistant or an orphan tool result.
    """
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="u1"),
        _assistant_with_calls("a", "b"),
        _tool_result("a"),
        _tool_result("b"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=3)

    _assert_tool_pairing(sent)
    assert len(sent) <= 3
    # The standalone ``u1`` is dropped first; the trailing exchange
    # doesn't fit in 2 non-system slots so it is dropped as a unit,
    # leaving only the system message.
    assert _summarize(sent) == [("system", "sys", None)]


def test_tightest_legal_budget_returns_only_system_messages() -> None:
    # ``max_context_messages=1`` is rejected by the constructor; the
    # tightest legal budget is 2, which can fit a single system
    # message and one safe trailing message. With multiple exchanges
    # in the history the trailing complete exchange is preserved and
    # the older conversation is dropped.
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="hi"),
        _assistant_with_calls("a"),
        _tool_result("a"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=2)

    _assert_tool_pairing(sent)
    # System + complete exchange (assistant + tool) = 3 messages,
    # which exceeds the budget of 2. The standalone ``hi`` is dropped
    # first, then the trailing exchange (also doesn't fit), so only
    # the system message survives.
    assert _summarize(sent) == [("system", "sys", None)]


def test_no_system_messages_within_budget() -> None:
    messages = [
        Message(role="user", content="u1"),
        _assistant_with_calls("a"),
        _tool_result("a"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=2)

    _assert_tool_pairing(sent)
    assert _summarize(sent) == [
        ("assistant", "", None),
        ("tool", "ok", "a"),
    ]


def test_preserves_full_history_when_at_exact_limit() -> None:
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="u"),
        _assistant_with_calls("a"),
        _tool_result("a"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=4)

    _assert_tool_pairing(sent)
    assert _summarize(sent) == _summarize(messages)


def test_run_does_not_mutate_messages_and_sends_safe_slice() -> None:
    """End-to-end: ``AgentLoop.run`` leaves the user's ``messages``
    list untouched and sends the provider a tool-call-consistent
    slice whose size respects ``max_context_messages``.
    """
    provider = _CaptureProvider()
    tools = ToolRegistry()
    tools.register(_NoopTool())
    loop = AgentLoop(provider, tools, max_context_messages=4)
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="first"),
        _assistant_with_calls("a"),
        _tool_result("a"),
        Message(role="user", content="latest"),
    ]
    original_snapshot = _summarize(messages)

    response = asyncio.run(loop.run(messages))

    assert response.content == "done"
    # User's messages list is untouched.
    assert _summarize(messages) == original_snapshot
    # Provider saw a tool-call-consistent slice.
    _assert_tool_pairing(provider.calls[0])
    # The sent slice must not exceed ``max_context_messages``.
    assert len(provider.calls[0]) <= 4


def test_truncation_drops_oldest_exchange_atomically() -> None:
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="u1"),
        _assistant_with_calls("a"),
        _tool_result("a"),
        Message(role="user", content="u2"),
        _assistant_with_calls("b"),
        _tool_result("b"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=5)

    _assert_tool_pairing(sent)
    # The first exchange is dropped atomically; ``u1`` cannot survive
    # without its assistant+tool pair.
    assert _summarize(sent) == [
        ("system", "sys", None),
        ("user", "u2", None),
        ("assistant", "", None),
        ("tool", "ok", "b"),
    ]


def test_truncation_handles_three_consecutive_tool_exchanges() -> None:
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="u1"),
        _assistant_with_calls("a"),
        _tool_result("a"),
        Message(role="user", content="u2"),
        _assistant_with_calls("b"),
        _tool_result("b"),
        Message(role="user", content="u3"),
        _assistant_with_calls("c"),
        _tool_result("c"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=6)

    _assert_tool_pairing(sent)
    # Each exchange is 3 messages (user + assistant + tool). With
    # budget 6 and 1 system message, keep=5. We can fit one complete
    # exchange plus 2 trailing messages; the algorithm drops u1, the
    # (assistant(a), tool(a)) exchange, then u2 to fit u3 + exchange
    # (assistant(b), tool(b)) + u3 + exchange (assistant(c), tool(c)).
    assert _summarize(sent) == [
        ("system", "sys", None),
        ("assistant", "", None),
        ("tool", "ok", "b"),
        ("user", "u3", None),
        ("assistant", "", None),
        ("tool", "ok", "c"),
    ]


def test_truncation_keeps_latest_user_message_when_safe() -> None:
    """When only the latest user message fits in the budget, the
    algorithm should drop the older exchange and keep the safe user
    message rather than discarding everything.
    """
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="old"),
        _assistant_with_calls("a"),
        _tool_result("a"),
        Message(role="user", content="latest"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=3)

    _assert_tool_pairing(sent)
    # System + (old+assistant+tool dropped atomically) + latest user
    # message is the only safe choice.
    assert _summarize(sent) == [
        ("system", "sys", None),
        ("user", "latest", None),
    ]


def test_truncation_preserves_messages_when_limit_unset() -> None:
    provider = _CaptureProvider()
    tools = ToolRegistry()
    tools.register(_NoopTool())
    loop = AgentLoop(provider, tools)  # max_context_messages defaults to None
    messages = [
        _assistant_with_calls("a"),
        _tool_result("a"),
        Message(role="user", content="hi"),
    ]

    response = asyncio.run(loop.run(list(messages)))

    assert response.content == "done"
    _assert_tool_pairing(provider.calls[0])
    assert _summarize(provider.calls[0]) == _summarize(messages)


def test_truncation_handles_assistant_without_tool_calls() -> None:
    """A plain assistant message (no tool_calls) is just text and
    does not need to be paired with anything.
    """
    messages = [
        Message(role="system", content="sys"),
        Message(role="user", content="u1"),
        Message(role="assistant", content="hi back"),
        Message(role="user", content="u2"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=3)

    _assert_tool_pairing(sent)
    # With budget=3, the leading user is dropped to make room for the
    # assistant + u2.
    assert _summarize(sent) == [
        ("system", "sys", None),
        ("assistant", "hi back", None),
        ("user", "u2", None),
    ]


def test_truncation_drops_orphan_tool_at_head_when_only_tools() -> None:
    messages = [
        _tool_result("orphan"),
        _tool_result("orphan2"),
    ]
    _, sent = _run_with_history(messages, max_context_messages=2)

    _assert_tool_pairing(sent)
    # Both tool messages are orphans with no matching assistant in the
    # history. They must be dropped to keep the provider slice safe.
    assert sent == []
