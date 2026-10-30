"""Locales and formatting shared with the web app (spec Part I6).

Money always uses Indian grouping (₹1,12,400), whatever the locale; digits are Latin unless
`native=True`. Keep this file in lockstep with frontend/lib/format.ts via
contracts/fixtures/format_cases.json.

Contract: money is byte-identical on both sides. Dates are rendered by whichever side shows them
(frontend for screens, backend for messages/PDFs) and are only required to be byte-identical for
`en` and `hi-Latn`: Babel and Node ICU ship different CLDR versions, so non-Latin month/weekday
names may differ. Other locales are tested per side for structure (weekday, day, month) only.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from types import MappingProxyType
from typing import Final, Literal, get_args

from babel.dates import format_date as _babel_format_date

Locale = Literal["hi", "en", "hi-Latn", "mr", "ta", "bn", "gu", "te"]
LOCALES: Final[tuple[str, ...]] = get_args(Locale)

BABEL_LOCALE: Final[Mapping[str, str]] = MappingProxyType(
    {
        "hi": "hi_IN",
        "en": "en_IN",
        "hi-Latn": "en_IN",
        "mr": "mr_IN",
        "ta": "ta_IN",
        "bn": "bn_IN",
        "gu": "gu_IN",
        "te": "te_IN",
    }
)
NATIVE_ZERO: Final[Mapping[str, int]] = MappingProxyType(
    {"hi": 0x0966, "mr": 0x0966, "bn": 0x09E6, "ta": 0x0BE6, "gu": 0x0AE6, "te": 0x0C66}
)
LAKH_CRORE: Final[Mapping[str, tuple[str, str]]] = MappingProxyType(
    {
        "en": ("lakh", "crore"),
        "hi-Latn": ("lakh", "crore"),
        "hi": ("लाख", "करोड़"),
        "mr": ("लाख", "कोटी"),
        "ta": ("லட்சம்", "கோடி"),
        "bn": ("লাখ", "কোটি"),
        "gu": ("લાખ", "કરોડ"),
        "te": ("లక్ష", "కోటి"),
    }
)
LAKH: Final = 100_000
CRORE: Final = 10_000_000


class LocaleError(ValueError):
    """Unsupported locale."""


def _check(locale: str) -> None:
    if locale not in LOCALES:
        raise LocaleError(f"unsupported locale {locale!r}; use one of {', '.join(LOCALES)}")


def group_indian(n: int) -> str:
    digits = str(n)
    if len(digits) <= 3:
        return digits
    head, tail = digits[:-3], digits[-3:]
    pairs: list[str] = []
    while len(head) > 2:
        pairs.insert(0, head[-2:])
        head = head[:-2]
    if head:
        pairs.insert(0, head)
    return ",".join(pairs) + "," + tail


def to_native_digits(text: str, locale: str) -> str:
    _check(locale)
    zero = NATIVE_ZERO.get(locale)
    if zero is None:
        return text
    return "".join(chr(zero + int(ch)) if ch in "0123456789" else ch for ch in text)


def _compact_round(rupees: int) -> tuple[int, int]:
    """Round whole rupees (>= 1 lakh) half-up to one decimal of lakh or crore.

    Returns (tenths, unit). Compact output deliberately drops paise: at lakh scale they are noise.
    99.95+ lakh would print as "100 lakh", so it is promoted to crore instead.
    """
    unit = CRORE if rupees >= CRORE else LAKH
    tenths = (rupees * 10 + unit // 2) // unit
    if unit == LAKH and tenths >= 1000:
        unit = CRORE
        tenths = (rupees * 10 + unit // 2) // unit
    return tenths, unit


def format_money(paise: int, locale: str, *, compact: bool = False, native: bool = False) -> str:
    if isinstance(paise, bool) or not isinstance(paise, int):
        raise TypeError("paise must be an int")
    _check(locale)
    sign = "-" if paise < 0 else ""
    rupees, rest = divmod(abs(paise), 100)
    suffix = ""
    if compact and rupees >= LAKH:
        tenths, unit = _compact_round(rupees)
        word = LAKH_CRORE[locale][1 if unit == CRORE else 0]
        whole, frac = divmod(tenths, 10)
        text = group_indian(whole) + (f".{frac}" if frac else "")
        suffix = f" {word}"
    else:
        text = group_indian(rupees) + (f".{rest:02d}" if rest else "")
    if native:
        text = to_native_digits(text, locale)
    return f"{sign}₹{text}{suffix}"


def format_date(value: date, locale: str, *, native: bool = False) -> str:
    """Short weekday, day and month: 'Thu, 29 Oct'. Same composition on the web side."""
    _check(locale)
    babel_locale = BABEL_LOCALE[locale]
    weekday = _babel_format_date(value, format="EEE", locale=babel_locale)
    month = _babel_format_date(value, format="MMM", locale=babel_locale)
    text = f"{weekday}, {value.day} {month}"
    return to_native_digits(text, locale) if native else text
