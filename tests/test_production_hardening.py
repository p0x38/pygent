from __future__ import annotations

import asyncio

import pytest

from pygent.exceptions import ProviderConnectionError, ProviderRequestError
from pygent.production import (
    CancellationToken,
    RetryPolicy,
    cancellable_gather,
    is_retryable_provider_error,
    retry_async,
)


@pytest.mark.asyncio
async def test_cancellation_token() -> None:
    token = CancellationToken()
    assert not token.cancelled

    token.cancel()

    assert token.cancelled
    await asyncio.wait_for(token.wait(), timeout=0.1)


@pytest.mark.asyncio
async def test_cancellable_gather_returns_results_in_input_order() -> None:
    async def delayed(value: int, delay: float) -> int:
        await asyncio.sleep(delay)
        return value

    result = await cancellable_gather(
        delayed(1, 0.02),
        delayed(2, 0.0),
        delayed(3, 0.01),
    )

    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_cancellable_gather_cancels_pending_tasks_after_one_completes() -> None:
    token = CancellationToken()
    cancelled = asyncio.Event()

    async def fast() -> str:
        await asyncio.sleep(0)
        return "done"

    async def slow() -> None:
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled.set()
            raise

    async def cancel_later() -> None:
        await asyncio.sleep(0.01)
        token.cancel()

    cancel_task = asyncio.create_task(cancel_later())

    try:
        with pytest.raises(asyncio.CancelledError):
            await cancellable_gather(fast(), slow(), cancellation=token)
    finally:
        await cancel_task

    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_cancellable_gather_rejects_pre_cancelled_token() -> None:
    token = CancellationToken()
    token.cancel()

    with pytest.raises(asyncio.CancelledError):
        await cancellable_gather(asyncio.sleep(0), cancellation=token)


def test_retry_policy_validation() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(attempts=0)
    with pytest.raises(ValueError):
        RetryPolicy(base_delay=-1)
    with pytest.raises(ValueError):
        RetryPolicy(base_delay=2, max_delay=1)


def test_provider_retry_classification() -> None:
    assert is_retryable_provider_error(ProviderConnectionError("down"))
    assert is_retryable_provider_error(ProviderRequestError("busy", status_code=503))
    assert not is_retryable_provider_error(ProviderRequestError("bad", status_code=400))


@pytest.mark.asyncio
async def test_retry_async_retries_transient_error() -> None:
    attempts = 0

    async def operation() -> str:  # ruff: ignore[unused-async]
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ProviderConnectionError("temporary")
        return "ok"

    result = await retry_async(
        operation,
        policy=RetryPolicy(attempts=3, base_delay=0, jitter=0),
    )

    assert result == "ok"
    assert attempts == 3


@pytest.mark.asyncio
async def test_retry_async_does_not_retry_permanent_error() -> None:
    attempts = 0

    async def operation() -> None:  # ruff: ignore[unused-async]
        nonlocal attempts
        attempts += 1
        raise ProviderRequestError("bad request", status_code=400)

    with pytest.raises(ProviderRequestError):
        await retry_async(
            operation,
            policy=RetryPolicy(attempts=3, base_delay=0, jitter=0),
        )

    assert attempts == 1


@pytest.mark.asyncio
async def test_retry_async_honors_cancellation() -> None:
    token = CancellationToken()

    async def operation() -> None:  # ruff: ignore[unused-async]
        raise ProviderConnectionError("temporary")

    token.cancel()
    with pytest.raises(asyncio.CancelledError):
        await retry_async(operation, cancellation=token)
