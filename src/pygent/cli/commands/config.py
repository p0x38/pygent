from __future__ import annotations

import os

import click

from pygent.config import ConsoleFormatter, config_path, getenv, init_config

from ..ui.console import console


@click.group(invoke_without_command=True)
@click.pass_context
def config(ctx: click.Context) -> None:
    """Inspect Pygent configuration."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@config.command("get")
@click.argument("name")
def get(name: str) -> None:
    """Get an environment configuration value."""
    value = getenv(name)

    if value is None:
        console.print(f"[dim]{name} is not set.[/dim]")
        return

    # Avoid dumping secrets directly into the terminal.
    if any(token in name.upper() for token in ("KEY", "TOKEN", "PASSWORD", "SECRET")):
        console.print(f"{name}=********")
    else:
        console.print(f"{name}={value}")


@config.command("list")
def list_config() -> None:
    """List configured Pygent-related environment variables."""
    values = {
        name: os.environ[name]
        for name in os.environ
        if (
            name.startswith("PYGENT_")
            or name.startswith("OLLAMA_")
            or name.startswith("OPENROUTER_")
        )
    }

    if not values:
        console.print("[dim]No Pygent-related environment variables found.[/dim]")
        return

    console.print(ConsoleFormatter.all(values))


@config.command("path")
def path() -> None:
    """Show the current working directory used for .env discovery."""
    console.print(f"Working directory: {os.getcwd()}")
    console.print(f"User config: {config_path()}")
    console.print(
        "[dim]Pygent searches for .env from the current directory and its "
        "parents when python-dotenv is installed.[/dim]"
    )


@config.command("init")
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite an existing configuration file.",
)
def init(force: bool) -> None:
    """Create a default Pygent configuration file."""
    path = config_path()

    if path.exists() and not force:
        raise click.ClickException(
            f"Configuration already exists: {path}\nUse --force to overwrite it."
        )

    try:
        path = init_config(force=force)
    except OSError as exc:
        raise click.ClickException(f"Could not create configuration: {exc}") from exc

    console.print(f"[green]Created configuration:[/green] {path}")
