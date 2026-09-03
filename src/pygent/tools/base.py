from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from pygent.types import ToolDefinition


class Tool(ABC):
    """Base interface for a callable agent tool."""

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Return the provider-neutral tool definition."""
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        arguments: Mapping[str, Any],
    ) -> Any:
        """Execute the tool with model-supplied arguments."""
        raise NotImplementedError
