from __future__ import annotations

from pygent.syntax import SyntaxHandler, SyntaxParser, SyntaxRegistry


class MentionSyntax(SyntaxHandler):
    name = "mention"
    prefix = "@"

    async def handle(self, value, context):
        raise NotImplementedError


class CommandSyntax(SyntaxHandler):
    name = "command"
    prefix = "/"

    async def handle(self, value, context):
        raise NotImplementedError


class DoubleArrowSyntax(SyntaxHandler):
    name = "double-arrow"
    prefix = ">>"

    async def handle(self, value, context):
        raise NotImplementedError


def test_parser_extracts_registered_syntax() -> None:
    registry = SyntaxRegistry([MentionSyntax(), CommandSyntax()])
    parsed = SyntaxParser(registry).parse("hello @file:main.py /help world")

    assert parsed.text == "hello   world"
    assert [(item.prefix, item.value) for item in parsed.invocations] == [
        ("@", "file:main.py"),
        ("/", "help"),
    ]


def test_parser_supports_multi_character_prefixes() -> None:
    registry = SyntaxRegistry([DoubleArrowSyntax(), MentionSyntax()])
    parsed = SyntaxParser(registry).parse(">>task @agent:coder")

    assert [(item.prefix, item.value) for item in parsed.invocations] == [
        (">>", "task"),
        ("@", "agent:coder"),
    ]


def test_unregistered_prefix_is_plain_text() -> None:
    registry = SyntaxRegistry([MentionSyntax()])
    parsed = SyntaxParser(registry).parse("hello /help")

    assert parsed.text == "hello /help"
    assert parsed.invocations == ()


def test_registry_rejects_duplicate_prefixes() -> None:
    registry = SyntaxRegistry([MentionSyntax()])

    try:
        registry.register(MentionSyntax())
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("Expected duplicate prefix to be rejected")
