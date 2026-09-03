from __future__ import annotations

import pytest

from pygent.types import ToolDefinition


@pytest.fixture
def definition() -> ToolDefinition:
    return ToolDefinition(
        name="example",
        description="An example tool.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer"},
                "enabled": {"type": "boolean"},
                "mode": {"type": "string", "enum": ["fast", "safe"]},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    )


def test_valid_arguments_are_accepted(definition: ToolDefinition) -> None:
    definition.validate_arguments(
        {"name": "test", "count": 2, "enabled": True, "mode": "fast"}
    )


def test_missing_required_argument_is_rejected(definition: ToolDefinition) -> None:
    with pytest.raises(ValueError, match="missing required arguments: name"):
        definition.validate_arguments({})


def test_unknown_argument_is_rejected(definition: ToolDefinition) -> None:
    with pytest.raises(ValueError, match="unexpected arguments: extra"):
        definition.validate_arguments({"name": "test", "extra": True})


def test_wrong_argument_type_is_rejected(definition: ToolDefinition) -> None:
    with pytest.raises(ValueError, match="invalid type for argument: count"):
        definition.validate_arguments({"name": "test", "count": "two"})


def test_boolean_is_not_accepted_as_integer(definition: ToolDefinition) -> None:
    with pytest.raises(ValueError, match="invalid type for argument: count"):
        definition.validate_arguments({"name": "test", "count": True})


def test_invalid_enum_value_is_rejected(definition: ToolDefinition) -> None:
    with pytest.raises(ValueError, match="invalid value for argument: mode"):
        definition.validate_arguments({"name": "test", "mode": "turbo"})


def test_empty_schema_accepts_arguments() -> None:
    definition = ToolDefinition(name="example", description="An example tool.")

    definition.validate_arguments({"anything": "goes"})


def test_invalid_schema_type_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported tool parameter type"):
        ToolDefinition(
            name="example",
            description="An example tool.",
            parameters={"type": "banana"},
        )


def test_invalid_required_schema_is_rejected() -> None:
    with pytest.raises(ValueError, match="required must be an array"):
        ToolDefinition(
            name="example",
            description="An example tool.",
            parameters={"type": "object", "required": "name"},
        )


def test_invalid_properties_schema_is_rejected() -> None:
    with pytest.raises(ValueError, match="properties must be an object"):
        ToolDefinition(
            name="example",
            description="An example tool.",
            parameters={"type": "object", "properties": []},
        )


def test_invalid_property_definition_is_rejected() -> None:
    with pytest.raises(ValueError, match="properties must contain schema objects"):
        ToolDefinition(
            name="example",
            description="An example tool.",
            parameters={
                "type": "object",
                "properties": {"value": "string"},
            },
        )
