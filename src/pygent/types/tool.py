from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolDefinition(BaseModel):
    """Provider-neutral description of a callable tool."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)

    def validate_arguments(self, arguments: dict[str, Any]) -> None:
        """Validate tool arguments against the supported JSON Schema subset."""
        schema = self.parameters
        if not schema:
            return

        if schema.get("type", "object") != "object":
            raise ValueError("tool parameter schema must describe an object")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            raise ValueError("tool parameter properties must be an object")

        required = schema.get("required", ())
        if not isinstance(required, list):
            raise ValueError("tool parameter required must be an array")

        missing = [name for name in required if name not in arguments]
        if missing:
            raise ValueError(f"missing required arguments: {', '.join(missing)}")

        if schema.get("additionalProperties") is False:
            unknown = [name for name in arguments if name not in properties]
            if unknown:
                raise ValueError(
                    f"unexpected arguments: {', '.join(sorted(unknown))}"
                )

        for name, value in arguments.items():
            property_schema = properties.get(name)
            if property_schema is not None:
                _validate_value(name, value, property_schema)


def _validate_value(name: str, value: Any, schema: Any) -> None:
    if not isinstance(schema, dict):
        raise ValueError(f"invalid schema for argument: {name}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"invalid value for argument: {name}")

    expected_type = schema.get("type")
    if expected_type is None:
        return

    valid = {
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
        "null": value is None,
    }
    if expected_type not in valid:
        raise ValueError(f"unsupported schema type for argument: {name}")
    if not valid[expected_type]:
        raise ValueError(f"invalid type for argument: {name}")
