from __future__ import annotations

from dataclasses import dataclass, field


def _metadata_factory() -> dict[str, object]:
    return {}


@dataclass(slots=True)
class AgentContext:
    """Per-run context available to the agent and its tools."""

    metadata: dict[str, object] = field(default_factory=_metadata_factory)
