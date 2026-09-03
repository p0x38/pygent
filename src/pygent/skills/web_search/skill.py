from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pygent.agent.context import AgentContext
from pygent.exceptions import ToolError
from pygent.skills.web_search.providers.ddgs import (
    DDGSSearchProvider,
    SearchProvider,
    SearchResult,
    normalize_results,
)
from pygent.tools.base import Tool
from pygent.types import ToolDefinition


class WebSearchTool(Tool):
    """Tool that performs a web search and returns a list of normalized hits."""

    DEFAULT_LIMIT = 5
    MAX_LIMIT = 20

    def __init__(
        self,
        *,
        provider: SearchProvider | None = None,
        default_limit: int = DEFAULT_LIMIT,
    ) -> None:
        if default_limit < 1 or default_limit > self.MAX_LIMIT:
            raise ValueError(f"default_limit must be between 1 and {self.MAX_LIMIT}")
        self._provider: SearchProvider = provider or DDGSSearchProvider()
        self._default_limit = default_limit

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="web_search",
            description="Search the web for a query and return top results.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> list[dict[str, Any]]:
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ToolError("'query' must be a non-empty string")

        limit = arguments.get("limit", self._default_limit)
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise ToolError("'limit' must be an integer")
        if limit < 1 or limit > self.MAX_LIMIT:
            raise ToolError(f"'limit' must be between 1 and {self.MAX_LIMIT}")

        try:
            raw = await self._provider.search(query, limit=limit)
        except ImportError as exc:
            raise ToolError(str(exc)) from exc
        except Exception as exc:
            raise ToolError(f"search failed: {exc}") from exc

        results: list[SearchResult] = normalize_results(raw)
        return [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in results]


class WebSearchSkill:
    """Bundle of web search tools ready to register with a :class:`ToolRegistry`."""

    def __init__(self, *, provider: SearchProvider | None = None) -> None:
        self.tool = WebSearchTool(provider=provider)

    def register_into(self, registry: Any) -> WebSearchTool:
        registry.register(self.tool)
        return self.tool
