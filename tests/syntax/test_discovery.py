from __future__ import annotations

from importlib.metadata import EntryPoint

from pygent.syntax import (
    SyntaxContext,
    SyntaxHandler,
    SyntaxRegistry,
    SyntaxResult,
    load_syntax_plugins,
)


class ExamplePlugin:
    def register_syntax(self, registry: SyntaxRegistry) -> None:
        registry.register(ExampleHandler())


class ExampleHandler(SyntaxHandler):
    name = "example"
    prefix = "#"

    async def handle(
        self,
        value: str,
        context: SyntaxContext,
    ) -> SyntaxResult:
        return SyntaxResult(text=value)


def test_load_syntax_plugins_from_entry_points() -> None:
    entry_point = EntryPoint(
        name="example",
        value="tests.syntax.test_discovery:ExamplePlugin",
        group="pygent.syntax",
    )

    registry = SyntaxRegistry()
    loaded = load_syntax_plugins(registry, plugins=[entry_point])

    assert len(loaded) == 1
    assert isinstance(loaded[0], ExamplePlugin)
    assert registry.get("#").name == "example"
