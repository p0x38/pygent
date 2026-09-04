"""Translation catalog loading helpers."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import cast

type CatalogValue = str | dict[str, "CatalogValue"]


def load_catalog(path: str | Path) -> dict[str, str]:
    """Load and flatten a TOML translation catalog."""
    catalog_path = Path(path)

    try:
        with catalog_path.open("rb") as file:
            data = tomllib.load(file)
    except FileNotFoundError:
        raise
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid translation catalog: {catalog_path}: {exc}") from exc
    except OSError as exc:
        raise OSError(
            f"Could not read translation catalog: {catalog_path}: {exc}"
        ) from exc

    translations: dict[str, str] = {}
    _flatten(data, translations)

    return translations


def _flatten(
    values: Mapping[str, object],
    output: dict[str, str],
    *,
    prefix: str = "",
) -> None:
    """Flatten a nested catalog mapping."""
    for key, value in values.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, str):
            output[full_key] = value
            continue

        if isinstance(value, dict):
            child = cast(dict[str, object], value)
            _flatten(
                child,
                output,
                prefix=full_key,
            )
            continue

        raise ValueError(f"Translation value must be a string or table: {full_key}")
