"""Configuration value formatting helpers."""

from __future__ import annotations

from enum import StrEnum
from numbers import Real

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


class ByteBase(StrEnum):
    """Bases used for byte-size formatting."""

    DECIMAL = "decimal"
    BINARY = "binary"


class ValueFormatter:
    """Format individual configuration values for display."""

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
                return self.size(
                    value,
                    unit=unit,
                    base=byte_base,
                )

            case ValueStyle.DURATION:
                return self.duration(value)

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

        decimal = cls._try_float(normalized)

        if decimal is not None:
            return decimal

        return value

    @staticmethod
    def detect_style(
        value: object,
        *,
        unit: str | None = None,
    ) -> ValueStyle:
        """Detect a suitable display style for a value."""
        if isinstance(value, bool):
            return ValueStyle.BOOLEAN

        if unit in {
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
            "PB",
            "KiB",
            "MiB",
            "GiB",
            "TiB",
            "PiB",
        }:
            return ValueStyle.SIZE

        if unit in {
            "s",
            "sec",
            "second",
            "seconds",
            "ms",
            "millisecond",
            "milliseconds",
            "min",
            "minute",
            "minutes",
            "h",
            "hour",
            "hours",
            "d",
            "day",
            "days",
        }:
            return ValueStyle.DURATION

        if isinstance(value, Real):
            return ValueStyle.NUMBER

        return ValueStyle.DEFAULT

    def default(
        self,
        value: object,
        *,
        unit: str | None = None,
    ) -> str:
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
        if isinstance(value, bool):
            key = "enabled" if value else "disabled"

            return self._translator(
                f"config.value.{key}",
                default=key.capitalize(),
            )

        normalized = str(value).lower()

        if normalized in {"true", "1", "yes", "enabled"}:
            return self._translator(
                "config.value.enabled",
                default="Enabled",
            )

        if normalized in {"false", "0", "no", "disabled"}:
            return self._translator(
                "config.value.disabled",
                default="Disabled",
            )

        return str(value)

    def yes_no(self, value: object) -> str:
        """Format a value as Yes or No."""
        if isinstance(value, bool):
            key = "yes" if value else "no"

            return self._translator(
                f"config.value.{key}",
                default=key.capitalize(),
            )

        normalized = str(value).lower()

        if normalized in {"true", "1", "yes", "enabled"}:
            return self._translator(
                "config.value.yes",
                default="Yes",
            )

        if normalized in {"false", "0", "no", "disabled"}:
            return self._translator(
                "config.value.no",
                default="No",
            )

        return str(value)

    def number(
        self,
        value: object,
        *,
        unit: str | None = None,
    ) -> str:
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
        """Format a byte-size value."""
        if not isinstance(value, Real):
            return self.default(value, unit=unit)

        if base is ByteBase.DECIMAL:
            units = ("B", "KB", "MB", "GB", "TB", "PB")
            factors = {
                "B": 1,
                "KB": 1_000,
                "MB": 1_000_000,
                "GB": 1_000_000_000,
                "TB": 1_000_000_000_000,
                "PB": 1_000_000_000_000_000,
            }
        else:
            units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")
            factors = {
                "B": 1,
                "KiB": 2**10,
                "MiB": 2**20,
                "GiB": 2**30,
                "TiB": 2**40,
                "PiB": 2**50,
            }

        input_unit = unit or "B"

        if input_unit not in factors:
            return self.default(value, unit=unit)

        size = float(value) * factors[input_unit]

        output_unit = units[0]
        result = size

        for candidate in units:
            factor = factors[candidate]

            if abs(size) >= factor:
                output_unit = candidate
                result = size / factor
            else:
                break

        if output_unit == "B":
            amount = int(result) if result.is_integer() else result
            noun_key = "byte" if abs(amount) == 1 else "bytes"

            amount_text = (
                str(int(amount))
                if isinstance(amount, float) and amount.is_integer()
                else f"{amount:g}"
            )

            return (
                f"{amount_text} "
                f"{self._translator(f'config.unit.{noun_key}', default=noun_key)}"
            )

        if result.is_integer():
            return f"{int(result)} {output_unit}"

        return f"{result:g} {output_unit}"

    def duration(self, value: object) -> str:
        """Format a duration in seconds."""
        if not isinstance(value, Real):
            return self.default(value)

        total_seconds = float(value)

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
            parts.append(
                self._translator(
                    "config.duration.day",
                    default="{count} day",
                    count=int(days),
                )
            )

        if hours:
            parts.append(
                self._translator(
                    "config.duration.hour",
                    default="{count} hour",
                    count=int(hours),
                )
            )

        if minutes:
            parts.append(
                self._translator(
                    "config.duration.minute",
                    default="{count} minute",
                    count=int(minutes),
                )
            )

        if seconds:
            seconds_text = str(int(seconds)) if seconds.is_integer() else f"{seconds:g}"

            parts.append(
                self._translator(
                    "config.duration.second",
                    default="{count} second",
                    count=seconds_text,
                )
            )

        return " ".join(parts)
