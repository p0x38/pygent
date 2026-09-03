"""OpenRouter provider example.

Prerequisites::

    export OPENROUTER_API_KEY=sk-or-v1-...

Run with::

    python examples/openrouter.py
"""

from __future__ import annotations

import asyncio

from pygent import Agent
from pygent.providers import OpenRouterProvider


async def main() -> None:
    provider = OpenRouterProvider(model="openai/gpt-4o-mini")
    agent = Agent(provider=provider)
    response = await agent.run("Give me a haiku about Python.")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
