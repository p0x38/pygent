"""Provider-neutral web search abstractions."""

from pygent.search.base import SearchProvider, SearchResult
from pygent.search.duckduckgo import DuckDuckGoSearch

__all__ = ["DuckDuckGoSearch", "SearchProvider", "SearchResult"]
