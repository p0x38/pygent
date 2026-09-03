from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentContext:
    """Per-run context available to the agent and its tools."""

    metadata: dict[str, Any] = field(default_factory=dict)
