from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from pygent.search import SearchProvider, SearchResult
from pygent.search.duckduckgo import DuckDuckGoSearch


class _Provider(SearchProvider):
    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        return [SearchResult(title=query, url="https://example.com")][:limit]


def test_search_provider_contract() -> None:
    result = SearchResult(title="Example", url="https://example.com", snippet="demo")
    assert result.title == "Example"
    assert result.url == "https://example.com"
    assert result.snippet == "demo"


@pytest.mark.asyncio
async def test_search_provider_can_be_implemented() -> None:
    results = await _Provider().search("hello", limit=1)
    assert results == [SearchResult(title="hello", url="https://example.com")]


@pytest.mark.asyncio
async def test_duckduckgo_search_parses_results() -> None:
    html = """
    <a class="result__a" href="https://example.com">Example</a>
    <a class="result__snippet">A useful result</a>
    <a class="result__a" href="https://example.org">Second</a>
    <a class="result__snippet">Another result</a>
    """
    request = httpx.Request("GET", "https://html.duckduckgo.com/html/?q=test")
    response = httpx.Response(200, text=html, request=request)
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=response)):
        results = await DuckDuckGoSearch().search("test", limit=1)

    assert results == [
        SearchResult(
            title="Example",
            url="https://example.com",
            snippet="A useful result",
        )
    ]


@pytest.mark.asyncio
async def test_duckduckgo_search_validates_arguments() -> None:
    provider = DuckDuckGoSearch()
    with pytest.raises(ValueError, match="query"):
        await provider.search(" ")
    with pytest.raises(ValueError, match="limit"):
        await provider.search("test", limit=0)
