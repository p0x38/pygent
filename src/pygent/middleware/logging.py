from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from pygent.middleware.base import Middleware
from pygent.types import Message, ModelResponse, ToolDefinition

logger = logging.getLogger("pygent.middleware.logging")


class LoggingMiddleware(Middleware):
    """Log the start and end of each completion call."""

    def __init__(self, *, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("pygent.middleware.logging")

    async def complete(
        self,
        call: Callable[..., Awaitable[ModelResponse]],
        messages: list[Message],
        *,
        tools: list[ToolDefinition],
    ) -> ModelResponse:
        self.logger.info(
            "completion.start",
            extra={"messages": len(messages), "tools": len(tools)},
        )
        try:
            response = await call(messages, tools=tools)
        except Exception as exc:
            self.logger.exception("completion.error: %s", exc)
            raise
        self.logger.info(
            "completion.end",
            extra={"finish_reason": response.finish_reason},
        )
        return response
