from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import httpx

from pygent.config import getenv
from pygent.providers.compatible import OpenAICompatibleProvider

from ..types.model import Message


class LMStudioProvider(OpenAICompatibleProvider):
    """Provider for models served by LM Studio."""

    DEFAULT_BASE_URL = "http://localhost:1234/v1"

    def __init__(
            self,
            model: str,
            *,
            base_url: str = DEFAULT_BASE_URL,
            api_key: str | None = None,
            client: httpx.AsyncClient | None = None,
            timeout: float = 60.0,
            extra_body: Mapping[str, Any] | None = None,
            default_headers: Mapping[str, str] | None = None,
            message_formatter: Callable[[Message], str] | None = None,
            include_name_metadata: bool = True,
    ) -> None:
        if api_key is None:
            api_key = getenv("LM_STUDIO_API_KEY")

        super().__init__(
            model,
            base_url=base_url,
            api_key=api_key,
            client=client,
            timeout=timeout,
            extra_body=extra_body,
            default_headers=default_headers,
            message_formatter=message_formatter,
            include_name_metadata=include_name_metadata,
        )