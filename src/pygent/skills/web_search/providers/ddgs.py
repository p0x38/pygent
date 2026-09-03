from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class SearchProvider(Protocol):
    """Pluggable backend for the :class:`WebSearchSkill`."""

    async def search(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        """Return a list of raw search result dictionaries."""
        raise NotImplementedError


@dataclass(slots=True)
class SearchResult:
    """Normalized web search result."""

    title: str
    url: str
    snippet: str


class DDGSSearchProvider:
    """Search provider backed by the optional ``duckduckgo_search`` package."""

    def __init__(self, *, client: Any | None = None) -> None:
        if client is None:
            try:
                from duckduckgo_search import DDGS  # type: ignore[import-not-found]
            except ImportError as exc:
                raise ImportError(
                    "DDGS support requires 'duckduckgo-search' (or pass a client)."
                ) from exc
            client = DDGS()
        self.client = client

    async def search(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for entry in self.client.text(query, max_results=limit):
            results.append(
                {
                    "title": entry.get("title", ""),
                    "href": entry.get("href", ""),
                    "body": entry.get("body", ""),
                }
            )
        return results


def normalize_results(
    entries: list[dict[str, Any]],
) -> list[SearchResult]:
    """Convert raw DDGS-style dictionaries into :class:`SearchResult`."""
    results: list[SearchResult] = []
    for entry in entries:
        results.append(
            SearchResult(
                title=str(entry.get("title", "")),
                url=str(entry.get("href") or entry.get("url") or ""),
                snippet=str(entry.get("body") or entry.get("snippet") or ""),
            )
        )
    return results
