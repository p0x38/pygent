from __future__ import annotations

from collections.abc import Sequence

from pygent.exceptions import RouterError
from pygent.providers.base import Provider
from pygent.routing.base import (
    FirstAvailableStrategy,
    ProviderEntry,
    ProviderUnavailable,
    SelectionStrategy,
)
from pygent.types import Message, ModelResponse, ToolDefinition


class Router(Provider):
    """A provider that delegates to a configurable selection strategy."""

    def __init__(
        self,
        entries: Sequence[ProviderEntry | Provider],
        *,
        strategy: SelectionStrategy | None = None,
    ) -> None:
        if not entries:
            raise ValueError("router requires at least one entry")

        normalized: list[ProviderEntry] = []
        for entry in entries:
            if isinstance(entry, ProviderEntry):
                normalized.append(entry)
            else:
                normalized.append(
                    ProviderEntry(name=type(entry).__name__, provider=entry)
                )

        self.entries: list[ProviderEntry] = normalized
        self.strategy: SelectionStrategy = strategy or FirstAvailableStrategy()

    def register(
        self,
        provider: Provider,
        *,
        name: str | None = None,
        available: bool = True,
    ) -> None:
        """Append a new provider to the routing pool."""
        self.entries.append(
            ProviderEntry(
                name=name or type(provider).__name__,
                provider=provider,
                available=available,
            )
        )

    def set_availability(self, name: str, available: bool) -> None:
        """Toggle a provider's availability flag."""
        for entry in self.entries:
            if entry.name == name:
                entry.available = available
                return
        raise KeyError(f"unknown provider: {name}")

    def select(self) -> ProviderEntry:
        """Return the next provider entry to use."""
        return self.strategy.select(self.entries)

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        """Run completion, falling back according to the configured strategy."""
        last_error: BaseException | None = None
        tried: set[str] = set()

        while True:
            try:
                entry = self.strategy.select(self.entries)
            except ProviderUnavailable as exc:
                if last_error is not None:
                    raise RouterError(str(exc)) from last_error
                raise

            if entry.name in tried:
                # Strategy returned an already-failed provider; stop.
                raise RouterError(
                    f"strategy yielded a previously-failed provider: {entry.name}"
                )
            tried.add(entry.name)

            try:
                return await entry.provider.complete(messages, tools=tools)
            except Exception as exc:
                last_error = exc
                self.strategy.on_failure(entry, exc)
                # Continue with next provider.

    def __repr__(self) -> str:
        return (
            f"Router(entries={self.entries!r}, strategy={type(self.strategy).__name__})"
        )
