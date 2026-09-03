from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import httpx

from pygent.agent.context import AgentContext
from pygent.exceptions import ToolError
from pygent.tools.base import Tool
from pygent.types import ToolDefinition


class OpenURLTool(Tool):
    """Fetch the body of a URL and return the raw text."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        on_text: Any = None,
    ) -> None:
        self.client = client
        self._on_text = on_text

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="open_url",
            description="Fetch the content of a URL and return it as text.",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> dict[str, Any]:
        url = arguments.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ToolError("'url' must be an http(s) URL")

        client = self.client
        owned_client = False
        if client is None:
            client = httpx.AsyncClient(timeout=15.0)
            owned_client = True

        try:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            text = response.text
            if self._on_text is not None:
                self._on_text(str(response.url), text)
            return {
                "url": str(response.url),
                "status_code": response.status_code,
                "text": text,
            }
        except httpx.HTTPError as exc:
            raise ToolError(f"failed to fetch URL: {exc}") from exc
        finally:
            if owned_client:
                await client.aclose()


class FindTextTool(Tool):
    """Find occurrences of a substring within a previously fetched page."""

    def __init__(self) -> None:
        self.last_text: str | None = None
        self.last_url: str | None = None

    def set_text(self, url: str, text: str) -> None:
        self.last_url = url
        self.last_text = text

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="find_text",
            description="Find occurrences of a substring on the last fetched page.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["pattern"],
                "additionalProperties": False,
            },
        )

    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> list[dict[str, Any]]:
        if self.last_text is None:
            raise ToolError("no page has been fetched yet")

        pattern = arguments.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            raise ToolError("'pattern' must be a non-empty string")
        limit = arguments.get("limit", 10)
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise ToolError("'limit' must be an integer")
        if limit < 1:
            raise ToolError("'limit' must be at least 1")

        matches = [
            {"match": match.group(0), "start": match.start()}
            for match in re.finditer(re.escape(pattern), self.last_text)
        ]
        return matches[:limit]
