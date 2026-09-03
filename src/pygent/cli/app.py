from __future__ import annotations

import click

from .commands.chat import chat
from .commands.config import config


@click.group()
@click.version_option()
def main() -> None:
    """Pygent command-line interface."""


main.add_command(chat)
main.add_command(config)
