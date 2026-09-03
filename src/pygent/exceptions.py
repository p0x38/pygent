from __future__ import annotations


class PygentError(Exception):
    """Base exception for Pygent errors."""


class AgentLoopError(PygentError):
    """Raised when an agent cannot complete its interaction loop."""

    def __init__(self, message: str, *, iterations: int) -> None:
        super().__init__(message)
        self.iterations = iterations


class ProviderError(PygentError):
    """Base exception for provider-related failures."""


class ProviderConnectionError(ProviderError):
    """Raised when a provider cannot be reached."""


class ProviderAuthenticationError(ProviderError):
    """Raised when a provider rejects the supplied credentials."""


class ProviderRateLimitError(ProviderError):
    """Raised when a provider enforces a rate limit."""


class ProviderRequestError(ProviderError):
    """Raised for malformed or rejected requests."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an unexpected or unparsable response."""


class RouterError(PygentError):
    """Base exception for routing failures."""


class ToolError(PygentError):
    """Base exception for tool-related failures."""


class ToolTimeoutError(ToolError):
    """Raised when a tool exceeds its allotted time."""
