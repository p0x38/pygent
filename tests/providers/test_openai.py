from __future__ import annotations

import httpx
import pytest

from pygent.providers.openai import OpenAIProvider


class _StubTransport(httpx.AsyncBaseTransport):
    def __init__(self, body: dict[str, object]) -> None:
        self.body = body
        self.request: httpx.Request | None = None

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request = request
        return httpx.Response(
            status_code=200,
            json=self.body,
            request=request,
        )


@pytest.mark.asyncio
async def test_uses_default_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    transport = _StubTransport(
        {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "hi"},
                    "finish_reason": "stop",
                }
            ]
        }
    )
    client = httpx.AsyncClient(
        transport=transport,
        base_url="https://api.openai.com/v1",
        headers={"Authorization": "Bearer key"},
    )
    provider = OpenAIProvider("gpt-test", api_key="key", client=client)

    await provider.complete(
        [
            __import__("pygent.types", fromlist=["Message"]).Message(
                role="user", content="hi"
            )
        ]
    )

    assert transport.request is not None
    assert str(transport.request.url) == "https://api.openai.com/v1/chat/completions"
    assert transport.request.headers.get("authorization") == "Bearer key"


def test_reads_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    provider = OpenAIProvider("m")
    assert provider.api_key == "env-key"
