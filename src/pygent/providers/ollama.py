from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pygent.providers.base import Provider
from pygent.types import Message, ModelResponse, ToolCall, ToolDefinition, Usage


class OllamaProvider(Provider):
    """Provider backed by the official Ollama Python client."""

    def __init__(
        self,
        model: str,
        *,
        host: str | None = None,
        client: Any | None = None,
    ) -> None:
        if not model:
            raise ValueError("model must not be empty")

        if client is None:
            try:
                from ollama import AsyncClient
            except ImportError as exc:
                raise ImportError(
                    "Ollama support requires the 'ollama' extra; "
                    "install it with `pip install pygent[ollama]`."
                ) from exc

            client = AsyncClient(host=host) if host is not None else AsyncClient()

        self.model = model
        self.client = client

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ModelResponse:
        response = await self.client.chat(
            model=self.model,
            messages=[self._message_to_ollama(message) for message in messages],
            tools=[self._tool_to_ollama(tool) for tool in tools],
            stream=False,
        )

        response_message = response.message
        tool_calls = [
            ToolCall(
                id=f"ollama-call-{index}",
                name=tool_call.function.name,
                arguments=dict(tool_call.function.arguments),
            )
            for index, tool_call in enumerate(response_message.tool_calls or (), 1)
        ]

        prompt_tokens = getattr(response, "prompt_eval_count", None)
        output_tokens = getattr(response, "eval_count", None)
        usage = None
        if isinstance(prompt_tokens, int) and isinstance(output_tokens, int):
            usage = Usage(
                input_tokens=prompt_tokens,
                output_tokens=output_tokens,
                total_tokens=prompt_tokens + output_tokens,
            )

        return ModelResponse(
            content=response_message.content,
            tool_calls=tool_calls,
            finish_reason=response.done_reason,
            usage=usage,
        )

    @staticmethod
    def _message_to_ollama(message: Message) -> dict[str, Any]:
        result: dict[str, Any] = {"role": message.role}
        if message.content is not None:
            result["content"] = message.content

        if message.role == "assistant" and message.tool_calls:
            result["tool_calls"] = [
                {
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    }
                }
                for call in message.tool_calls
            ]
        elif message.role == "tool" and message.name is not None:
            result["tool_name"] = message.name

        return result

    @staticmethod
    def _tool_to_ollama(tool: ToolDefinition) -> dict[str, Any]:
        parameters: Mapping[str, Any] = tool.parameters or {
            "type": "object",
            "properties": {},
        }
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": dict(parameters),
            },
        }

    async def aclose(self) -> None:
        """Close the underlying Ollama client."""
        await self.client.aclose()
