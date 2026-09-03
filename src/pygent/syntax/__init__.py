"""Extensible conversational syntax for Pygent."""

from pygent.syntax.base import SyntaxContext, SyntaxHandler, SyntaxResult
from pygent.syntax.discovery import (
    ENTRY_POINT_GROUP,
    discover_syntax_plugins,
    load_syntax_plugins,
)
from pygent.syntax.parser import ParsedInput, SyntaxInvocation, SyntaxParser
from pygent.syntax.plugins import SyntaxPlugin, inject_syntax_plugin
from pygent.syntax.registry import SyntaxRegistry

__all__ = [
    "ENTRY_POINT_GROUP",
    "ParsedInput",
    "SyntaxContext",
    "SyntaxHandler",
    "SyntaxInvocation",
    "SyntaxParser",
    "SyntaxPlugin",
    "SyntaxRegistry",
    "SyntaxResult",
    "discover_syntax_plugins",
    "inject_syntax_plugin",
    "load_syntax_plugins",
]
