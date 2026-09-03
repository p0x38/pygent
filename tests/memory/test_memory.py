from __future__ import annotations

from pygent.memory import ConversationMemory
from pygent.types import Message


def test_add_and_read_messages() -> None:
    memory = ConversationMemory()
    memory.add(Message(role="user", content="hi"))
    memory.add(Message(role="assistant", content="hello"))

    messages = memory.messages()

    assert [m.role for m in messages] == ["user", "assistant"]


def test_clear_removes_messages() -> None:
    memory = ConversationMemory()
    memory.add(Message(role="user", content="hi"))

    memory.clear()

    assert memory.messages() == []
    assert memory.all_messages() == []


def test_conversation_ids_are_isolated() -> None:
    memory = ConversationMemory()
    memory.add(Message(role="user", content="a"))

    memory.set_conversation("other")
    memory.add(Message(role="user", content="b"))

    assert [m.content for m in memory.messages()] == ["b"]

    memory.set_conversation("default")
    assert [m.content for m in memory.messages()] == ["a"]


def test_reset_conversation_drops_history() -> None:
    memory = ConversationMemory()
    memory.add(Message(role="user", content="hi"))

    memory.reset_conversation(memory.conversation_id)

    assert memory.messages() == []


def test_seed_replaces_history() -> None:
    memory = ConversationMemory()
    memory.add(Message(role="user", content="old"))

    memory.seed([Message(role="user", content="new")])

    assert [m.content for m in memory.messages()] == ["new"]


def test_len_and_contains() -> None:
    memory = ConversationMemory()
    msg = Message(role="user", content="hi")
    memory.add(msg)

    assert len(memory) == 1
    assert msg in memory
