from __future__ import annotations

import os

import click

from pygent.config import (
    ConsoleFormatter,
    config_path,
    getenv,
    init_config,
    load_toml,
)
from pygent.i18n import Translator

from ..ui.console import console


def _get_formatter() -> ConsoleFormatter:
    """Create the console configuration formatter."""
    translator = Translator(
        {
            # Temporary/default English catalog.
            # Replace this with your locale loader later.
        }
    )
    return ConsoleFormatter(translator)


def _get_environment() -> dict[str, str]:
    """Return Pygent-related environment variables."""
    return {
        name: value
        for name, value in os.environ.items()
        if (
            name.startswith("PYGENT_")
            or name.startswith("OLLAMA_")
            or name.startswith("OPENROUTER_")
        )
    }


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


@config.command("show")
def show_config() -> None:
    """Show Pygent environment and TOML configuration."""
    list_config()


@config.command("list")
def list_config() -> None:
    """List Pygent environment variables and configuration file values."""
    environment = _get_environment()
    path = config_path()

    try:
        config_values = load_toml(path)
    except FileNotFoundError:
        config_values = {}
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    if not environment and not config_values:
        console.print("[dim]No Pygent configuration found.[/dim]")
        return

    formatter = _get_formatter()

    console.print(
        formatter.all(
            environment,
            config_values,
        ),
    )


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
