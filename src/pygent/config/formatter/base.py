"""Base configuration formatter."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ConfigFormatter(ABC):
    """Base class for configuration formatters."""

    @abstractmethod
    def format(self, config: Any) -> str:
        """Format configuration into a string."""
        raise NotImplementedError
