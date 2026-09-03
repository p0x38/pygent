"""Minimal interactive CLI for Pygent.

This example wires a stub ``Provider`` so it runs without network access.
Swap in :class:`pygent.providers.OllamaProvider` or
:class:`pygent.providers.OpenAIProvider` to talk to a real model.

Run with::

    python examples/cli.py

Commands inside the REPL:

* ``/quit`` — exit the CLI
* ``/reset`` — clear conversation memory
* Any other line — sent to the agent as a user message
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Sequence

from pygent import Agent
from pygent.memory import ConversationMemory
from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolDefinition


class EchoProvider(Provider):
    """Trivial provider that echoes the last user message."""

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        last_user = next(
            (m for m in reversed(messages) if m.role == "user"),
            None,
        )
        content = (last_user.content if last_user else "") or ""
        return ModelResponse(content=f"echo: {content}")


def _build_agent(provider_name: str) -> Agent:
    """Return an agent backed by the chosen provider (defaults to the stub)."""
    provider: Provider
    if provider_name == "echo":
        provider = EchoProvider()
    elif provider_name == "ollama":
        from pygent.providers import OllamaProvider

        provider = OllamaProvider(model="qwen2.5-coder:3b")
    elif provider_name == "openai":
        from pygent.providers import OpenAIProvider

        provider = OpenAIProvider(model="gpt-4o-mini")
    else:
        raise SystemExit(f"unknown provider: {provider_name}")
    return Agent(provider=provider, memory=ConversationMemory())


async def _repl(agent: Agent) -> None:
    print("Pygent CLI — type /quit to exit, /reset to clear memory.")
    while True:
        try:
            line = input("> ")
        except EOFError:
            print()
            return

        stripped = line.strip()
        if not stripped:
            continue
        if stripped in {"/quit", "/exit"}:
            return
        if stripped == "/reset":
            if agent.memory is not None:
                agent.memory.clear()
            print("(memory cleared)")
            continue

        response = await agent.run(stripped)
        print(response.text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Minimal Pygent REPL.",
    )
    parser.add_argument(
        "--provider",
        default="echo",
        choices=("echo", "ollama", "openai"),
        help="Which provider to use (default: echo).",
    )
    args = parser.parse_args(argv)

    agent = _build_agent(args.provider)
    try:
        asyncio.run(_repl(agent))
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
