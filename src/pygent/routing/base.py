from __future__ import annotations

from abc import ABC, abstractmethod

from pygent.providers.base import Provider


class ProviderUnavailable(RuntimeError):
    """Raised by a strategy when no provider can satisfy the request."""


class ProviderEntry:
    """A provider with a logical name and optional availability check."""

    def __init__(
        self,
        name: str,
        provider: Provider,
        *,
        available: bool = True,
    ) -> None:
        self.name = name
        self.provider = provider
        self.available = available

    def __repr__(self) -> str:
        return f"ProviderEntry(name={self.name!r}, available={self.available})"


class SelectionStrategy(ABC):
    """Strategy that picks a provider for each request."""

    @abstractmethod
    def select(self, entries: list[ProviderEntry]) -> ProviderEntry:
        """Return the next provider entry to use."""
        raise NotImplementedError

    def on_failure(  # ruff: ignore[empty-method-without-abstract-decorator] - optional extension point
        self,
        entry: ProviderEntry,
        error: BaseException,
    ) -> None:
        """Hook called when a selected provider fails; default is a no-op."""


class FirstAvailableStrategy(SelectionStrategy):
    """Pick the first provider marked as available."""

    def select(self, entries: list[ProviderEntry]) -> ProviderEntry:
        for entry in entries:
            if entry.available:
                return entry
        raise ProviderUnavailable("no available providers")


class PriorityStrategy(SelectionStrategy):
    """Pick the highest-priority available provider.

    Priority is determined by the order in which providers were registered
    with the router: the first entry has the highest priority.
    """

    def select(self, entries: list[ProviderEntry]) -> ProviderEntry:
        return FirstAvailableStrategy().select(entries)


class FallbackStrategy(SelectionStrategy):
    """Cycle through available providers, remembering the last one tried."""

    def __init__(self) -> None:
        self._last_index: int = -1
        self._failed: set[str] = set()

    def select(self, entries: list[ProviderEntry]) -> ProviderEntry:
        available = [entry for entry in entries if entry.available]
        if not available:
            raise ProviderUnavailable("no available providers")

        if self._last_index >= 0:
            for offset in range(1, len(available) + 1):
                index = (self._last_index + offset) % len(available)
                candidate = available[index]
                if candidate.name not in self._failed:
                    return candidate
            raise ProviderUnavailable("all providers have failed during this request")

        for entry in available:
            if entry.name not in self._failed:
                return entry
        raise ProviderUnavailable("all providers have failed during this request")

    def on_failure(
        self,
        entry: ProviderEntry,
        error: BaseException,
    ) -> None:
        self._failed.add(entry.name)
        if self._last_index >= 0:
            self._last_index = (self._last_index + 1) % max(1, len(self._failed) + 1)

    def reset(self) -> None:
        """Forget the set of providers that have failed for the next request."""
        self._failed.clear()
        self._last_index = -1
