"""Search providers for the web search skill."""

from pygent.skills.web_search.providers.ddgs import (
    DDGSSearchProvider,
    SearchProvider,
    SearchResult,
    normalize_results,
)

__all__ = [
    "DDGSSearchProvider",
    "SearchProvider",
    "SearchResult",
    "normalize_results",
]
