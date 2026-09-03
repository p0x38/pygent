from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from pygent.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
)
from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolCall, ToolDefinition, Usage


class OpenAICompatibleProvider(Provider):
    """Provider that talks to OpenAI-style ``/chat/completions`` endpoints."""

    def __init__(
        self,
        model: str,
        *,
        base_url: str = "https://api.openai.com/v1",
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = 60.0,
        extra_body: Mapping[str, Any] | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        if not model:
            raise ValueError("model must not be empty")
        if not base_url:
            raise ValueError("base_url must not be empty")

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.extra_body: dict[str, Any] = dict(extra_body or {})
        self.default_headers: dict[str, str] = dict(default_headers or {})

        if client is None:
            headers: dict[str, str] = {"Content-Type": "application/json"}
            if api_key is not None:
                headers["Authorization"] = f"Bearer {api_key}"
            headers.update(self.default_headers)
            client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=timeout,
            )
        self._owns_client = client is None or not self._has_user_managed_client(client)
        self.client = client

    @staticmethod
    def _has_user_managed_client(client: httpx.AsyncClient) -> bool:
        return not getattr(client, "_is_pygent_default", True)

    async def aclose(self) -> None:
        """Close the underlying HTTP client if Pygent created it."""
        if self._owns_client:
            await self.client.aclose()

    async def __aenter__(self) -> OpenAICompatibleProvider:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [self._message_to_payload(message) for message in messages],
        }
        if tools:
            payload["tools"] = [self._tool_to_payload(tool) for tool in tools]
        if self.extra_body:
            payload.update(self.extra_body)

        try:
            response = await self.client.post("/chat/completions", json=payload)
        except httpx.HTTPError as exc:
            raise ProviderConnectionError(str(exc)) from exc

        if response.status_code == 401 or response.status_code == 403:
            raise ProviderAuthenticationError(f"authentication failed: {response.text}")
        if response.status_code == 429:
            raise ProviderRateLimitError(f"rate limited: {response.text}")
        if response.status_code >= 400:
            raise ProviderRequestError(
                f"request failed with status {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise ProviderResponseError(
                f"failed to parse response JSON: {exc}"
            ) from exc

        return self._parse_response(data)

    def _parse_response(self, data: Any) -> ModelResponse:
        if not isinstance(data, dict):
            raise ProviderResponseError("response must be a JSON object")

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ProviderResponseError("response is missing 'choices'")

        first = choices[0]
        if not isinstance(first, dict):
            raise ProviderResponseError("invalid 'choices[0]' entry")

        message_data = first.get("message", {})
        if not isinstance(message_data, dict):
            raise ProviderResponseError("invalid 'choices[0].message' entry")

        content = message_data.get("content")
        if content is not None and not isinstance(content, str):
            raise ProviderResponseError("'message.content' must be a string or null")

        tool_calls = self._parse_tool_calls(message_data.get("tool_calls"))

        finish_reason = first.get("finish_reason")
        if finish_reason is not None and not isinstance(finish_reason, str):
            raise ProviderResponseError("'finish_reason' must be a string or null")

        usage = self._parse_usage(data.get("usage"))

        return ModelResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
        )

    @staticmethod
    def _parse_tool_calls(raw: Any) -> list[ToolCall]:
        if raw is None:
            return []
        if not isinstance(raw, list):
            raise ProviderResponseError("'tool_calls' must be a list")

        result: list[ToolCall] = []
        for index, entry in enumerate(raw, start=1):
            if not isinstance(entry, dict):
                raise ProviderResponseError("invalid 'tool_calls' entry")
            function_data = entry.get("function", {})
            if not isinstance(function_data, dict):
                raise ProviderResponseError("invalid 'tool_calls.function' entry")

            call_id = entry.get("id") or f"tool-call-{index}"
            name = function_data.get("name")
            if not isinstance(name, str) or not name:
                raise ProviderResponseError("tool call is missing a 'name'")
            arguments = function_data.get("arguments", {})
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments) if arguments else {}
                except json.JSONDecodeError as exc:
                    raise ProviderResponseError(
                        f"tool call arguments are not valid JSON: {exc}"
                    ) from exc
            if not isinstance(arguments, dict):
                raise ProviderResponseError("tool call arguments must be a JSON object")

            result.append(ToolCall(id=call_id, name=name, arguments=dict(arguments)))
        return result

    @staticmethod
    def _parse_usage(raw: Any) -> Usage | None:
        if raw is None:
            return None
        if not isinstance(raw, dict):
            raise ProviderResponseError("'usage' must be a JSON object")

        def _int(name: str) -> int:
            value = raw.get(name)
            if value is None:
                return 0
            if isinstance(value, bool) or not isinstance(value, int):
                raise ProviderResponseError(f"usage.{name} must be an integer")
            return value

        return Usage(
            input_tokens=_int("prompt_tokens"),
            output_tokens=_int("completion_tokens"),
            total_tokens=_int("total_tokens"),
        )

    @staticmethod
    def _message_to_payload(message: Message) -> dict[str, Any]:
        result: dict[str, Any] = {"role": message.role}
        if message.content is not None:
            result["content"] = message.content
        elif message.role == "assistant" and message.tool_calls:
            result["content"] = None

        if message.role == "assistant" and message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": json.dumps(call.arguments),
                    },
                }
                for call in message.tool_calls
            ]
        elif message.role == "tool":
            if message.tool_call_id is not None:
                result["tool_call_id"] = message.tool_call_id
            if message.name is not None:
                result["name"] = message.name
        return result

    @staticmethod
    def _tool_to_payload(tool: ToolDefinition) -> dict[str, Any]:
        parameters: dict[str, Any] = dict(tool.parameters) or {
            "type": "object",
            "properties": {},
        }
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": parameters,
            },
        }
