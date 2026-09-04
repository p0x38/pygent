"""Execution helpers for parsed Pygent syntax."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pygent.syntax.base import SyntaxContext, SyntaxResult
from pygent.syntax.parser import ParsedInput, SyntaxParser
from pygent.syntax.registry import SyntaxRegistry


@dataclass(slots=True)
class ProcessedInput:
    """Input after syntax handlers have processed its invocations."""

    text: str
    results: tuple[SyntaxResult, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


class SyntaxProcessor:
    """Parse and execute registered syntax handlers."""

    def __init__(self, registry: SyntaxRegistry) -> None:
        self.registry = registry
        self.parser = SyntaxParser(registry)

    async def process(
        self,
        text: str,
        *,
        context: SyntaxContext | None = None,
    ) -> ProcessedInput:
        """Process syntax invocations and return cleaned user text."""
        parsed: ParsedInput = self.parser.parse(text)
        syntax_context = context or SyntaxContext()
        results: list[SyntaxResult] = []

        for invocation in parsed.invocations:
            handler = self.registry.get(invocation.prefix)
            if handler is None:
                continue
            result = await handler.handle(invocation.value, syntax_context)
            results.append(result)

        metadata: dict[str, Any] = dict(syntax_context.metadata)
        metadata["syntax"] = [result.metadata for result in results]

        return ProcessedInput(
            text=parsed.text,
            results=tuple(results),
            metadata=metadata,
        )


__all__ = ["ProcessedInput", "SyntaxProcessor"]
