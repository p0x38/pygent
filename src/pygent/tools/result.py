from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ToolResult(BaseModel):
    """Normalized result of a tool invocation."""

    model_config = ConfigDict(extra="forbid")

    tool_call_id: str
    name: str
    content: Any
    is_error: bool = False
