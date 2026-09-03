from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from pygent.config import getenv
from pygent.providers.compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    """Provider for the OpenRouter OpenAI-compatible API.

    OpenRouter re-uses the OpenAI ``/chat/completions`` payload, but exposes a
    free-form ``models`` field and accepts extra routing hints through
    ``extra_body`` (``transforms``, ``route``, etc.).
    """

    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_TITLE_HEADER = "Pygent"

    def __init__(
        self,
        model: str,
        *,
        api_key: str | None = None,
        site_url: str | None = None,
        app_name: str | None = DEFAULT_TITLE_HEADER,
        client: httpx.AsyncClient | None = None,
        timeout: float = 60.0,
        extra_body: Mapping[str, Any] | None = None,
    ) -> None:
        if api_key is None:
            api_key = getenv("OPENROUTER_API_KEY")

        headers: dict[str, str] = {}
        if site_url is not None:
            headers["HTTP-Referer"] = site_url
        if app_name is not None:
            headers["X-Title"] = app_name

        super().__init__(
            model,
            base_url=self.DEFAULT_BASE_URL,
            api_key=api_key,
            client=client,
            timeout=timeout,
            extra_body=extra_body,
            default_headers=headers,
        )
