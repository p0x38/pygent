from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from pygent.config import getenv
from pygent.providers.compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    """Provider for the OpenAI API.

    Inherits request/response handling from :class:`OpenAICompatibleProvider`
    and simply pins the default base URL and reads ``OPENAI_API_KEY`` when no
    API key is supplied.
    """

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(
        self,
        model: str,
        *,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = 60.0,
        extra_body: Mapping[str, Any] | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        if api_key is None:
            api_key = getenv("OPENAI_API_KEY")
        super().__init__(
            model,
            base_url=self.DEFAULT_BASE_URL,
            api_key=api_key,
            client=client,
            timeout=timeout,
            extra_body=extra_body,
            default_headers=default_headers,
        )
