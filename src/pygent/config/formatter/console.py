"""Console configuration formatter."""

from __future__ import annotations

from collections.abc import Mapping

from .base import ConfigFormatter


class ConsoleFormatter(ConfigFormatter):
    """Format configuration for human-readable terminal output."""

    @staticmethod
    def _source_suffix(from_config: bool) -> str:
        """Return a suffix describing the configuration source."""
        return " (via config file)" if from_config else ""

    @staticmethod
    def _keep_alive(value: str) -> str:
        """Format an Ollama keep-alive value."""
        return "infinite" if value == "-1" else value

    @staticmethod
    def _library(value: str) -> str:
        """Format an Ollama LLM library."""
        return value.upper()

    @staticmethod
    def _vulkan(value: str) -> str:
        """Format an Ollama Vulkan setting."""
        normalized = value.lower()

        if normalized in {"0", "false", "no", "disabled"}:
            return "Disabled"

        if normalized in {"1", "true", "yes", "enabled"}:
            return "Enabled"

        return value

    def format(self, config: Mapping[str, str]) -> str:
        """Format the supplied configuration."""
        return self.all(config)

    @classmethod
    def all(
        cls,
        values: Mapping[str, str],
        *,
        config_values: set[str] | None = None,
    ) -> str:
        """Format all supported configuration sections."""
        configured = config_values or set()
        sections: list[str] = []

        pygent_values = {
            name: value for name, value in values.items() if name.startswith("PYGENT_")
        }

        ollama_values = {
            name: value for name, value in values.items() if name.startswith("OLLAMA_")
        }

        openrouter_values = {
            name: value
            for name, value in values.items()
            if name.startswith("OPENROUTER_")
        }

        if pygent_values:
            sections.append(
                cls.default(
                    pygent_values.get("PYGENT_PROVIDER", "ollama"),
                    pygent_values.get(
                        "PYGENT_MODEL",
                        "qwen2.5-coder:3b",
                    ),
                    provider_from_config="PYGENT_PROVIDER" in configured,
                    model_from_config="PYGENT_MODEL" in configured,
                )
            )

        if ollama_values:
            sections.append(
                cls.ollama(
                    ollama_values,
                    config_values=configured,
                )
            )

        if openrouter_values:
            sections.append(
                cls.openrouter(
                    openrouter_values,
                    config_values=configured,
                )
            )

        return "\n\n".join(sections)

    @classmethod
    def default(
        cls,
        provider: str,
        model: str,
        *,
        provider_from_config: bool = False,
        model_from_config: bool = False,
    ) -> str:
        """Format default provider configuration."""
        return "\n".join(
            [
                "[Default]",
                (f"Provider: {provider}{cls._source_suffix(provider_from_config)}"),
                (f"Model: {model}{cls._source_suffix(model_from_config)}"),
            ]
        )

    @classmethod
    def ollama(
        cls,
        values: Mapping[str, str],
        *,
        config_values: set[str] | None = None,
    ) -> str:
        """Format Ollama configuration."""
        configured = config_values or set()

        def get(name: str) -> tuple[str, bool]:
            return (
                values.get(name, "Not set"),
                name in configured,
            )

        keep_alive, keep_alive_config = get("OLLAMA_KEEP_ALIVE")
        library, library_config = get("OLLAMA_LLM_LIBRARY")
        max_loaded, max_loaded_config = get("OLLAMA_MAX_LOADED_MODELS")
        parallel, parallel_config = get("OLLAMA_NUM_PARALLEL")
        vulkan, vulkan_config = get("OLLAMA_VULKAN")

        return "\n".join(
            [
                "[Ollama]",
                (
                    "Keep alive: "
                    f"{cls._keep_alive(keep_alive)}"
                    f"{cls._source_suffix(keep_alive_config)}"
                ),
                (
                    "LLM Library: "
                    f"{cls._library(library)}"
                    f"{cls._source_suffix(library_config)}"
                ),
                (
                    "Max loaded models: "
                    f"{max_loaded}"
                    f"{cls._source_suffix(max_loaded_config)}"
                ),
                (f"Parallel requests: {parallel}{cls._source_suffix(parallel_config)}"),
                (f"Vulkan: {cls._vulkan(vulkan)}{cls._source_suffix(vulkan_config)}"),
            ]
        )

    @classmethod
    def openrouter(
        cls,
        values: Mapping[str, str],
        *,
        config_values: set[str] | None = None,
    ) -> str:
        """Format OpenRouter configuration."""
        configured = config_values or set()

        lines = ["[OpenRouter]"]

        fields = (
            ("OPENROUTER_API_KEY", "API key"),
            ("OPENROUTER_BASE_URL", "Base URL"),
        )

        for name, label in fields:
            if name not in values:
                continue

            value = values[name]

            if "KEY" in name:
                value = "********"

            lines.append(f"{label}: {value}{cls._source_suffix(name in configured)}")

        return "\n".join(lines)
