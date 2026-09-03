from __future__ import annotations

import pytest

from pygent.exceptions import RouterError
from pygent.providers.base import Provider
from pygent.routing import (
    FallbackStrategy,
    ProviderEntry,
    Router,
)
from pygent.types import Message, ModelResponse, ToolDefinition


class _StubProvider(Provider):
    def __init__(
        self,
        content: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.content = content
        self.error = error
        self.calls = 0

    async def complete(
        self,
        messages: list[Message],
        *,
        tools: list[ToolDefinition] = (),
    ) -> ModelResponse:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return ModelResponse(content=self.content or "")


@pytest.mark.asyncio
async def test_router_picks_first_provider() -> None:
    a = _StubProvider(content="hello")
    b = _StubProvider(content="world")
    router = Router(
        [
            ProviderEntry("a", a),
            ProviderEntry("b", b),
        ]
    )

    response = await router.complete([Message(role="user", content="hi")])

    assert response.content == "hello"
    assert a.calls == 1
    assert b.calls == 0


@pytest.mark.asyncio
async def test_router_falls_back_on_failure() -> None:
    a = _StubProvider(error=RuntimeError("first failed"))
    b = _StubProvider(content="fallback")
    router = Router(
        [
            ProviderEntry("a", a),
            ProviderEntry("b", b),
        ],
        strategy=FallbackStrategy(),
    )

    response = await router.complete([Message(role="user", content="hi")])

    assert response.content == "fallback"
    assert a.calls == 1
    assert b.calls == 1


@pytest.mark.asyncio
async def test_router_raises_when_all_providers_fail() -> None:
    a = _StubProvider(error=RuntimeError("boom"))
    b = _StubProvider(error=RuntimeError("boom"))
    router = Router(
        [
            ProviderEntry("a", a),
            ProviderEntry("b", b),
        ],
        strategy=FallbackStrategy(),
    )

    with pytest.raises(RouterError):
        await router.complete([Message(role="user", content="hi")])


def test_router_register_and_availability() -> None:
    router = Router([ProviderEntry("primary", _StubProvider("a"))])
    router.set_availability("primary", False)

    assert router.entries[0].available is False

    router.register(_StubProvider("b"), name="secondary")
    assert router.entries[1].name == "secondary"
    assert router.entries[1].available is True


def test_router_rejects_empty_entries() -> None:
    with pytest.raises(ValueError, match="at least one entry"):
        Router([])
