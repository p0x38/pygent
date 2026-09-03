from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from pygent.agent.context import AgentContext
from pygent.exceptions import ToolTimeoutError
from pygent.types import ToolDefinition


class Tool(ABC):
    """Base interface for a callable agent tool."""

    timeout: float | None = None

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Return the provider-neutral tool definition."""
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> Any:
        """Execute the tool with model-supplied arguments."""
        raise NotImplementedError

    async def execute_with_timeout(
        self,
        arguments: Mapping[str, Any],
        *,
        context: AgentContext | None = None,
    ) -> Any:
        """Run :meth:`execute` honouring the tool's ``timeout`` setting."""
        if self.timeout is None:
            return await self.execute(arguments, context=context)
        try:
            return await asyncio.wait_for(
                self.execute(arguments, context=context), timeout=self.timeout
            )
        except TimeoutError as exc:
            raise ToolTimeoutError(
                f"tool {self.definition.name!r} exceeded timeout "
                f"of {self.timeout} seconds"
            ) from exc
