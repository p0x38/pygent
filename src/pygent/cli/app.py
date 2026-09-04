from __future__ import annotations

import click

from pygent.i18n import load_translator

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
@click.pass_context
def main(ctx: click.Context, locale: str) -> None:
    """Pygent command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj["translator"] = load_translator(locale)


main.add_command(chat)
main.add_command(config)
