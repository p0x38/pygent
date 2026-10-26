from __future__ import annotations

import pytest

from pygent.providers.lmstudio import LMStudioProvider


@pytest.mark.asyncio
async def test_uses_default_base_url_and_environment_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LM_STUDIO_API_KEY", "test-key")

    provider = LMStudioProvider("local-model")

    try:
        assert provider.base_url == "http://localhost:1234/v1"
        assert provider.api_key == "test-key"
        assert str(provider.client.base_url).rstrip("/") == (
            "http://localhost:1234/v1"
        )
        assert provider.client.headers["authorization"] == "Bearer test-key"
    finally:
        await provider.aclose()


def test_allows_custom_base_url() -> None:
    provider = LMStudioProvider(
        "local-model",
        base_url="http://127.0.0.1:4321/v1",
    )

    assert provider.base_url == "http://127.0.0.1:4321/v1"