from __future__ import annotations

from typing import Any

import httpx

from pygent.skills.browser.tools import FindTextTool, OpenURLTool
from pygent.tools.registry import ToolRegistry


class BrowserSkill:
    """Bundle of browser-related tools."""

    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self.find_text = FindTextTool()
        self.open_url = OpenURLTool(client=client, on_text=self.find_text.set_text)

    def register_into(self, registry: ToolRegistry) -> dict[str, Any]:
        registry.register(self.open_url)
        registry.register(self.find_text)
        return {"open_url": self.open_url, "find_text": self.find_text}

    async def aclose(self) -> None:
        # Tools own their clients only when not provided externally; nothing to do
        # here for now, but kept for symmetry.
        return None
