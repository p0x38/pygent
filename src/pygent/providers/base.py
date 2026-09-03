from __future__ import annotations

from abc import ABC, abstractmethod


class Provider(ABC):
    """Base interface implemented by LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response for a prompt."""
        raise NotImplementedError
