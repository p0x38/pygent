from __future__ import annotations

from pathlib import Path

import pytest

from pygent.memory import PersistentConversationMemory
from pygent.types import Message


def test_persistent_memory_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    memory = PersistentConversationMemory("chat", path=path)
    memory.add(Message(role="user", content="hello"))
    memory.add(Message(role="assistant", content="hi"))

    restored = PersistentConversationMemory("chat", path=path)

    assert restored.conversations() == ["chat"]
    assert [message.content for message in restored.messages()] == ["hello", "hi"]


def test_persistent_memory_keeps_conversations_isolated(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    memory = PersistentConversationMemory("one", path=path)
    memory.add(Message(role="user", content="first"))
    memory.set_conversation("two")
    memory.add(Message(role="user", content="second"))

    restored = PersistentConversationMemory("one", path=path)

    assert restored.get_conversation("one")[0].content == "first"
    assert restored.get_conversation("two")[0].content == "second"


def test_persistent_memory_reset_is_saved(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    memory = PersistentConversationMemory("chat", path=path)
    memory.add(Message(role="user", content="hello"))
    memory.reset_conversation("chat")

    restored = PersistentConversationMemory(path=path)

    assert restored.conversations() == []


def test_persistent_memory_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    path.write_text("not json", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not load memory file"):
        PersistentConversationMemory(path=path)


def test_persistent_memory_loads_valid_json_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "memory.json"
    memory = PersistentConversationMemory("chat", path=path)
    memory.add(Message(role="user", content="hello"))

    original_read_text = Path.read_text
    reads = 0

    def counted_read_text(self: Path, *args: object, **kwargs: object) -> str:
        nonlocal reads
        if self == path:
            reads += 1
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", counted_read_text)
    restored = PersistentConversationMemory("chat", path=path)

    assert restored.messages()[0].content == "hello"
    assert reads == 1
