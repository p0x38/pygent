from __future__ import annotations

import pytest
from pydantic import BaseModel

from pygent import StructuredOutput
from pygent.exceptions import StructuredOutputError
from pygent.types import ModelResponse


class Person(BaseModel):
    name: str
    age: int


def test_parse_valid_json() -> None:
    parser = StructuredOutput(Person)
    result = parser.parse(ModelResponse(content='{"name":"Alice","age":16}'))

    assert result == Person(name="Alice", age=16)


def test_parse_invalid_json() -> None:
    parser = StructuredOutput(Person)

    with pytest.raises(StructuredOutputError, match="not valid JSON"):
        parser.parse(ModelResponse(content="not json"))


def test_parse_validation_error() -> None:
    parser = StructuredOutput(Person)

    with pytest.raises(StructuredOutputError, match="failed validation"):
        parser.parse(ModelResponse(content='{"name":"Alice","age":"x"}'))


def test_parse_requires_content() -> None:
    parser = StructuredOutput(Person)

    with pytest.raises(StructuredOutputError, match="no textual content"):
        parser.parse(ModelResponse())


def test_schema_matches_model() -> None:
    parser = StructuredOutput(Person)

    assert parser.schema() == Person.model_json_schema()
