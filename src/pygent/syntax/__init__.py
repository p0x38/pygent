"""Extensible conversational syntax for Pygent."""

from pygent.syntax.base import SyntaxContext, SyntaxHandler, SyntaxResult
from pygent.syntax.builtin import (
    BuiltinSyntaxPlugin,
    CommandHandler,
    MentionHandler,
    create_builtin_syntax_registry,
)
from pygent.syntax.parser import ParsedInput, SyntaxInvocation, SyntaxParser
from pygent.syntax.plugins import SyntaxPlugin, inject_syntax_plugin
from pygent.syntax.registry import SyntaxRegistry

__all__ = [
    "BuiltinSyntaxPlugin",
    "CommandHandler",
    "MentionHandler",
    "ParsedInput",
    "SyntaxContext",
    "SyntaxHandler",
    "SyntaxInvocation",
    "SyntaxParser",
    "SyntaxPlugin",
    "SyntaxRegistry",
    "SyntaxResult",
    "create_builtin_syntax_registry",
    "inject_syntax_plugin",
]
