"""Configuration helpers for Pygent.

The :func:`load_dotenv` wrapper keeps ``python-dotenv`` optional. Pygent also
provides a small user-level TOML configuration model used by applications and
the CLI.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir
from pydantic import BaseModel, ConfigDict, Field

_CONFIG_DIR_NAME = "pygent"
_CONFIG_FILE_NAME = "config.toml"

_LOADED = False
_LOAD_ERROR: Exception | None = None


class DefaultConfig(BaseModel):
    """Default provider settings."""

    provider: str = "ollama"
    model: str = "qwen2.5-coder:3b"


class SyntaxConfig(BaseModel):
    """Configuration for conversational syntax."""

    enabled: bool = True
    prefixes: dict[str, str] = Field(
        default_factory=lambda: {"mention": "@", "command": "/"}
    )


class ChatConfig(BaseModel):
    """Interactive chat configuration."""

    syntax: SyntaxConfig = Field(default_factory=SyntaxConfig)


class Config(BaseModel):
    """Pygent user configuration."""

    model_config = ConfigDict(extra="ignore")

    default: DefaultConfig = Field(default_factory=DefaultConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)


def _ensure_loaded() -> None:
    """Load ``.env`` from the current directory and parents once per process."""
    global _LOADED, _LOAD_ERROR

    if _LOADED:
        return

    _LOADED = True
    try:
        from dotenv import find_dotenv, load_dotenv
    except ImportError as exc:
        _LOAD_ERROR = exc
        return

    try:
        env_path = find_dotenv(usecwd=True)
    except Exception:
        return

    if env_path:
        load_dotenv(env_path, override=False)


def load_dotenv(*, path: str | Path | None = None) -> bool:
    """Load a ``.env`` file into :data:`os.environ`."""
    global _LOADED, _LOAD_ERROR

    if path is not None:
        _LOADED = False
        _ensure_loaded()
        try:
            from dotenv import load_dotenv as _load
        except ImportError as exc:
            _LOAD_ERROR = exc
            return False
        return bool(_load(Path(path), override=False))

    _ensure_loaded()
    return _LOAD_ERROR is None


def getenv(name: str, default: str | None = None) -> str | None:
    """Return ``os.environ[name]`` after attempting to load ``.env``."""
    _ensure_loaded()
    return os.environ.get(name, default)


def config_dir() -> Path:
    """Return the user-level Pygent configuration directory."""
    return Path(user_config_dir(_CONFIG_DIR_NAME))


def config_path() -> Path:
    """Return the user-level Pygent TOML configuration path."""
    return config_dir() / _CONFIG_FILE_NAME


def load_config(path: str | Path | None = None) -> Config:
    """Load Pygent configuration, falling back to built-in defaults."""
    config_file = Path(path) if path is not None else config_path()

    if not config_file.exists():
        return Config()

    try:
        with config_file.open("rb") as file:
            data: dict[str, Any] = tomllib.load(file)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(
            f"Invalid TOML configuration: {config_file}"
        ) from exc

    return Config.model_validate(data)


def init_config(*, force: bool = False) -> Path:
    """Create the default user configuration file."""
    path = config_path()

    if path.exists() and not force:
        raise FileExistsError(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """# Pygent configuration

[default]
provider = "ollama"
model = "qwen2.5-coder:3b"

[chat.syntax]
enabled = true

[chat.syntax.prefixes]
mention = "@"
command = "/"
""",
        encoding="utf-8",
    )
    return path


__all__ = [
    "ChatConfig",
    "Config",
    "DefaultConfig",
    "SyntaxConfig",
    "config_dir",
    "config_path",
    "getenv",
    "init_config",
    "load_config",
    "load_dotenv",
]
