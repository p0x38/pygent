"""Persistent conversation memory backed by JSON."""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

from platformdirs import user_data_dir
from pydantic import PrivateAttr

from pygent.types import Message

from .conversation import ConversationMemory

_DEFAULT_FILE_NAME = "memory.json"


class PersistentConversationMemory(ConversationMemory):
    """Conversation memory persisted to a JSON file."""

    _path: Path = PrivateAttr()

    def __init__(
        self,
        conversation_id: str = "default",
        *,
        path: str | Path | None = None,
    ) -> None:
        super().__init__(conversation_id=conversation_id)
        self._path = Path(path) if path is not None else self.default_path()
        self._load()
        self.set_conversation(conversation_id)

    @property
    def path(self) -> Path:
        """Return the file used for persistent storage."""
        return self._path

    @staticmethod
    def default_path() -> Path:
        """Return the default persistent memory path."""
        return Path(user_data_dir("pygent", "p0x38")) / _DEFAULT_FILE_NAME

    def _load(self) -> None:
        if not self.path.exists():
            return

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not load memory file: {self.path}") from exc

        if not isinstance(data, dict):
            raise ValueError(f"Invalid memory file: {self.path}")

        data = cast(dict[str, Any], data)

        raw_history = data.get("history", {})

        if not isinstance(raw_history, dict):
            raise ValueError(f"Invalid memory history: {self.path}")

        history = cast(dict[object, object], raw_history)

        self.history = {}

        for conversation_id, raw_messages in history.items():
            if not isinstance(conversation_id, str):
                raise ValueError(f"Invalid memory conversation: {self.path}")

            if not isinstance(raw_messages, list):
                raise ValueError(f"Invalid memory conversation: {self.path}")

            messages = cast(list[object], raw_messages)

            self.history[conversation_id] = [
                Message.model_validate(message) for message in messages
            ]

    def _save(self) -> None:
        payload: dict[str, Any] = {
            "version": 1,
            "history": {
                conversation_id: [
                    message.model_dump(mode="json") for message in messages
                ]
                for conversation_id, messages in self.history.items()
            },
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_path = tempfile.mkstemp(
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temporary_path, self.path)
        except Exception:
            with contextlib.suppress(OSError):
                os.unlink(temporary_path)
            raise

    def add(self, message: Message) -> None:
        super().add(message)
        self._save()

    def clear(self) -> None:
        super().clear()
        self._save()

    def reset_conversation(self, conversation_id: str) -> None:
        super().reset_conversation(conversation_id)
        self._save()

    def seed(self, messages: Iterable[Message]) -> None:
        super().seed(messages)
        self._save()

    def conversations(self) -> list[str]:
        """Return stored conversation IDs in stable order."""
        return sorted(self.history)

    def get_conversation(self, conversation_id: str) -> list[Message]:
        """Return a snapshot of a stored conversation."""
        return list(self.history.get(conversation_id, ()))

    def replace_history(self, history: dict[str, list[Message]]) -> None:
        """Replace all stored conversations and persist them."""
        self.history = {name: list(messages) for name, messages in history.items()}
        self.current_messages = list(self.history.get(self.conversation_id, ()))
        self._save()
