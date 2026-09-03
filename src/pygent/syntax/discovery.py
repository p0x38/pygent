"""External syntax plugin discovery for Pygent."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from importlib.metadata import EntryPoint, entry_points
from typing import Protocol, cast

from pygent.syntax.plugins import SyntaxPlugin
from pygent.syntax.registry import SyntaxRegistry

ENTRY_POINT_GROUP = "pygent.syntax"


class _EntryPoint(Protocol):
    """Minimal entry-point interface required by the loader."""

    name: str

    def load(self) -> object:
        """Load the object exposed by the entry point."""
        ...


def _load_plugin(entry_point: _EntryPoint) -> SyntaxPlugin:
    """Load and validate a syntax plugin from an entry point."""
    plugin: object = entry_point.load()

    if not hasattr(plugin, "register_syntax") and callable(plugin):
        factory = cast(Callable[[], object], plugin)
        plugin = factory()

    if not hasattr(plugin, "register_syntax"):
        raise TypeError(
            f"Syntax entry point {entry_point.name!r} does not provide "
            "a register_syntax() method"
        )

    return cast(SyntaxPlugin, plugin)


def discover_syntax_plugins(
    *,
    group: str = ENTRY_POINT_GROUP,
) -> tuple[EntryPoint, ...]:
    """Return installed syntax plugin entry points."""
    return tuple(entry_points(group=group))


def load_syntax_plugins(
    registry: SyntaxRegistry,
    *,
    group: str = ENTRY_POINT_GROUP,
    plugins: Iterable[_EntryPoint] | None = None,
) -> tuple[SyntaxPlugin, ...]:
    """Load and register external syntax plugins.

    Args:
        registry: Registry receiving discovered plugins.
        group: Entry-point group to discover.
        plugins: Optional entry points, primarily useful for testing.

    Returns:
        The loaded plugin objects in discovery order.
    """
    entry_point_list = (
        tuple(plugins) if plugins is not None else discover_syntax_plugins(group=group)
    )
    loaded: list[SyntaxPlugin] = []

    for entry_point in entry_point_list:
        plugin = _load_plugin(entry_point)
        plugin.register_syntax(registry)
        loaded.append(plugin)

    return tuple(loaded)


__all__ = [
    "ENTRY_POINT_GROUP",
    "discover_syntax_plugins",
    "load_syntax_plugins",
]
