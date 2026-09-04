from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchResult:
    """A provider-neutral web search result."""

    title: str
    url: str
    snippet: str = ""


class SearchProvider(ABC):
    """Interface implemented by web search providers."""

    @abstractmethod
    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        """Search the web and return normalized results."""
        raise NotImplementedError
