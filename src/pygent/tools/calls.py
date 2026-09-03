from __future__ import annotations

from typing import Any

from pygent.tools.registry import ToolRegistry
from pygent.types import ToolCall


async def execute_tool_call(
    registry: ToolRegistry,
    call: ToolCall,
) -> Any:
    """Execute one model-issued tool call through a registry."""
    tool = registry.get(call.name)
    return await tool.execute(call.arguments)
