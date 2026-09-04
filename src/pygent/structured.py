from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from pygent.exceptions import StructuredOutputError
from pygent.types import ModelResponse

T = TypeVar("T", bound=BaseModel)


class StructuredOutput[T: BaseModel]:
    """Validate model JSON content against a Pydantic model."""

    def __init__(self, model: type[T]) -> None:
        self.model = model

    def parse(self, response: ModelResponse) -> T:
        """Parse and validate the textual response as structured JSON."""
        if response.content is None:
            raise StructuredOutputError("model response has no textual content")

        try:
            data: Any = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise StructuredOutputError(
                f"structured response is not valid JSON: {exc}"
            ) from exc

        try:
            return self.model.model_validate(data)
        except ValidationError as exc:
            raise StructuredOutputError(
                f"structured response failed validation: {exc}"
            ) from exc

    def schema(self) -> dict[str, Any]:
        """Return the JSON Schema used to describe the expected output."""
        return self.model.model_json_schema()
