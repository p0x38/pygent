from __future__ import annotations

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


class FakeEntryPoint:
    name = "example"

    def load(self) -> object:
        return ExamplePlugin()


def test_load_syntax_plugins_from_entry_points() -> None:
    entry_point = FakeEntryPoint()

    registry = SyntaxRegistry()
    loaded = load_syntax_plugins(registry, plugins=[entry_point])

    assert len(loaded) == 1
    assert isinstance(loaded[0], ExamplePlugin)
    handler = registry.get("#")
    assert handler is not None
    assert handler.name == "example"
