import json
from datetime import date

import pytest

from arth.core.i18n import (
    BABEL_LOCALE,
    LAKH_CRORE,
    LOCALES,
    NATIVE_ZERO,
    LocaleError,
    format_date,
    format_money,
    group_indian,
    to_native_digits,
)
from arth.core.paths import CONTRACTS_DIR

CASES = json.loads((CONTRACTS_DIR / "fixtures" / "format_cases.json").read_text(encoding="utf-8"))

SPEC = CASES["locales"]
NON_LATIN = tuple(loc for loc, row in SPEC.items() if row["nativeZero"] is not None)


def _case_id(c: dict) -> str:
    compact = "-compact" if c.get("compact") else ""
    native = "-native" if c.get("native") else ""
    return f"{c['locale']}-{c['paise']}{compact}{native}"


@pytest.mark.parametrize("case", CASES["money"], ids=_case_id)
def test_money_matches_shared_fixture(case: dict) -> None:
    got = format_money(
        case["paise"], case["locale"], compact=case.get("compact", False), native=case.get("native", False)
    )
    assert got == case["expected"]


@pytest.mark.parametrize("case", CASES["dates"], ids=lambda c: c["locale"])
def test_dates_match_shared_fixture(case: dict) -> None:
    assert format_date(date.fromisoformat(case["date"]), case["locale"]) == case["expected"]


def test_code_tables_equal_fixture_locales_section() -> None:
    assert list(LOCALES) == list(SPEC)
    assert set(LAKH_CRORE) == set(BABEL_LOCALE) == set(SPEC)
    for locale, row in SPEC.items():
        assert LAKH_CRORE[locale] == (row["lakh"], row["crore"])
        assert BABEL_LOCALE[locale] == row["babel"]
        assert NATIVE_ZERO.get(locale) == row["nativeZero"]
    assert set(NATIVE_ZERO) == set(NON_LATIN)


@pytest.mark.parametrize("locale", LOCALES)
def test_fixture_covers_every_locale(locale: str) -> None:
    mine = [c for c in CASES["money"] if c["locale"] == locale]
    lakh, crore = SPEC[locale]["lakh"], SPEC[locale]["crore"]
    assert any(not c.get("compact") and not c.get("native") for c in mine)
    assert any(c.get("compact") and c["expected"].endswith(f" {lakh}") for c in mine)
    assert any(c.get("compact") and c["expected"].endswith(f" {crore}") for c in mine)
    if locale in NON_LATIN:
        assert any(c.get("native") for c in mine)


@pytest.mark.parametrize("locale", LOCALES)
def test_date_has_weekday_day_and_month(locale: str) -> None:
    # Non-Latin names may differ from the web build (CLDR drift); only structure is asserted.
    weekday, rest = format_date(date(2026, 10, 29), locale).split(", ", 1)
    assert weekday
    assert rest.startswith("29 ")
    assert rest[3:].strip()


@pytest.mark.parametrize("locale", NON_LATIN)
def test_native_date_uses_native_digits(locale: str) -> None:
    assert to_native_digits("29", locale) in format_date(date(2026, 10, 29), locale, native=True)


def test_date_single_digit_day_has_no_padding() -> None:
    assert format_date(date(2026, 11, 5), "en").split(", ", 1)[1].startswith("5 ")


def test_unknown_locale_is_rejected() -> None:
    with pytest.raises(LocaleError, match="unsupported locale 'fr'"):
        format_money(100, "fr")
    with pytest.raises(LocaleError):
        format_money(100_000_00, "fr", compact=True)
    with pytest.raises(LocaleError):
        format_date(date(2026, 10, 29), "fr")
    with pytest.raises(LocaleError):
        to_native_digits("29", "fr")


@pytest.mark.parametrize("bad", [True, 1.5, 100.0, "100", None])
def test_money_requires_int(bad: object) -> None:
    with pytest.raises(TypeError, match="paise must be an int"):
        format_money(bad, "en")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("n", "expected"),
    [(0, "0"), (999, "999"), (1000, "1,000"), (100000, "1,00,000"), (12345678, "1,23,45,678")],
)
def test_group_indian(n: int, expected: str) -> None:
    assert group_indian(n) == expected
