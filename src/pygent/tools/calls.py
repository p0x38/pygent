from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pygent.tools.registry import ToolRegistry
from pygent.tools.result import ToolResult
from pygent.types import ToolCall


async def execute_tool_call(
    registry: ToolRegistry,
    call: ToolCall,
) -> ToolResult:
    """Execute one model-issued tool call and normalize its result."""
    tool = registry.get(call.name)

    try:
        content = await tool.execute(call.arguments)
    except Exception as exc:
        return ToolResult(
            tool_call_id=call.id,
            name=call.name,
            content=str(exc),
            is_error=True,
        )

    return ToolResult(
        tool_call_id=call.id,
        name=call.name,
        content=content,
    )
