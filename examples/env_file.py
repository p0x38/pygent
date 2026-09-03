"""Load secrets from a ``.env`` file before constructing a provider.

Prerequisites::

    pip install "pygent[dotenv]"

Create a ``.env`` file in your project root::

    OPENAI_API_KEY=sk-...
    # or
    OPENROUTER_API_KEY=sk-or-v1-...

Then run::

    python examples/env_file.py
"""

from __future__ import annotations

import asyncio
import os
from typing import Literal

from pygent import load_dotenv
from pygent.agent import Agent
from pygent.providers import OpenAIProvider, OpenRouterProvider
from pygent.providers.base import Provider

ProviderName = Literal["openai", "openrouter"]


def _build_provider() -> Provider:
    # ``load_dotenv`` is safe to call even when python-dotenv is not installed.
    if not load_dotenv():
        print(
            "python-dotenv is not installed; relying on real environment "
            "variables instead."
        )

    openai_key = os.environ.get("OPENAI_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")

    if openai_key:
        return OpenAIProvider(model="gpt-4o-mini")
    if openrouter_key:
        return OpenRouterProvider(model="openai/gpt-4o-mini")
    raise SystemExit(
        "No API key found. Set OPENAI_API_KEY or OPENROUTER_API_KEY in your "
        "shell or in a .env file."
    )


async def main() -> None:
    provider = _build_provider()
    agent = Agent(provider=provider)
    response = await agent.run("Say hello in one short sentence.")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
