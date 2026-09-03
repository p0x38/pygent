"""Parsing primitives for extensible Pygent syntax."""

from __future__ import annotations

from dataclasses import dataclass

from pygent.syntax.registry import SyntaxRegistry


@dataclass(slots=True, frozen=True)
class SyntaxInvocation:
    """A syntax expression found in user input."""

    handler_name: str
    prefix: str
    value: str
    start: int
    end: int


@dataclass(slots=True, frozen=True)
class ParsedInput:
    """User input split into ordinary text and syntax invocations."""

    text: str
    invocations: tuple[SyntaxInvocation, ...]


class SyntaxParser:
    """Parse registered syntax without knowing what individual handlers do."""

    def __init__(self, registry: SyntaxRegistry) -> None:
        self.registry = registry

    def parse(self, text: str) -> ParsedInput:
        """Parse syntax expressions from ``text``.

        A syntax expression starts at a token boundary. Its value continues
        until the next whitespace character. Handlers may impose additional
        restrictions in their own implementation.
        """
        invocations: list[SyntaxInvocation] = []
        spans: list[tuple[int, int]] = []

        for index, character in enumerate(text):
            if index and not text[index - 1].isspace():
                continue

            handler = self.registry.get(character)
            if handler is None:
                continue

            end = index + 1
            while end < len(text) and not text[end].isspace():
                end += 1

            value = text[index + 1 : end]
            if not value:
                continue

            invocations.append(
                SyntaxInvocation(
                    handler_name=handler.name,
                    prefix=handler.prefix,
                    value=value,
                    start=index,
                    end=end,
                )
            )
            spans.append((index, end))

        if not spans:
            return ParsedInput(text=text, invocations=())

        parts: list[str] = []
        cursor = 0
        for start, end in spans:
            parts.append(text[cursor:start])
            cursor = end
        parts.append(text[cursor:])

        return ParsedInput(
            text="".join(parts).strip(),
            invocations=tuple(invocations),
        )
