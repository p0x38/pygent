from __future__ import annotations

from pygent.config import ConsoleFormatter
from pygent.config.formatter.value import ByteBase, ValueFormatter, ValueStyle
from pygent.i18n import load_translator


def formatter(locale: str = "en") -> ConsoleFormatter:
    return ConsoleFormatter(load_translator(locale))


def test_value_formatter_detects_units_before_number() -> None:
    values = ValueFormatter(load_translator())

    assert values.detect_style(1024, unit="B") is ValueStyle.SIZE
    assert values.detect_style(2, unit="s") is ValueStyle.DURATION
    assert values.detect_style(2, unit="ms") is ValueStyle.DURATION
    assert values.detect_style(2) is ValueStyle.NUMBER


def test_value_formatter_coerces_common_scalars() -> None:
    values = ValueFormatter(load_translator())

    assert values.format("true") == "True"
    assert values.format("42") == "42"
    assert values.format("3.5") == "3.5"
    assert values.format("08") == '"08"'
    assert values.format("ollama") == '"ollama"'


def test_value_formatter_formats_byte_sizes() -> None:
    values = ValueFormatter(load_translator())

    assert values.format(1, style=ValueStyle.SIZE, unit="B") == "1 byte"
    assert values.format(2, style=ValueStyle.SIZE, unit="B") == "2 bytes"
    assert values.format(1000, style=ValueStyle.SIZE, unit="B") == "1 KB"
    assert values.format(1000, style=ValueStyle.SIZE, unit="KB") == "1 MB"
    assert values.format(1024, style=ValueStyle.SIZE, unit="B", byte_base=ByteBase.BINARY) == "1 KiB"
    assert values.format(1024, style=ValueStyle.SIZE, unit="KiB", byte_base=ByteBase.BINARY) == "1 MiB"


def test_value_formatter_converts_duration_units() -> None:
    values = ValueFormatter(load_translator())

    assert values.format(1000, style=ValueStyle.DURATION, unit="ms") == "1 second"
    assert values.format(90, style=ValueStyle.DURATION, unit="s") == "1 minute 30 seconds"
    assert values.format(2, style=ValueStyle.DURATION, unit="min") == "2 minutes"


def test_value_formatter_localizes_values_and_durations() -> None:
    values = ValueFormatter(load_translator("ja"))

    assert values.format(True, style=ValueStyle.ENABLED) == "有効"
    assert values.format(False, style=ValueStyle.YES_NO) == "いいえ"
    assert values.format(1, style=ValueStyle.SIZE, unit="B") == "1 バイト"
    assert values.format(120, style=ValueStyle.DURATION, unit="s") == "2分"


def test_console_formatter_escapes_rich_section_markup() -> None:
    output = formatter().toml(
        {
            "default": {"provider": "ollama"},
            "chat": {"syntax": {"enabled": True}},
        }
    )

    assert "\\[default]" in output
    assert "\\[chat.syntax]" in output
    assert 'provider: "ollama" (via toml)' in output
    assert "enabled: True (via toml)" in output


def test_console_formatter_localizes_sections_and_fields() -> None:
    output = formatter("ja").environment(
        {
            "OLLAMA_KEEP_ALIVE": "-1",
            "OLLAMA_VULKAN": "false",
        }
    )

    assert "Ollama" in output
    assert "キープアライブ" in output
    assert "Vulkan" in output
    assert "無効" in output
    assert "環境変数" in output
