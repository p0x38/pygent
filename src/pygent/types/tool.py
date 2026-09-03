from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


JsonSchemaType = Literal[
    "object",
    "string",
    "integer",
    "number",
    "boolean",
    "array",
    "null",
]


class JsonSchema(BaseModel):
    """Validated subset of JSON Schema supported by Pygent tools."""

    model_config = ConfigDict(extra="allow")

    type: JsonSchemaType | None = None
    description: str | None = None
    enum: list[Any] | None = None
    properties: dict[str, JsonSchema] | None = None
    required: list[str] = Field(default_factory=list)
    additionalProperties: bool | JsonSchema | None = None
    items: JsonSchema | None = None

    @model_validator(mode="after")
    def validate_structure(self) -> JsonSchema:
        if self.type == "object" and self.properties is None and self.items is not None:
            raise ValueError("items is not valid for object schemas")
        if self.type != "object" and self.properties is not None:
            raise ValueError("properties is only valid for object schemas")
        if self.type != "array" and self.items is not None:
            raise ValueError("items is only valid for array schemas")

        if self.properties is not None:
            missing = [name for name in self.required if name not in self.properties]
            if missing:
                raise ValueError(
                    "required fields must be declared in properties: "
                    + ", ".join(missing)
                )
        elif self.required:
            raise ValueError("required is only valid when properties are defined")

        if len(self.required) != len(set(self.required)):
            raise ValueError("required fields must be unique")

        if self.enum is not None and not self.enum:
            raise ValueError("enum must contain at least one value")

        return self


class ToolDefinition(BaseModel):
    """Provider-neutral description of a callable tool."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_parameters_schema(self) -> ToolDefinition:
        if self.parameters:
            JsonSchema.model_validate(self.parameters)
        return self

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

        required = schema.get("required", [])
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
