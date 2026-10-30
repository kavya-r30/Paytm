from decimal import Decimal, Inexact, Rounded, localcontext
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arth.core.money import MoneyError, div_round_half_even, to_paise
from arth.core.qty import QtyError, line_amount, to_milli

BIG = 10**40


def _ref_half_even(n: int, d: int) -> int:
    return round(Fraction(n, d))  # Fraction.__round__ rounds half-to-even


def test_to_paise_exact() -> None:
    assert to_paise("62") == 6200
    assert to_paise("62.5") == 6250
    assert to_paise(Decimal("0.01")) == 1
    assert to_paise(1600) == 160000


def test_to_paise_negative() -> None:
    assert to_paise("-62.5") == -6250
    assert to_paise(-3) == -300
    assert to_paise("-0") == 0


def test_to_paise_rejects_sub_paise() -> None:
    with pytest.raises(MoneyError):
        to_paise("1.005")


def test_half_even_rounding() -> None:
    assert div_round_half_even(5, 2) == 2
    assert div_round_half_even(7, 2) == 4
    assert div_round_half_even(-5, 2) == -2


def test_div_round_half_even_ties_and_signs() -> None:
    assert div_round_half_even(1, 2) == 0
    assert div_round_half_even(3, 2) == 2
    assert div_round_half_even(-3, 2) == -2
    assert div_round_half_even(5, -2) == -2
    assert div_round_half_even(-5, -2) == 2
    assert div_round_half_even(10**40 + 1, 2) == 5 * 10**39  # beyond default Decimal precision


def test_div_round_half_even_zero_denominator() -> None:
    with pytest.raises(ZeroDivisionError):
        div_round_half_even(1, 0)


@given(st.integers(-BIG, BIG), st.integers(-BIG, BIG).filter(lambda d: d != 0))
def test_div_round_half_even_matches_fraction_reference(n: int, d: int) -> None:
    assert div_round_half_even(n, d) == _ref_half_even(n, d)


@given(st.integers(-BIG, BIG), st.integers(1, 10**20))
def test_div_round_half_even_exact_ties(k: int, d: int) -> None:
    # (2k+1)*d / (2d) is exactly k + 1/2
    assert div_round_half_even((2 * k + 1) * d, 2 * d) == _ref_half_even((2 * k + 1) * d, 2 * d)


def test_sugar_half_kilo_at_48_per_kg_is_24_rupees() -> None:
    # Billing screen: "Sugar, loose 0.5 kg · ₹24" at ₹48/kg
    assert line_amount(unit_price_paise=4800, qty_milli=to_milli("0.5")) == 2400


def test_line_amount_half_even_ties() -> None:
    assert line_amount(1, 500) == 0
    assert line_amount(1, 1500) == 2
    assert line_amount(1, 2500) == 2
    assert line_amount(-1, 1500) == -2


def test_to_milli_exact_and_negative() -> None:
    assert to_milli("0.5") == 500
    assert to_milli("-1.250") == -1250
    assert to_milli(3) == 3000
    assert to_milli(Decimal("0.001")) == 1
    assert to_milli("-0") == 0


def test_to_milli_rejects_more_than_three_decimals() -> None:
    with pytest.raises(QtyError):
        to_milli("0.0005")


@given(st.integers(0, 10_000_000))
def test_one_unit_costs_unit_price(price: int) -> None:
    assert line_amount(price, 1000) == price


@given(st.integers(0, 1_000_000), st.integers(0, 100_000))
def test_line_amount_is_monotonic_in_quantity(price: int, qty: int) -> None:
    assert line_amount(price, qty + 1) >= line_amount(price, qty)


@given(st.integers(-(10**12), 10**12))
def test_paise_round_trip_through_rupee_string(paise: int) -> None:
    rupees = Decimal(paise) / 100
    assert to_paise(str(rupees)) == paise


@given(st.integers(-BIG, BIG))
def test_paise_round_trip_large(paise: int) -> None:
    sign = "-" if paise < 0 else ""
    whole, frac = divmod(abs(paise), 100)
    assert to_paise(f"{sign}{whole}.{frac:02d}") == paise


@given(st.integers(-BIG, BIG))
def test_milli_round_trip_large(milli: int) -> None:
    sign = "-" if milli < 0 else ""
    whole, frac = divmod(abs(milli), 1000)
    assert to_milli(f"{sign}{whole}.{frac:03d}") == milli


@given(st.integers(-(10**30), 10**30), st.integers(-(10**30), 10**30))
def test_line_amount_large_ints_match_reference(price: int, qty: int) -> None:
    assert line_amount(price, qty) == _ref_half_even(price * qty, 1000)


@pytest.mark.parametrize("bad", [1.5, 0.0, True, False, float("nan"), float("inf")])
def test_float_and_bool_rejected(bad: object) -> None:
    with pytest.raises(MoneyError):
        to_paise(bad)  # type: ignore[arg-type]
    with pytest.raises(QtyError):
        to_milli(bad)  # type: ignore[arg-type]


def test_float_message() -> None:
    with pytest.raises(MoneyError, match="pass str, int or Decimal, not float"):
        to_paise(1.5)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "bad",
    [
        "1e2",
        "1E2",
        "inf",
        "-inf",
        "Infinity",
        "nan",
        "NaN",
        "sNaN",
        "",
        " 1",
        "1 ",
        "+1",
        ".5",
        "1.",
        "1_0",
        "--1",
        "1\n",
        "١٢",
    ],
)
def test_non_plain_strings_rejected(bad: str) -> None:
    with pytest.raises(MoneyError):
        to_paise(bad)
    with pytest.raises(QtyError):
        to_milli(bad)


@pytest.mark.parametrize("bad", [Decimal("Infinity"), Decimal("-Infinity"), Decimal("NaN"), Decimal("sNaN")])
def test_non_finite_decimals_rejected(bad: Decimal) -> None:
    with pytest.raises(MoneyError):
        to_paise(bad)
    with pytest.raises(QtyError):
        to_milli(bad)


def test_other_types_rejected() -> None:
    with pytest.raises(MoneyError):
        to_paise(None)  # type: ignore[arg-type]


def test_parsing_ignores_ambient_decimal_context() -> None:
    with localcontext() as ctx:
        ctx.prec = 3
        ctx.traps[Inexact] = True
        ctx.traps[Rounded] = True
        assert to_paise("123456789012345678901234567890.12") == 12345678901234567890123456789012
        assert to_paise(Decimal("1.50")) == 150
        with pytest.raises(MoneyError):
            to_paise("1.005")
        assert to_milli("123456789012345678901234567890.123") == 123456789012345678901234567890123


def test_decimal_objects_with_exponent() -> None:
    assert to_paise(Decimal("1E+2")) == 10000
    assert to_paise(Decimal("1E-2")) == 1
    with pytest.raises(MoneyError):
        to_paise(Decimal("1E-3"))
    with pytest.raises(MoneyError):
        to_paise(Decimal("1E+99999999"))
