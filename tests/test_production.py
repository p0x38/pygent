from __future__ import annotations

import asyncio

import pytest

from pygent.production import CancellationToken, cancellable_gather


def test_cancellation_token() -> None:
    token = CancellationToken()
    assert not token.cancelled
    token.cancel()
    assert token.cancelled


@pytest.mark.asyncio
async def test_cancellable_gather() -> None:
    token = CancellationToken()
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def work() -> str:
        started.set()
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled.set()
            raise
        return "done"

    task = asyncio.create_task(cancellable_gather(work(), cancellation=token))
    await started.wait()
    token.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_empty_cancellable_gather() -> None:
    assert await cancellable_gather() == []
