from pathlib import Path

from .translator import Translator

_LOCALE_DIR = Path(__file__).with_name("locales")


def load_translator(
    locale: str = "en",
) -> Translator:
    """Load a translator for a locale with English fallback."""
    fallback = Translator.from_file(_LOCALE_DIR / "en.toml")

    if locale == "en":
        return fallback

    return Translator.from_file(
        _LOCALE_DIR / f"{locale}.toml",
        fallback=fallback,
    )
