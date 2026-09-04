from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from pygent.types.usage import Usage

Role = Literal["system", "user", "assistant", "tool"]


def _tool_call_list_factory() -> list[ToolCall]:
    return []


class ToolCall(BaseModel):
    """A request from a model to execute a registered tool."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    """A provider-neutral conversation message."""

    model_config = ConfigDict(extra="forbid")

    role: Role
    content: str | None = None
    name: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=_tool_call_list_factory)
    tool_call_id: str | None = None


class ModelResponse(BaseModel):
    """A provider-neutral response returned by an LLM."""

    model_config = ConfigDict(extra="forbid")

    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=_tool_call_list_factory)
    finish_reason: str | None = None
    usage: Usage | None = None
