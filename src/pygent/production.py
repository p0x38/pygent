from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

T = TypeVar("T")


class CancellationToken:
    """Cooperative cancellation signal for long-running agent work."""

    def __init__(self) -> None:
        self._event = asyncio.Event()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        """Request cancellation."""
        self._event.set()

    async def wait(self) -> None:
        """Wait until cancellation is requested."""
        await self._event.wait()


async def cancellable_gather(
    *coroutines: Awaitable[T],
    cancellation: CancellationToken | None = None,
) -> list[T]:
    """Gather awaitables while reliably propagating cooperative cancellation."""
    tasks = [asyncio.ensure_future(coroutine) for coroutine in coroutines]
    if not tasks:
        return []

    cancellation_task: asyncio.Task[None] | None = None
    try:
        if cancellation is None:
            return list(await asyncio.gather(*tasks))

        if cancellation.cancelled:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise asyncio.CancelledError("agent cancellation requested")

        cancellation_task = asyncio.create_task(cancellation.wait())
        pending: set[asyncio.Task[T]] = set(tasks)
        while pending:
            done, pending = await asyncio.wait(
                [*pending, cancellation_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            if cancellation_task in done and cancellation.cancelled:
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
                raise asyncio.CancelledError("agent cancellation requested")

            if cancellation_task in done:
                done.discard(cancellation_task)

            if not pending:
                break

        return [task.result() for task in tasks]
    except asyncio.CancelledError:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    finally:
        if cancellation_task is not None:
            cancellation_task.cancel()
            await asyncio.gather(cancellation_task, return_exceptions=True)
