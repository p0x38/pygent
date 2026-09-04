from __future__ import annotations

import shutil
from pathlib import Path

import click

from pygent.memory import PersistentConversationMemory

from ..ui.console import console


def _memory(path: str | Path | None = None) -> PersistentConversationMemory:
    """Create the persistent CLI memory store."""
    return PersistentConversationMemory(path=path)


@click.group()
def memory() -> None:
    """Manage persistent conversation memory."""


@memory.command("list")
@click.option("--path", type=click.Path(path_type=Path), default=None)
def list_memory(path: Path | None) -> None:
    """List stored conversations."""
    store = _memory(path)
    conversations = store.conversations()

    if not conversations:
        console.print("[dim]No conversations found.[/dim]")
        return

    for conversation_id in conversations:
        count = len(store.get_conversation(conversation_id))
        console.print(f"{conversation_id} ({count} messages)")


@memory.command("get")
@click.argument("conversation")
@click.option("--path", type=click.Path(path_type=Path), default=None)
def get_memory(conversation: str, path: Path | None) -> None:
    """Show the messages in a conversation."""
    store = _memory(path)
    messages = store.get_conversation(conversation)

    if not messages:
        raise click.ClickException(f"Conversation not found: {conversation}")

    for message in messages:
        content = message.content or ""
        console.print(f"[{message.role}] {content}", markup=False)


@memory.command("clear")
@click.argument("conversation")
@click.option("--path", type=click.Path(path_type=Path), default=None)
def clear_memory(conversation: str, path: Path | None) -> None:
    """Delete one stored conversation."""
    store = _memory(path)
    if conversation not in store.conversations():
        raise click.ClickException(f"Conversation not found: {conversation}")

    store.reset_conversation(conversation)
    console.print(f"[dim]Conversation cleared: {conversation}[/dim]")


@memory.command("reset")
@click.option("--path", type=click.Path(path_type=Path), default=None)
@click.confirmation_option(
    "--yes",
    prompt="Reset all stored conversations?",
)
def reset_memory(path: Path | None) -> None:
    """Delete all stored conversations."""
    store = _memory(path)
    store.replace_history({})
    console.print("[dim]All conversations reset.[/dim]")


@memory.command("export")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option("--path", type=click.Path(path_type=Path), default=None)
def export_memory(destination: Path, path: Path | None) -> None:
    """Export persistent memory to a JSON file."""
    store = _memory(path)
    if not store.path.exists():
        raise click.ClickException("No memory file exists to export.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(store.path, destination)
    except OSError as exc:
        raise click.ClickException(f"Could not export memory: {exc}") from exc

    console.print(f"Exported memory: {destination}")


@memory.command("import")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--path", type=click.Path(path_type=Path), default=None)
@click.confirmation_option(
    "--yes",
    prompt="Replace all stored conversations with this import?",
)
def import_memory(source: Path, path: Path | None) -> None:
    """Import persistent memory from a JSON file."""
    try:
        imported = PersistentConversationMemory(path=source)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    target = _memory(path)
    target.replace_history(
        {
            conversation_id: imported.get_conversation(conversation_id)
            for conversation_id in imported.conversations()
        }
    )
    console.print(f"Imported memory: {source}")
