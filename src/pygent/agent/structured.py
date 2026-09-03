from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from pygent.exceptions import PygentError


class StructuredOutputError(PygentError):
    """Raised when a structured output cannot be parsed or validated."""


_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def parse_structured_output[T: BaseModel](
    text: str,
    model: type[T],
) -> T:
    """Parse ``text`` into a Pydantic ``model`` instance.

    The function accepts plain JSON or a JSON object embedded in prose and
    raises :class:`StructuredOutputError` when parsing fails.
    """
    if not text:
        raise StructuredOutputError("response is empty")

    candidate = text.strip()
    if not candidate.startswith("{"):
        match = _JSON_BLOCK.search(candidate)
        if match is None:
            raise StructuredOutputError("response is not JSON")
        candidate = match.group(0)

    try:
        payload: Any = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise StructuredOutputError(f"invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise StructuredOutputError("JSON payload must be an object")

    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise StructuredOutputError(str(exc)) from exc


def tool_arguments[T: BaseModel](
    tool_arguments: Mapping[str, Any],
    model: type[T],
) -> T:
    """Validate model-supplied tool arguments against ``model``."""
    try:
        return model.model_validate(dict(tool_arguments))
    except ValidationError as exc:
        raise StructuredOutputError(str(exc)) from exc
