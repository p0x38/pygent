from __future__ import annotations

import httpx
import pytest

from pygent.exceptions import ToolError
from pygent.skills.browser import BrowserSkill
from pygent.tools import ToolRegistry


class _StubTransport(httpx.AsyncBaseTransport):
    def __init__(self, body: str, status_code: int = 200) -> None:
        self.body = body
        self.status_code = status_code

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=self.status_code,
            text=self.body,
            request=request,
        )


@pytest.mark.asyncio
async def test_open_url_fetches_page() -> None:
    transport = _StubTransport("hello world", status_code=200)
    client = httpx.AsyncClient(transport=transport)
    skill = BrowserSkill(client=client)

    result = await skill.open_url.execute({"url": "https://example.com/"})

    assert result["text"] == "hello world"
    assert result["status_code"] == 200


@pytest.mark.asyncio
async def test_open_url_rejects_non_http() -> None:
    skill = BrowserSkill()
    with pytest.raises(ToolError):
        await skill.open_url.execute({"url": "file:///etc/passwd"})


@pytest.mark.asyncio
async def test_find_text_requires_fetched_page() -> None:
    skill = BrowserSkill()
    with pytest.raises(ToolError):
        await skill.find_text.execute({"pattern": "x"})


@pytest.mark.asyncio
async def test_find_text_returns_matches() -> None:
    transport = _StubTransport("hello hello world")
    client = httpx.AsyncClient(transport=transport)
    skill = BrowserSkill(client=client)
    await skill.open_url.execute({"url": "https://example.com/"})

    matches = await skill.find_text.execute({"pattern": "hello", "limit": 5})

    assert [m["match"] for m in matches] == ["hello", "hello"]
    assert skill.find_text.last_text == "hello hello world"


def test_browser_skill_registers_tools() -> None:
    registry = ToolRegistry()
    skill = BrowserSkill()
    skill.register_into(registry)

    names = {t.definition.name for t in registry}
    assert names == {"open_url", "find_text"}
