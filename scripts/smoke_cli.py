"""Smoke test for the CLI example, run with `uv run python scripts/smoke_cli.py`."""

from __future__ import annotations

import asyncio
import builtins
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.cli import _build_agent, _repl


class _ScriptedInput:
    """Replace ``input()`` with a scripted stream of answers."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = list(lines)
        self._index = 0

    def __call__(self, prompt: str = "") -> str:
        del prompt
        if self._index >= len(self._lines):
            raise EOFError
        line = self._lines[self._index]
        self._index += 1
        return line


def main() -> int:
    scripted_input = _ScriptedInput(
        ["hello", "how are you?", "/reset", "after reset", "/quit"]
    )
    output = io.StringIO()
    agent = _build_agent("echo")

    original_input = builtins.input
    original_stdout = sys.stdout
    sys.stdout = output
    builtins.input = scripted_input
    try:
        asyncio.run(_repl(agent))
    finally:
        sys.stdout = original_stdout
        builtins.input = original_input

    text = output.getvalue()
    assert "echo: hello" in text, text
    assert "echo: how are you?" in text, text
    assert "(memory cleared)" in text, text
    assert "echo: after reset" in text, text
    print("CLI smoke test passed:")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
