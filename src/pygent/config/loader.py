"""Configuration loading helpers."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

from .models import Config

_CONFIG_DIR_NAME = "pygent"
_CONFIG_FILE_NAME = "config.toml"

_loaded = False
_load_error: Exception | None = None


def _ensure_loaded() -> None:
    """Load ``.env`` from the current directory and parents once per process."""
    global _loaded, _load_error

    if _loaded:
        return

    _loaded = True

    try:
        from dotenv import find_dotenv
        from dotenv import load_dotenv as _load_dotenv
    except ImportError as exc:
        _load_error = exc
        return

    try:
        env_path = find_dotenv(usecwd=True)
    except Exception:
        return

    if env_path:
        _load_dotenv(env_path, override=False)


def load_dotenv(*, path: str | Path | None = None) -> bool:
    """Load a ``.env`` file into :data:`os.environ`.

    Returns ``True`` if the file was loaded, or ``False`` if the optional
    ``python-dotenv`` dependency is not installed.
    """
    global _loaded, _load_error

    if path is not None:
        try:
            from dotenv import load_dotenv as _load
        except ImportError as exc:
            _load_error = exc
            return False

        _loaded = True
        _load_error = None

        return bool(_load(Path(path), override=False))

    _ensure_loaded()
    return _load_error is None


def getenv(
    name: str,
    default: str | None = None,
) -> str | None:
    """Return an environment variable after attempting to load ``.env``."""
    _ensure_loaded()
    return os.environ.get(name, default)


def config_dir() -> Path:
    """Return the user-level Pygent configuration directory."""
    return Path(user_config_dir(_CONFIG_DIR_NAME, "p0x38"))


def config_path() -> Path:
    """Return the path to the user-level Pygent configuration file."""
    return config_dir() / _CONFIG_FILE_NAME


def load_config(path: str | Path | None = None) -> Config:
    """Load Pygent configuration from a TOML file.

    If ``path`` is omitted, the user-level Pygent configuration path is used.

    A missing configuration file is not an error; the default configuration
    is returned instead.
    """
    config_file = Path(path) if path is not None else config_path()

    if not config_file.exists():
        return Config()

    try:
        with config_file.open("rb") as file:
            data: dict[str, Any] = tomllib.load(file)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML configuration: {config_file}") from exc

    return Config.model_validate(data)


def init_config(*, force: bool = False) -> Path:
    """Create the default Pygent configuration file.

    Raises:
        FileExistsError: If the configuration already exists and ``force`` is
            False.
        OSError: If the configuration directory or file cannot be created.
    """
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


def get_default_provider() -> str:
    """Return the configured default provider."""
    return (
        getenv(
            "PYGENT_PROVIDER",
            load_config().default.provider,
        )
        or "ollama"
    )


def get_default_model() -> str:
    """Return the configured default model."""
    return (
        getenv(
            "PYGENT_MODEL",
            load_config().default.model,
        )
        or "qwen2.5-coder:3b"
    )


__all__ = [
    "config_dir",
    "config_path",
    "get_default_model",
    "get_default_provider",
    "getenv",
    "init_config",
    "load_config",
    "load_dotenv",
]
