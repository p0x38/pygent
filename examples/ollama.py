"""Ollama provider example.

Prerequisites::

    pip install "pygent[ollama]"
    ollama serve
    ollama pull qwen2.5-coder:3b

Run with::

    python examples/ollama.py
"""

from __future__ import annotations

import asyncio

from pygent import Agent
from pygent.providers import OllamaProvider


async def main() -> None:
    provider = OllamaProvider(model="qwen2.5-coder:3b")
    agent = Agent(provider=provider)
    response = await agent.run("Explain what a Python list is.")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
