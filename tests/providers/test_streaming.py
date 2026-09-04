from __future__ import annotations

import pytest

from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse


class _Provider(Provider):
    async def complete(self, messages: list[Message], *, tools=()) -> ModelResponse:
        return ModelResponse(content="complete")


@pytest.mark.asyncio
async def test_provider_stream_defaults_to_complete() -> None:
    provider = _Provider()
    events = [event async for event in provider.stream([Message(role="user", content="hi")])]
    assert events == [ModelResponse(content="complete")]
