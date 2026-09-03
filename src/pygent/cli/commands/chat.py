from __future__ import annotations

import asyncio
from typing import Any

import click

from pygent import Agent
from pygent.agent import AgentContext
from pygent.memory import ConversationMemory
from pygent.syntax import (
    SyntaxContext,
    SyntaxProcessor,
    create_builtin_syntax_registry,
    load_syntax_plugins,
)

from ...config import get_default_model, get_default_provider
from ...providers.base import Provider
from ..ui.console import console


def _create_provider(provider: str, model: str) -> Provider:
    if provider == "ollama":
        from pygent.providers.ollama import OllamaProvider

        return OllamaProvider(model)

    if provider == "openrouter":
        from pygent.providers.openrouter import OpenRouterProvider

        return OpenRouterProvider(model)

    raise click.ClickException(f"Unsupported provider: {provider}")


async def _chat(provider: str, model: str) -> None:
    llm = _create_provider(provider, model)
    memory = ConversationMemory(conversation_id="cli")
    registry = create_builtin_syntax_registry()
    load_syntax_plugins(registry)
    syntax = SyntaxProcessor(registry)

    agent = Agent(
        llm,
        memory=memory,
        max_iterations=8,
    )

    console.print(f"[bold]Pygent[/bold] — {provider}/{model}")
    console.print("Type /help for commands, /exit to quit.\n")

    while True:
        try:
            prompt = await asyncio.to_thread(
                click.prompt,
                "You",
                prompt_suffix=" > ",
                default="",
                show_default=False,
            )
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        prompt = prompt.strip()

        if not prompt:
            continue

        try:
            processed = await syntax.process(prompt, context=SyntaxContext())
        except Exception as exc:
            console.print(f"[red]Syntax error:[/red] {exc}")
            continue

        command: dict[str, Any] | None = next(
            (
                result.metadata
                for result in processed.results
                if result.metadata.get("type") == "command"
            ),
            None,
        )

        if command is not None:
            name = str(command.get("command", ""))
            if name in {"exit", "quit"}:
                break
            if name == "clear":
                memory.clear()
                console.print("[dim]Conversation cleared.[/dim]")
                continue
            if name == "help":
                console.print(
                    "/clear  Clear conversation history\n"
                    "/exit   Exit the chat\n"
                    "/quit   Exit the chat"
                )
                continue

        if not processed.text:
            continue

        try:
            context = AgentContext(metadata=processed.metadata)
            response = await agent.run(processed.text, context=context)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            continue

        if response.text:
            console.print(f"\n[bold]Pygent[/bold] > {response.text}\n")


@click.command()
@click.option("--provider", default=None, type=click.Choice(["ollama", "openrouter"]))
@click.option("--model", default=None)
def chat(provider: str, model: str) -> None:
    """Start an interactive chat session."""
    provider = provider or get_default_provider()
    model = model or get_default_model()

    asyncio.run(_chat(provider, model))
