from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from pygent.types import ModelResponse, ToolCall

EventType = Literal[
    "iteration_start",
    "text_delta",
    "tool_call_delta",
    "tool_result",
    "iteration_end",
    "completion",
    "error",
]


class AgentEvent(BaseModel):
    """Streaming event emitted by :class:`AgentLoop.stream`."""

    model_config = ConfigDict(extra="forbid")

    type: EventType
    iteration: int | None = None
    text_delta: str | None = None
    tool_call: ToolCall | None = None
    tool_result: dict[str, Any] | None = None
    response: ModelResponse | None = None
    error: str | None = None
