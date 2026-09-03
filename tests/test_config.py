"""Tests for :mod:`pygent.config`."""

from __future__ import annotations

import os

import pytest

from pygent import config


@pytest.fixture
def _reset_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset the module-level ``_LOADED`` flag so each test gets a fresh load."""
    monkeypatch.setattr(config, "_LOADED", False)
    monkeypatch.setattr(config, "_LOAD_ERROR", None)


def test_getenv_falls_back_to_os_environ(
    monkeypatch: pytest.MonkeyPatch, _reset_loaded: None
) -> None:
    monkeypatch.setenv("FOO_BAR_BAZ", "from-env")
    assert config.getenv("FOO_BAR_BAZ") == "from-env"


def test_load_dotenv_without_dependency_returns_false(
    monkeypatch: pytest.MonkeyPatch, _reset_loaded: None
) -> None:
    """If ``python-dotenv`` is not installed, ``load_dotenv`` is a safe no-op."""
    monkeypatch.setitem(__import__("sys").modules, "dotenv", None)
    monkeypatch.setattr(config, "_LOAD_ERROR", ImportError("no dotenv"))
    assert config.load_dotenv() is False


def test_load_dotenv_with_path(
    tmp_path: os.PathLike[str],
    monkeypatch: pytest.MonkeyPatch,
    _reset_loaded: None,
) -> None:
    pytest.importorskip("dotenv")
    from pathlib import Path

    env_file = Path(tmp_path) / ".env"
    env_file.write_text("FOO_FROM_FILE=hello\n", encoding="utf-8")

    monkeypatch.delenv("FOO_FROM_FILE", raising=False)
    loaded = config.load_dotenv(path=env_file)

    assert loaded is True
    assert os.environ.get("FOO_FROM_FILE") == "hello"
