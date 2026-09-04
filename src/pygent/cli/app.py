from __future__ import annotations

import click

from .commands.chat import chat
from .commands.config import config


@click.group()
@click.version_option()
@click.option(
    "--locale",
    default="en",
    show_default=True,
    help="Locale used for user-facing messages.",
)
def main(locale: str) -> None:
    """Pygent command-line interface."""
    ...


main.add_command(chat)
main.add_command(config)
