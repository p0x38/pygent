from __future__ import annotations

from collections.abc import Sequence

import pytest

from pygent.providers.base import Provider
from pygent.routing import (
    FallbackStrategy,
    FirstAvailableStrategy,
    ProviderEntry,
    ProviderUnavailable,
)
from pygent.types import Message, ModelResponse, ToolDefinition


class _StubProvider(Provider):
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls = 0

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls += 1
        return ModelResponse(content=f"{self.name}-{self.calls}")


def test_first_available_picks_first() -> None:
    strategy = FirstAvailableStrategy()
    entries = [
        ProviderEntry("a", _StubProvider("a")),
        ProviderEntry("b", _StubProvider("b")),
    ]
    assert strategy.select(entries).name == "a"


def test_first_available_skips_unavailable() -> None:
    strategy = FirstAvailableStrategy()
    entries = [
        ProviderEntry("a", _StubProvider("a"), available=False),
        ProviderEntry("b", _StubProvider("b")),
    ]
    assert strategy.select(entries).name == "b"


def test_first_available_raises_when_none_available() -> None:
    strategy = FirstAvailableStrategy()
    entries = [
        ProviderEntry("a", _StubProvider("a"), available=False),
    ]
    with pytest.raises(ProviderUnavailable):
        strategy.select(entries)


def test_fallback_cycles_through_providers() -> None:
    strategy = FallbackStrategy()
    a = _StubProvider("a")
    b = _StubProvider("b")
    c = _StubProvider("c")
    entries = [
        ProviderEntry("a", a),
        ProviderEntry("b", b),
        ProviderEntry("c", c),
    ]

    assert strategy.select(entries).name == "a"
    strategy.on_failure(entries[0], RuntimeError("boom"))
    assert strategy.select(entries).name == "b"
    strategy.on_failure(entries[1], RuntimeError("boom"))
    assert strategy.select(entries).name == "c"
    strategy.on_failure(entries[2], RuntimeError("boom"))
    with pytest.raises(ProviderUnavailable):
        strategy.select(entries)


def test_fallback_reset_returns_to_first() -> None:
    strategy = FallbackStrategy()
    entries = [
        ProviderEntry("a", _StubProvider("a")),
        ProviderEntry("b", _StubProvider("b")),
    ]
    strategy.on_failure(entries[0], RuntimeError("boom"))
    strategy.reset()
    assert strategy.select(entries).name == "a"
