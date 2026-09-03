from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from pygent.tools import Tool, ToolRegistry
from pygent.types import ToolDefinition


class DummyTool(Tool):
    def __init__(self, name: str = "dummy") -> None:
        self._definition = ToolDefinition(
            name=name,
            description="A test tool.",
        )

    @property
    def definition(self) -> ToolDefinition:
        return self._definition

    async def execute(self, arguments: Mapping[str, Any]) -> Any:
        return arguments


def test_register_and_get_tool() -> None:
    registry = ToolRegistry()
    tool = DummyTool()

    registry.register(tool)

    assert len(registry) == 1
    assert registry.get("dummy") is tool
    assert registry.definitions() == [tool.definition]


def test_duplicate_registration_raises() -> None:
    registry = ToolRegistry()
    registry.register(DummyTool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(DummyTool())


def test_unregister_returns_tool() -> None:
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register(tool)

    assert registry.unregister("dummy") is tool
    assert len(registry) == 0


def test_missing_tool_raises() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="Unknown tool: missing"):
        registry.get("missing")

    with pytest.raises(KeyError, match="Unknown tool: missing"):
        registry.unregister("missing")
