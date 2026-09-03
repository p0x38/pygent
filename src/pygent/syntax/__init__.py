"""Extensible conversational syntax for Pygent."""

from pygent.syntax.base import SyntaxContext, SyntaxHandler, SyntaxResult
from pygent.syntax.builtin import (
    BuiltinSyntaxPlugin,
    CommandHandler,
    MentionHandler,
    create_builtin_syntax_registry,
)
from pygent.syntax.discovery import (
    ENTRY_POINT_GROUP,
    discover_syntax_plugins,
    load_syntax_plugins,
)
from pygent.syntax.parser import ParsedInput, SyntaxInvocation, SyntaxParser
from pygent.syntax.plugins import SyntaxPlugin, inject_syntax_plugin
from pygent.syntax.processor import ProcessedInput, SyntaxProcessor
from pygent.syntax.registry import SyntaxRegistry

__all__ = [
    "BuiltinSyntaxPlugin",
    "CommandHandler",
    "ENTRY_POINT_GROUP",
    "MentionHandler",
    "ParsedInput",
    "ProcessedInput",
    "SyntaxContext",
    "SyntaxHandler",
    "SyntaxInvocation",
    "SyntaxParser",
    "SyntaxPlugin",
    "SyntaxProcessor",
    "SyntaxRegistry",
    "SyntaxResult",
    "create_builtin_syntax_registry",
    "discover_syntax_plugins",
    "inject_syntax_plugin",
    "load_syntax_plugins",
]
