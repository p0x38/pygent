"""Registry for injectable Pygent syntax handlers."""

from __future__ import annotations

from collections.abc import Iterable

from pygent.syntax.base import SyntaxHandler


class SyntaxRegistry:
    """Register and resolve syntax handlers by prefix."""

    def __init__(self, handlers: Iterable[SyntaxHandler] = ()) -> None:
        self._handlers: dict[str, SyntaxHandler] = {}
        for handler in handlers:
            self.register(handler)

    def register(self, handler: SyntaxHandler, *, replace: bool = False) -> None:
        """Register a handler.

        Args:
            handler: Handler to register.
            replace: Replace an existing handler using the same prefix.
        """
        if not handler.name:
            raise ValueError("Syntax handler name cannot be empty")
        if not handler.prefix:
            raise ValueError("Syntax handler prefix cannot be empty")
        if handler.prefix in self._handlers and not replace:
            raise ValueError(
                f"Syntax prefix already registered: {handler.prefix!r}"
            )
        self._handlers[handler.prefix] = handler

    def unregister(self, prefix: str) -> SyntaxHandler | None:
        """Remove and return the handler for ``prefix``."""
        return self._handlers.pop(prefix, None)

    def get(self, prefix: str) -> SyntaxHandler | None:
        """Return the handler for ``prefix`` if registered."""
        return self._handlers.get(prefix)

    def __iter__(self):
        return iter(self._handlers.values())

    def __len__(self) -> int:
        return len(self._handlers)
