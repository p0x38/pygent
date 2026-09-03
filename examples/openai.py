"""OpenAI provider example.

Prerequisites::

    export OPENAI_API_KEY=sk-...

Run with::

    python examples/openai.py
"""

from __future__ import annotations

import asyncio

from pygent import Agent
from pygent.providers import OpenAIProvider


async def main() -> None:
    provider = OpenAIProvider(model="gpt-4o-mini")
    agent = Agent(provider=provider)
    response = await agent.run("Say hello in Japanese.")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
