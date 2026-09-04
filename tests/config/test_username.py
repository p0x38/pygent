from __future__ import annotations

from pathlib import Path

import pytest

from pygent.config import get_username, load_config


def test_username_from_toml(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text('[user]\nusername = "NoteSwiper"\n', encoding="utf-8")

    assert load_config(config_file).user.username == "NoteSwiper"


def test_username_environment_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text('[user]\nusername = "toml-user"\n', encoding="utf-8")
    monkeypatch.setenv("PYGENT_USERNAME", "env-user")
    monkeypatch.setattr("pygent.config.loader.config_path", lambda: config_file)

    assert get_username() == "env-user"


def test_username_defaults_to_none(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text("", encoding="utf-8")

    assert load_config(config_file).user.username is None
