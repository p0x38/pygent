from __future__ import annotations

import json

import httpx
import pytest

from pygent.providers.openrouter import OpenRouterProvider
from pygent.types import Message


class _StubTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.request: httpx.Request | None = None

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request = request
        return httpx.Response(
            status_code=200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "ok",
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
            request=request,
        )


@pytest.mark.asyncio
async def test_sends_default_headers_and_extra_body() -> None:
    transport = _StubTransport()
    client = httpx.AsyncClient(
        transport=transport,
        base_url="https://openrouter.ai/api/v1",
        headers={
            "Authorization": "Bearer sk-or-v1",
            "X-Title": "Pygent",
        },
    )
    provider = OpenRouterProvider(
        "openai/gpt-4o-mini",
        api_key="sk-or-v1",
        extra_body={"transforms": ["middle-out"]},
        client=client,
    )

    await provider.complete([Message(role="user", content="hi")])

    assert transport.request is not None
    assert str(transport.request.url) == "https://openrouter.ai/api/v1/chat/completions"
    assert transport.request.headers.get("authorization") == "Bearer sk-or-v1"
    assert transport.request.headers.get("http-referer") is None
    assert transport.request.headers.get("x-title") == "Pygent"
    payload = json.loads(transport.request.content)
    assert payload["transforms"] == ["middle-out"]


def test_reads_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    provider = OpenRouterProvider("openai/gpt-4o-mini")
    assert provider.api_key == "env-key"
