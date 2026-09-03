"""Configuration helpers for Pygent.

The :func:`load_dotenv` wrapper makes ``python-dotenv`` an optional dependency
so that Pygent itself does not require it. Providers call
:func:`getenv` (instead of :func:`os.environ.get` directly) so that any
``.env`` file the user has in their project is picked up automatically when
the optional extra is installed.
"""

from __future__ import annotations

import os
from pathlib import Path

_LOADED = False
_LOAD_ERROR: Exception | None = None


def _ensure_loaded() -> None:
    """Load ``.env`` from the current directory and parents (once per process)."""
    global _LOADED, _LOAD_ERROR
    if _LOADED:
        return
    _LOADED = True
    try:
        from dotenv import find_dotenv, load_dotenv  # type: ignore[import-not-found]
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
    """Load a ``.env`` file into :data:`os.environ`.

    Returns ``True`` if the file was loaded, ``False`` if the optional
    ``python-dotenv`` dependency is not installed.

    The providers call this helper automatically, so end users normally do
    not need to invoke it. It is exposed for scripts and applications that
    want to load a specific file or force a reload.
    """
    global _LOADED, _LOAD_ERROR
    if path is not None:
        _LOADED = False  # allow loading a different file
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


__all__ = ["getenv", "load_dotenv"]
