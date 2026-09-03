from __future__ import annotations

import asyncio
from typing import Any

import click

from pygent import Agent
from pygent.agent import AgentContext
from pygent.config import load_config
from pygent.memory import ConversationMemory
from pygent.syntax import SyntaxContext, SyntaxSession

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


def _show_syntax_help() -> None:
    console.print(
        "/syntax on              Enable syntax\n"
        "/syntax off             Disable syntax\n"
        "/syntax mention <p>    Set the mention prefix\n"
        "/syntax command <p>    Set the command prefix\n"
        "/syntax reset           Restore default prefixes\n"
        "/syntax                Show this help"
    )


async def _chat(provider: str, model: str) -> None:
    llm = _create_provider(provider, model)
    memory = ConversationMemory(conversation_id="cli")
    syntax_session = SyntaxSession(load_config().chat.syntax)

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

        command: dict[str, Any] | None = None
        processed_text = prompt
        metadata: dict[str, Any] = {}

        if not syntax_session.config.enabled and prompt.startswith("/syntax"):
            command_text = prompt[len("/syntax") :].strip()
            command = {"command": "syntax", "arguments": command_text}
        else:
            try:
                processed = await syntax_session.processor().process(
                    prompt,
                    context=SyntaxContext(),
                )
            except Exception as exc:
                console.print(f"[red]Syntax error:[/red] {exc}")
                continue

            command = next(
                (
                    result.metadata
                    for result in processed.results
                    if result.metadata.get("type") == "command"
                ),
                None,
            )
            processed_text = processed.text
            metadata = processed.metadata

        if command is not None:
            name = str(command.get("command", ""))
            arguments = str(command.get("arguments", "")).strip()

            if name in {"exit", "quit"}:
                break
            if name == "clear":
                memory.clear()
                console.print("[dim]Conversation cleared.[/dim]")
                continue
            if name == "help":
                _show_syntax_help()
                continue
            if name == "syntax":
                parts = arguments.split(maxsplit=1)
                action = parts[0].lower() if parts else "help"
                value = parts[1] if len(parts) > 1 else ""

                try:
                    if action == "on":
                        syntax_session.set_enabled(True)
                    elif action == "off":
                        syntax_session.set_enabled(False)
                    elif action in {"mention", "command"} and value:
                        syntax_session.set_prefix(action, value)
                    elif action == "reset":
                        syntax_session.reset()
                    else:
                        _show_syntax_help()
                        continue
                except ValueError as exc:
                    console.print(f"[red]Syntax error:[/red] {exc}")
                    continue

                console.print(
                    "[dim]Syntax configuration updated for this session.[/dim]"
                )
                continue

        if not syntax_session.config.enabled:
            processed_text = prompt
            metadata = {}

        if not processed_text:
            continue

        try:
            context = AgentContext(metadata=metadata)
            response = await agent.run(processed_text, context=context)
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
