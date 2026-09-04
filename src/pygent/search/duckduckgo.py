from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import quote_plus

import httpx

from pygent.search.base import SearchProvider, SearchResult


class _ResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[SearchResult] = []
        self._title = ""
        self._url = ""
        self._snippet = ""
        self._in_title = False
        self._in_snippet = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "a" and "result__a" in classes:
            self._title = ""
            self._url = attributes.get("href") or ""
            self._in_title = True
        elif "result__snippet" in classes:
            self._snippet = ""
            self._in_snippet = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_title:
            self._in_title = False
        if self._in_snippet and tag in {"a", "div"}:
            self._in_snippet = False
            if self._title and self._url:
                self.results.append(
                    SearchResult(
                        title=self._title.strip(),
                        url=self._url,
                        snippet=self._snippet.strip(),
                    )
                )

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title += data
        elif self._in_snippet:
            self._snippet += data


class DuckDuckGoSearch(SearchProvider):
    """Search DuckDuckGo's HTML endpoint without requiring an API key."""

    endpoint = "https://html.duckduckgo.com/html/"

    def __init__(self, *, timeout: float = 10.0) -> None:
        self.timeout = timeout

    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if limit < 1:
            raise ValueError("limit must be at least 1")

        url = f"{self.endpoint}?q={quote_plus(query)}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers={"User-Agent": "pygent/0.2"})
            response.raise_for_status()

        parser = _ResultParser()
        parser.feed(response.text)
        return parser.results[:limit]
