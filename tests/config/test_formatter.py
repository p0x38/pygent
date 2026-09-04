from pygent.config import ConsoleFormatter


def test_ollama_formatter() -> None:
    values = {
        "OLLAMA_KEEP_ALIVE": "-1",
        "OLLAMA_LLM_LIBRARY": "cpu",
        "OLLAMA_MAX_LOADED_MODELS": "1",
        "OLLAMA_NUM_PARALLEL": "8",
        "OLLAMA_VULKAN": "0",
    }

    assert ConsoleFormatter.ollama(values) == "\n".join(
        [
            "[Ollama]",
            "Keep alive: infinite",
            "LLM Library: CPU",
            "Max loaded models: 1",
            "Parallel requests: 8",
            "Vulkan: Disabled",
        ]
    )


def test_openrouter_formatter() -> None:
    values = {
        "OPENROUTER_API_KEY": "secret",
        "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
    }

    result = ConsoleFormatter.openrouter(values)

    assert result == "\n".join(
        [
            "[OpenRouter]",
            "API key: ********",
            "Base URL: https://openrouter.ai/api/v1",
        ]
    )


def test_openrouter_formatter_hides_api_key() -> None:
    values = {
        "OPENROUTER_API_KEY": "super-secret",
    }

    result = ConsoleFormatter.openrouter(values)

    assert "super-secret" not in result
    assert "API key: ********" in result


def test_all_formatter() -> None:
    values = {
        "PYGENT_PROVIDER": "ollama",
        "PYGENT_MODEL": "qwen2.5-coder:3b",
        "OLLAMA_KEEP_ALIVE": "-1",
        "OLLAMA_LLM_LIBRARY": "cpu",
        "OPENROUTER_API_KEY": "secret",
    }

    result = ConsoleFormatter.all(values)

    assert "[Default]" in result
    assert "[Ollama]" in result
    assert "[OpenRouter]" in result
    assert "Provider: ollama" in result
    assert "Model: qwen2.5-coder:3b" in result
    assert "Keep alive: infinite" in result
    assert "API key: ********" in result
    assert "secret" not in result
