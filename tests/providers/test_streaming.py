from __future__ import annotations

from collections.abc import Sequence

import pytest

from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolDefinition


class _Provider(Provider):
    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        return ModelResponse(content="complete")


@pytest.mark.asyncio
async def test_provider_stream_defaults_to_complete() -> None:
    provider = _Provider()
    events = [
        event async for event in provider.stream([Message(role="user", content="hi")])
    ]
    assert events == [ModelResponse(content="complete")]
