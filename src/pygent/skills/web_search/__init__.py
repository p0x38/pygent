"""Web search skill."""

from pygent.skills.web_search.providers.ddgs import (
    DDGSSearchProvider,
    SearchProvider,
    SearchResult,
    normalize_results,
)
from pygent.skills.web_search.skill import WebSearchSkill, WebSearchTool

__all__ = [
    "DDGSSearchProvider",
    "SearchProvider",
    "SearchResult",
    "WebSearchSkill",
    "WebSearchTool",
    "normalize_results",
]
