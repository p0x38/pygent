from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Sequence

import pytest

from pygent.exceptions import ProviderConnectionError
from pygent.middleware import (
    LoggingMiddleware,
    Middleware,
    MiddlewareChain,
    RetryMiddleware,
    TimingMiddleware,
    UsageTrackingMiddleware,
)
from pygent.types import Message, ModelResponse, ToolDefinition, Usage


class _ScriptedProvider:
    def __init__(
        self, responses: list[ModelResponse], errors: Sequence[Exception]
    ) -> None:
        self.responses = list(responses)
        self.errors = list(errors)
        self.calls = 0

    async def __call__(
        self,
        messages: list[Message],
        *,
        tools: list[ToolDefinition],
    ) -> ModelResponse:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_retry_middleware_retries_then_succeeds() -> None:
    errors = [ProviderConnectionError("boom"), ProviderConnectionError("boom")]
    responses = [
        ModelResponse(
            content="ok", usage=Usage(input_tokens=1, output_tokens=2, total_tokens=3)
        )
    ]
    provider = _ScriptedProvider(responses, errors)
    middleware = RetryMiddleware(
        max_attempts=3,
        initial_delay=0.0,
        max_delay=0.0,
        sleep=lambda _delay: _noop(),
    )
    chain = MiddlewareChain([middleware])
    wrapped = chain.wrap(provider)

    response = await wrapped([Message(role="user", content="hi")], tools=[])

    assert response.content == "ok"
    assert provider.calls == 3


@pytest.mark.asyncio
async def test_retry_middleware_exhausts_attempts() -> None:
    errors = [ProviderConnectionError("boom")] * 3
    provider = _ScriptedProvider([], errors)
    middleware = RetryMiddleware(
        max_attempts=2,
        initial_delay=0.0,
        max_delay=0.0,
        sleep=lambda _delay: _noop(),
    )
    chain = MiddlewareChain([middleware])
    wrapped = chain.wrap(provider)

    with pytest.raises(ProviderConnectionError):
        await wrapped([Message(role="user", content="hi")], tools=[])

    assert provider.calls == 2


@pytest.mark.asyncio
async def test_logging_middleware_invokes_logger(
    caplog: pytest.LogCaptureFixture,
) -> None:
    provider = _ScriptedProvider([ModelResponse(content="ok")], [])
    middleware = LoggingMiddleware(logger=logging.getLogger("pygent.test.logging"))
    chain = MiddlewareChain([middleware])
    wrapped = chain.wrap(provider)

    with caplog.at_level(logging.INFO, logger="pygent.test.logging"):
        await wrapped([Message(role="user", content="hi")], tools=[])

    assert any("completion.start" in rec.message for rec in caplog.records)
    assert any("completion.end" in rec.message for rec in caplog.records)


@pytest.mark.asyncio
async def test_timing_middleware_records_duration() -> None:
    provider = _ScriptedProvider([ModelResponse(content="ok")], [])
    middleware = TimingMiddleware()
    chain = MiddlewareChain([middleware])
    wrapped = chain.wrap(provider)

    await wrapped([Message(role="user", content="hi")], tools=[])

    assert middleware.last_duration is not None
    assert middleware.last_duration >= 0
    assert len(middleware.durations) == 1


@pytest.mark.asyncio
async def test_usage_middleware_accumulates() -> None:
    provider = _ScriptedProvider(
        [
            ModelResponse(
                content="a",
                usage=Usage(input_tokens=1, output_tokens=2, total_tokens=3),
            ),
            ModelResponse(
                content="b",
                usage=Usage(input_tokens=4, output_tokens=5, total_tokens=9),
            ),
        ],
        [],
    )
    middleware = UsageTrackingMiddleware()
    chain = MiddlewareChain([middleware])
    wrapped = chain.wrap(provider)

    await wrapped([Message(role="user", content="hi")], tools=[])
    await wrapped([Message(role="user", content="hi")], tools=[])

    assert middleware.total == Usage(input_tokens=5, output_tokens=7, total_tokens=12)
    assert len(middleware.calls) == 2


@pytest.mark.asyncio
async def test_chain_runs_in_order() -> None:
    order: list[str] = []

    class _Tag(Middleware):
        def __init__(self, name: str) -> None:
            self.name = name

        async def complete(
            self,
            call: Callable[..., Awaitable[ModelResponse]],
            messages: list[Message],
            *,
            tools: list[ToolDefinition],
        ) -> ModelResponse:
            order.append(self.name)
            return await call(messages, tools=tools)

    chain = MiddlewareChain([_Tag("a"), _Tag("b"), _Tag("c")])
    wrapped = chain.wrap(_ScriptedProvider([ModelResponse(content="ok")], []))

    await wrapped([Message(role="user", content="hi")], tools=[])

    assert order == ["a", "b", "c"]


async def _noop() -> None:  # ruff: ignore[unused-async]
    return None
