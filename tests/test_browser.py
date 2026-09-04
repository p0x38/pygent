from __future__ import annotations

import re

import httpx
import pytest

from pygent.browser import Browser


@pytest.mark.asyncio
async def test_browser_fetches_and_follows_redirects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/redirect":
            return httpx.Response(302, headers={"Location": "/page"})
        return httpx.Response(200, text="hello", headers={"content-type": "text/plain"})

    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient

    def client_factory(*args: object, **kwargs: object) -> httpx.AsyncClient:
        kwargs["transport"] = transport
        return original(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)
    page = await Browser().fetch("https://example.test/redirect")

    assert page.url == "https://example.test/page"
    assert page.content == "hello"
    assert page.status_code == 200


@pytest.mark.asyncio
async def test_browser_rejects_non_http_url() -> None:
    with pytest.raises(ValueError, match=re.escape("HTTP(S)")):
        await Browser().fetch("ftp://example.test/file")


@pytest.mark.asyncio
async def test_browser_enforces_response_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(200, content=b"12345"))
    original = httpx.AsyncClient

    def client_factory(*args: object, **kwargs: object) -> httpx.AsyncClient:
        kwargs["transport"] = transport
        return original(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)

    with pytest.raises(ValueError, match="max_bytes"):
        await Browser(max_bytes=4).fetch("https://example.test/page")
