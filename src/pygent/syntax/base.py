"""Base types for extensible Pygent syntax."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


def _metadata_factory() -> dict[str, object]:
    return {}


@dataclass(slots=True)
class SyntaxContext:
    """Context supplied to a syntax handler."""

    metadata: dict[str, object] = field(default_factory=_metadata_factory)


@dataclass(slots=True, frozen=True)
class SyntaxResult:
    """Result produced by a syntax handler."""

    text: str = ""
    handled: bool = True
    metadata: dict[str, object] = field(default_factory=_metadata_factory)


class SyntaxHandler(ABC):
    """Base class for an injectable conversational syntax handler."""

    name: str
    prefix: str
    consume_rest: bool = False

    @abstractmethod
    async def handle(
        self,
        value: str,
        context: SyntaxContext,
    ) -> SyntaxResult:
        """Handle a syntax expression."""
        raise NotImplementedError
