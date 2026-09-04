from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from pygent.exceptions import (
    ProviderConnectionError,
    ProviderRateLimitError,
    ProviderRequestError,
)

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


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded exponential-backoff policy for transient provider failures."""

    attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 8.0
    jitter: float = 0.1

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts must be at least 1")
        if self.base_delay < 0:
            raise ValueError("base_delay must be non-negative")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be at least base_delay")
        if self.jitter < 0:
            raise ValueError("jitter must be non-negative")


def is_retryable_provider_error(exc: BaseException) -> bool:
    """Return whether a provider error is safe to retry."""
    if isinstance(exc, (ProviderConnectionError, ProviderRateLimitError)):
        return True
    if isinstance(exc, ProviderRequestError):
        return exc.status_code in {408, 409, 425, 500, 502, 503, 504}
    return False


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy | None = None,
    cancellation: CancellationToken | None = None,
) -> T:
    """Run an async operation with bounded retries for transient failures."""
    policy = policy or RetryPolicy()

    for attempt in range(1, policy.attempts + 1):
        if cancellation is not None and cancellation.cancelled:
            raise asyncio.CancelledError("agent cancellation requested")
        try:
            return await operation()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if not is_retryable_provider_error(exc) or attempt >= policy.attempts:
                raise

            delay = min(policy.max_delay, policy.base_delay * (2 ** (attempt - 1)))
            if policy.jitter:
                delay += random.uniform(0, policy.jitter)
            if cancellation is None:
                await asyncio.sleep(delay)
            else:
                try:
                    await asyncio.wait_for(cancellation.wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass

    raise AssertionError("retry loop exited unexpectedly")


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
