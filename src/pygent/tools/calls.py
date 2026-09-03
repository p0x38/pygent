from __future__ import annotations

from pygent.tools.registry import ToolRegistry
from pygent.tools.result import ToolResult
from pygent.types import ToolCall


async def execute_tool_call(
    registry: ToolRegistry,
    call: ToolCall,
) -> ToolResult:
    """Execute one model-issued tool call and normalize its result."""
    try:
        tool = registry.get(call.name)
        content = await tool.execute(call.arguments)
    except KeyError as exc:
        return ToolResult(
            tool_call_id=call.id,
            name=call.name,
            content=exc.args[0] if exc.args else str(exc),
            is_error=True,
        )
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
