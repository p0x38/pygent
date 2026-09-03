"""Extensible conversational syntax for Pygent."""

from pygent.syntax.base import SyntaxContext, SyntaxHandler, SyntaxResult
from pygent.syntax.parser import ParsedInput, SyntaxInvocation, SyntaxParser
from pygent.syntax.plugins import SyntaxPlugin, inject_syntax_plugin
from pygent.syntax.registry import SyntaxRegistry

__all__ = [
    "ParsedInput",
    "SyntaxContext",
    "SyntaxHandler",
    "SyntaxInvocation",
    "SyntaxParser",
    "SyntaxPlugin",
    "SyntaxRegistry",
    "SyntaxResult",
    "inject_syntax_plugin",
]
