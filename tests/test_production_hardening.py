from __future__ import annotations

import asyncio

import pytest

from pygent.production import CancellationToken, cancellable_gather


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

    asyncio.create_task(cancel_later())
    with pytest.raises(asyncio.CancelledError):
        await cancellable_gather(fast(), slow(), cancellation=token)

    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_cancellable_gather_rejects_pre_cancelled_token() -> None:
    token = CancellationToken()
    token.cancel()

    with pytest.raises(asyncio.CancelledError):
        await cancellable_gather(asyncio.sleep(0), cancellation=token)
