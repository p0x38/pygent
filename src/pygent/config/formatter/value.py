"""Configuration value formatting helpers."""

from __future__ import annotations

from enum import StrEnum
from numbers import Real
from typing import ClassVar

from pygent.i18n import Translator


class ValueStyle(StrEnum):
    """Display styles for configuration values."""

    DEFAULT = "default"
    BOOLEAN = "boolean"
    ENABLED = "enabled"
    YES_NO = "yes-no"
    SIZE = "size"
    DURATION = "duration"
    NUMBER = "number"
    SENTINEL = "sentinel"


class ByteBase(StrEnum):
    """Bases used for byte-size formatting."""

    DECIMAL = "decimal"
    BINARY = "binary"


class ValueFormatter:
    """Format individual configuration values for display."""

    _SIZE_UNITS: ClassVar[dict[str, int]] = {
        "B": 1,
        "KB": 1_000,
        "MB": 1_000_000,
        "GB": 1_000_000_000,
        "TB": 1_000_000_000_000,
        "PB": 1_000_000_000_000_000,
        "KiB": 2**10,
        "MiB": 2**20,
        "GiB": 2**30,
        "TiB": 2**40,
        "PiB": 2**50,
    }
    _DURATION_UNITS: ClassVar[dict[str, float]] = {
        "ms": 0.001,
        "millisecond": 0.001,
        "milliseconds": 0.001,
        "s": 1,
        "sec": 1,
        "second": 1,
        "seconds": 1,
        "min": 60,
        "minute": 60,
        "minutes": 60,
        "h": 3_600,
        "hour": 3_600,
        "hours": 3_600,
        "d": 86_400,
        "day": 86_400,
        "days": 86_400,
    }

    def __init__(self, translator: Translator) -> None:
        self._translator = translator

    def format(
        self,
        value: object,
        *,
        style: ValueStyle | None = None,
        unit: str | None = None,
        byte_base: ByteBase = ByteBase.DECIMAL,
    ) -> str:
        """Format a configuration value."""
        value = self._coerce(value)

        if value is None:
            return self._translator(
                "config.value.not_set",
                default="Not set",
            )

        if style is None:
            style = self.detect_style(value, unit=unit)

        match style:
            case ValueStyle.BOOLEAN:
                return self.boolean(value)
            case ValueStyle.ENABLED:
                return self.enabled(value)
            case ValueStyle.YES_NO:
                return self.yes_no(value)
            case ValueStyle.SIZE:
                return self.size(value, unit=unit, base=byte_base)
            case ValueStyle.DURATION:
                return self.duration(value, unit=unit)
            case ValueStyle.SENTINEL:
                if value == -1:
                    return self._translator(
                        "config.value.infinite",
                        default="Infinite",
                    )
                return self.number(value, unit=unit)
            case ValueStyle.NUMBER:
                return self.number(value, unit=unit)
            case ValueStyle.DEFAULT:
                return self.default(value, unit=unit)

    @staticmethod
    def _try_int(value: str) -> int | None:
        """Try to parse a string as an integer."""
        normalized = value.strip()
        sign = ""
        digits = normalized
        if normalized[:1] in {"+", "-"}:
            sign = normalized[0]
            digits = normalized[1:]
        if len(digits) > 1 and digits.startswith("0") and digits[1].isdigit():
            return None
        try:
            return int(f"{sign}{digits}")
        except ValueError:
            return None

    @staticmethod
    def _try_float(value: str) -> float | None:
        """Try to parse a string as a float."""
        try:
            return float(value.strip())
        except ValueError:
            return None

    @classmethod
    def _coerce(cls, value: object) -> object:
        """Coerce string values to common scalar types."""
        if not isinstance(value, str):
            return value

        normalized = value.strip()

        if normalized.lower() in {"true", "false"}:
            return normalized.lower() == "true"

        integer = cls._try_int(normalized)
        if integer is not None:
            return integer

        # Preserve integer-looking strings with leading zeroes.
        sign = normalized[:1] if normalized[:1] in {"+", "-"} else ""
        digits = normalized[len(sign) :]
        if len(digits) > 1 and digits.startswith("0") and digits[1].isdigit():
            return value

        decimal = cls._try_float(normalized)
        if decimal is not None:
            return decimal

        return value

    @classmethod
    def detect_style(cls, value: object, *, unit: str | None = None) -> ValueStyle:
        """Detect a suitable display style for a value."""
        if isinstance(value, bool):
            return ValueStyle.BOOLEAN
        if unit in cls._SIZE_UNITS:
            return ValueStyle.SIZE
        if unit in cls._DURATION_UNITS:
            return ValueStyle.DURATION
        if isinstance(value, Real):
            return ValueStyle.NUMBER
        return ValueStyle.DEFAULT

    def default(self, value: object, *, unit: str | None = None) -> str:
        """Format a value without special conversion."""
        result = str(value)
        if unit:
            return f"{result} {unit}"
        if isinstance(value, str):
            return f'"{result}"'
        return result

    @staticmethod
    def boolean(value: object) -> str:
        """Format a value as True or False."""
        if isinstance(value, bool):
            return str(value)
        normalized = str(value).lower()
        if normalized == "true":
            return "True"
        if normalized == "false":
            return "False"
        return str(value)

    def enabled(self, value: object) -> str:
        """Format a value as Enabled or Disabled."""
        normalized = str(value).lower()
        if normalized in {"true", "1", "yes", "enabled"}:
            return self._translator("config.value.enabled", default="Enabled")
        if normalized in {"false", "0", "no", "disabled"}:
            return self._translator("config.value.disabled", default="Disabled")
        return str(value)

    def yes_no(self, value: object) -> str:
        """Format a value as Yes or No."""
        normalized = str(value).lower()
        if normalized in {"true", "1", "yes", "enabled"}:
            return self._translator("config.value.yes", default="Yes")
        if normalized in {"false", "0", "no", "disabled"}:
            return self._translator("config.value.no", default="No")
        return str(value)

    def number(self, value: object, *, unit: str | None = None) -> str:
        """Format a numeric value."""
        if not isinstance(value, Real):
            return self.default(value, unit=unit)
        if isinstance(value, float) and value.is_integer():
            result = str(int(value))
        elif isinstance(value, float):
            result = f"{value:g}"
        else:
            result = str(value)
        return f"{result} {unit}" if unit else result

    def size(
        self,
        value: object,
        *,
        unit: str | None = None,
        base: ByteBase = ByteBase.DECIMAL,
    ) -> str:
        """Format a byte-size value using the requested output base."""
        if not isinstance(value, Real):
            return self.default(value, unit=unit)

        input_unit = unit or "B"
        input_factor = self._SIZE_UNITS.get(input_unit)
        if input_factor is None:
            return self.default(value, unit=unit)

        if base is ByteBase.DECIMAL:
            units = ("B", "KB", "MB", "GB", "TB", "PB")
        else:
            units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")

        factors = {candidate: self._SIZE_UNITS[candidate] for candidate in units}
        size = float(value) * input_factor
        output_unit = "B"
        result = size
        for candidate in units:
            factor = factors[candidate]
            if abs(size) >= factor:
                output_unit = candidate
                result = size / factor
            else:
                break

        if output_unit == "B":
            amount_text = f"{result:g}"
            noun_key = "byte" if abs(result) == 1 else "bytes"
            return (
                f"{amount_text} "
                f"{self._translator(f'config.unit.{noun_key}', default=noun_key)}"
            )
        return f"{int(result) if result.is_integer() else result:g} {output_unit}"

    def _format_duration_unit(self, unit: str, count: int | float) -> str:
        """Format a localized duration unit with singular/plural handling."""
        plural = count != 1
        key = f"config.duration.{unit}s" if plural else f"config.duration.{unit}"
        default = f"{{count}} {unit}s" if plural else f"{{count}} {unit}"

        return self._translator(
            key,
            default=default,
            count=count,
        )

    def duration(self, value: object, *, unit: str | None = None) -> str:
        """Format a duration after converting its input unit to seconds."""
        if not isinstance(value, Real):
            return self.default(value, unit=unit)

        factor = self._DURATION_UNITS.get(unit or "s")
        if factor is None:
            return self.default(value, unit=unit)

        total_seconds = float(value) * factor

        if total_seconds < 0:
            return f"-{self.duration(-total_seconds)}"

        if total_seconds == 0:
            return self._translator(
                "config.duration.zero",
                default="0 seconds",
            )

        days, remainder = divmod(total_seconds, 86_400)
        hours, remainder = divmod(remainder, 3_600)
        minutes, seconds = divmod(remainder, 60)

        parts: list[str] = []

        if days:
            parts.append(self._format_duration_unit("day", int(days)))

        if hours:
            parts.append(self._format_duration_unit("hour", int(hours)))

        if minutes:
            parts.append(self._format_duration_unit("minute", int(minutes)))

        if seconds:
            seconds_value: int | float
            seconds_value = int(seconds) if seconds.is_integer() else seconds

            parts.append(self._format_duration_unit("second", seconds_value))

        return " ".join(parts)
