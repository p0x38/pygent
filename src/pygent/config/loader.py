"""Configuration loading helpers."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from platformdirs import user_config_dir
from tomlkit import dumps

from .models import Config

_CONFIG_DIR_NAME = "pygent"
_CONFIG_FILE_NAME = "config.toml"

_loaded = False
_load_error: Exception | None = None


type TomlValue = str | int | float | bool | list["TomlValue"] | dict[str, "TomlValue"]


def load_toml(path: str | Path | None = None) -> dict[str, TomlValue]:
    """Load raw Pygent configuration from a TOML file."""
    config_file = Path(path) if path is not None else config_path()

    if not config_file.exists():
        return {}

    try:
        with config_file.open("rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        raise
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML configuration: {config_file}") from exc
    except OSError as exc:
        raise OSError(
            f"Could not read configuration file: {config_file}: {exc}"
        ) from exc


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
    """Load a ``.env`` file into :data:`os.environ`."""
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


def getenv(name: str, default: str | None = None) -> str | None:
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
    """Load and validate Pygent configuration from a TOML file."""
    return Config.model_validate(load_toml(path))


def init_config(*, force: bool = False) -> Path:
    """Create the default Pygent configuration file."""
    path = config_path()

    if path.exists() and not force:
        raise FileExistsError(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    config = Config()

    path.write_text(
        dumps(config.model_dump(mode="python", exclude_none=True)),
        encoding="utf-8",
    )

    return path


def get_default_provider() -> str:
    """Return the configured default provider."""
    return getenv("PYGENT_PROVIDER", load_config().provider.provider) or "ollama"


def get_default_model() -> str:
    """Return the configured default model."""
    return getenv("PYGENT_MODEL", load_config().provider.model) or "qwen2.5-coder:3b"


def get_username() -> str | None:
    """Return the configured username, with environment override."""
    return getenv("PYGENT_USERNAME", load_config().user.username)


__all__ = [
    "config_dir",
    "config_path",
    "get_default_model",
    "get_default_provider",
    "get_username",
    "getenv",
    "init_config",
    "load_config",
    "load_dotenv",
    "load_toml",
]
