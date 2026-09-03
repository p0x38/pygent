from __future__ import annotations

from typing import Any

import pytest

from pygent.exceptions import ToolError
from pygent.skills.web_search import (
    SearchResult,
    WebSearchSkill,
    WebSearchTool,
    normalize_results,
)
from pygent.tools import ToolRegistry


class _FakeProvider:
    def __init__(self, results: list[dict[str, Any]] | Exception) -> None:
        self.results = results
        self.calls: list[tuple[str, int]] = []

    async def search(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        self.calls.append((query, limit))
        if isinstance(self.results, Exception):
            raise self.results
        return list(self.results)


def test_normalize_results() -> None:
    raw = [
        {"title": "t1", "href": "https://a.example", "body": "snippet 1"},
        {"title": "t2", "url": "https://b.example", "snippet": "snippet 2"},
    ]
    results = normalize_results(raw)
    assert results == [
        SearchResult(title="t1", url="https://a.example", snippet="snippet 1"),
        SearchResult(title="t2", url="https://b.example", snippet="snippet 2"),
    ]


@pytest.mark.asyncio
async def test_web_search_tool_returns_results() -> None:
    provider = _FakeProvider([{"title": "t", "href": "https://a", "body": "b"}])
    tool = WebSearchTool(provider=provider, default_limit=3)

    result = await tool.execute({"query": "pygent"})

    assert result == [{"title": "t", "url": "https://a", "snippet": "b"}]
    assert provider.calls == [("pygent", 3)]


@pytest.mark.asyncio
async def test_web_search_tool_rejects_empty_query() -> None:
    tool = WebSearchTool(provider=_FakeProvider([]))
    with pytest.raises(ToolError):
        await tool.execute({"query": "  "})


@pytest.mark.asyncio
async def test_web_search_tool_propagates_provider_error() -> None:
    provider = _FakeProvider(RuntimeError("boom"))
    tool = WebSearchTool(provider=provider)
    with pytest.raises(ToolError):
        await tool.execute({"query": "pygent"})


def test_web_search_skill_registers_tool() -> None:
    provider = _FakeProvider([])
    skill = WebSearchSkill(provider=provider)
    registry = ToolRegistry()

    tool = skill.register_into(registry)

    assert tool is skill.tool
    assert "web_search" in [t.definition.name for t in registry]


def test_web_search_tool_rejects_invalid_default_limit() -> None:
    with pytest.raises(ValueError):
        WebSearchTool(default_limit=0)
