from __future__ import annotations


class PygentError(Exception):
    """Base exception for Pygent errors."""


class AgentLoopError(PygentError):
    """Raised when an agent cannot complete its interaction loop."""

    def __init__(self, message: str, *, iterations: int) -> None:
        super().__init__(message)
        self.iterations = iterations
