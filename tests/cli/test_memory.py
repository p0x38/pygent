from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from pygent.cli import main
from pygent.memory import PersistentConversationMemory
from pygent.types import Message


def test_memory_help() -> None:
    result = CliRunner().invoke(main, ["memory", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "get" in result.output
    assert "clear" in result.output
    assert "reset" in result.output
    assert "export" in result.output
    assert "import" in result.output


def test_memory_list_and_get(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    memory = PersistentConversationMemory("chat", path=path)
    memory.add(Message(role="user", content="hello"))
    memory.add(Message(role="assistant", content="hi"))

    runner = CliRunner()
    result = runner.invoke(main, ["memory", "list", "--path", str(path)])
    assert result.exit_code == 0
    assert "chat (2 messages)" in result.output

    result = runner.invoke(main, ["memory", "get", "chat", "--path", str(path)])
    assert result.exit_code == 0
    assert "[user] hello" in result.output
    assert "[assistant] hi" in result.output


def test_memory_clear(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    memory = PersistentConversationMemory("chat", path=path)
    memory.add(Message(role="user", content="hello"))

    result = CliRunner().invoke(
        main,
        ["memory", "clear", "chat", "--path", str(path)],
    )
    assert result.exit_code == 0
    assert PersistentConversationMemory(path=path).conversations() == []


def test_memory_export_and_import(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    exported = tmp_path / "export.json"
    imported_path = tmp_path / "imported.json"

    memory = PersistentConversationMemory("chat", path=path)
    memory.add(Message(role="user", content="hello"))

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["memory", "export", str(exported), "--path", str(path)],
    )
    assert result.exit_code == 0
    assert exported.exists()

    result = runner.invoke(
        main,
        [
            "memory",
            "import",
            str(exported),
            "--path",
            str(imported_path),
            "--yes",
        ],
    )
    assert result.exit_code == 0
    restored = PersistentConversationMemory(path=imported_path)
    assert restored.get_conversation("chat")[0].content == "hello"


def test_memory_reset(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    memory = PersistentConversationMemory("one", path=path)
    memory.add(Message(role="user", content="first"))
    memory.set_conversation("two")
    memory.add(Message(role="user", content="second"))

    result = CliRunner().invoke(
        main,
        ["memory", "reset", "--path", str(path), "--yes"],
    )
    assert result.exit_code == 0
    assert PersistentConversationMemory(path=path).conversations() == []
