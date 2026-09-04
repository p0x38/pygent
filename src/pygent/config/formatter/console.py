"""Console configuration formatter."""

from __future__ import annotations

from collections.abc import Mapping

from ...i18n.translator import Translator
from .base import ConfigFormatter
from .labels import ConfigLabels
from .value import ValueFormatter, ValueStyle

type TomlValue = str | int | float | bool | list["TomlValue"] | dict[str, "TomlValue"]


class ConsoleFormatter(ConfigFormatter):
    """Format configuration for human-readable terminal output."""

    def __init__(self, translator: Translator) -> None:
        self._translator = translator
        self._labels = ConfigLabels(translator)
        self._values = ValueFormatter(translator)

    @staticmethod
    def _section(name: str) -> str:
        """Format a literal TOML section header for Rich."""
        return rf"[bold cyan]\[{name}][/bold cyan]"

    def _source_suffix(self, source: str) -> str:
        """Return a configuration source suffix."""
        return self._translator(
            "config.source_suffix.default",
            default=" (via {source})",
            source=source,
        )

    def format(self, config: Mapping[str, str]) -> str:
        """Format configuration environment variables."""
        return self.environment(config)

    def toml(self, values: Mapping[str, TomlValue]) -> str:
        """Format a TOML configuration mapping."""
        lines: list[str] = []

        def visit(table: Mapping[str, TomlValue], prefix: str = "") -> None:
            scalar_lines: list[str] = []
            nested: list[tuple[str, dict[str, TomlValue]]] = []

            for key, value in table.items():
                if isinstance(value, dict):
                    nested.append((key, value))
                else:
                    scalar_lines.append(self._format_toml_field(key, value))

            if prefix:
                if lines:
                    lines.append("")
                lines.append(self._section(self._section_name(prefix)))

            lines.extend(scalar_lines)

            for key, child in nested:
                child_prefix = f"{prefix}.{key}" if prefix else key
                visit(child, child_prefix)

        visit(values)
        return "\n".join(lines)

    def _section_name(self, path: tuple[str, ...] | str) -> str:
        """Translate and format a configuration section path."""
        if isinstance(path, str):
            path = tuple(path.split("."))

        return " > ".join(self._labels.section(part) for part in path)

    def _format_toml_field(self, key: str, value: TomlValue) -> str:
        """Format one TOML field."""
        return (
            f"{self._labels.field(key)}: "
            f"{self._values.format(value)}"
            f"{self._source_suffix(self._labels.source('toml'))}"
        )

    def environment(self, values: Mapping[str, str]) -> str:
        """Format configuration environment variables."""
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
            sections.append(self.pygent(pygent_values))
        if ollama_values:
            sections.append(self.ollama(ollama_values))
        if openrouter_values:
            sections.append(self.openrouter(openrouter_values))

        return "\n\n".join(sections)

    def pygent(self, values: Mapping[str, str]) -> str:
        """Format Pygent environment configuration."""
        provider = values.get("PYGENT_PROVIDER", "ollama")
        model = values.get("PYGENT_MODEL", "qwen2.5-coder:3b")
        source = self._labels.source("env")
        return "\n".join(
            [
                self._section(self._labels.section("pygent")),
                (
                    f"{self._labels.field('provider')}: "
                    f"{self._values.format(provider)}"
                    f"{self._source_suffix(source)}"
                ),
                (
                    f"{self._labels.field('model')}: "
                    f"{self._values.format(model)}"
                    f"{self._source_suffix(source)}"
                ),
            ]
        )

    def all(
        self, environment: Mapping[str, str], config: Mapping[str, TomlValue]
    ) -> str:
        """Format environment variables and configuration file values."""
        sections: list[str] = []
        if environment:
            sections.append(self.environment(environment))
        if config:
            sections.append(self.toml(config))
        return "\n\n".join(sections)

    def ollama(self, values: Mapping[str, str]) -> str:
        """Format Ollama environment configuration."""

        def get(name: str) -> str:
            return values.get(name, "Not set")

        source = self._labels.source("env")
        return "\n".join(
            [
                self._section(self._labels.section("ollama")),
                (
                    f"{self._labels.field('keep_alive')}: "
                    f"{self._values.format(get('OLLAMA_KEEP_ALIVE'))}"
                    f"{self._source_suffix(source)}"
                ),
                (
                    f"{self._labels.field('llm_library')}: "
                    f"{self._values.format(get('OLLAMA_LLM_LIBRARY'))}"
                    f"{self._source_suffix(source)}"
                ),
                (
                    f"{self._labels.field('max_loaded_models')}: "
                    f"{self._values.format(get('OLLAMA_MAX_LOADED_MODELS'))}"
                    f"{self._source_suffix(source)}"
                ),
                (
                    f"{self._labels.field('parallel_requests')}: "
                    f"{self._values.format(get('OLLAMA_NUM_PARALLEL'))}"
                    f"{self._source_suffix(source)}"
                ),
                (
                    f"{self._labels.field('vulkan')}: "
                    f"{self._values.format(get('OLLAMA_VULKAN'), style=ValueStyle.ENABLED)}"
                    f"{self._source_suffix(source)}"
                ),
            ]
        )

    def openrouter(self, values: Mapping[str, str]) -> str:
        """Format OpenRouter environment configuration."""
        lines = [self._section(self._labels.section("openrouter"))]
        source = self._labels.source("env")
        fields = (
            ("OPENROUTER_API_KEY", "api_key"),
            ("OPENROUTER_BASE_URL", "base_url"),
        )
        for name, label_key in fields:
            if name not in values:
                continue
            value = "********" if "KEY" in name else values[name]
            lines.append(
                f"{self._labels.field(label_key)}: "
                f"{self._values.format(value)}"
                f"{self._source_suffix(source)}"
            )
        return "\n".join(lines)
