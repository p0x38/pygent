"""LM Studio example with customizable group-chat message formatting."""

from __future__ import annotations

import asyncio

from pygent import Agent
from pygent.memory import ConversationMemory
from pygent.providers import LMStudioProvider
from pygent.types import Message


def format_message(message: Message) -> str:
    """Format user messages as [username] content."""
    if message.role == "user" and message.name:
        return f"[{message.name}] {message.content or ''}"

    return message.content or ""


async def main() -> None:
    memory = ConversationMemory()
    memory.seed(
        [
            Message(
                role="system",
                content=(
                    "You are participating in a group conversation. "
                    "User messages may begin with [username]. "
                    "Keep track of which participant said each thing."
                ),
            ),
        ]
    )

    provider = LMStudioProvider(
        model="your-loaded-model-id",
        message_formatter=format_message,
        include_name_metadata=False,
    )

    async with Agent(provider=provider, memory=memory) as agent:
        messages = [
            Message(role="user", name="user1", content="Hi"),
            Message(
                role="user",
                name="user1",
                content="do you know user2?",
            ),
            Message(role="user", name="user2", content="okay"),
        ]

        for message in messages:
            response = await agent.run(message)
            print(f"assistant: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
