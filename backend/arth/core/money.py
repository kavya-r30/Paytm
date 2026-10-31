"""Money is integer paise everywhere. Formatting lives in arth.core.i18n."""

from __future__ import annotations

import re
from decimal import Decimal

_PLAIN_DECIMAL = re.compile(r"-?[0-9]+(\.[0-9]+)?")
_MAX_EXPONENT = 1000  # refuse absurd Decimal exponents instead of building gigantic ints


class MoneyError(ValueError):
    """A money value cannot be represented exactly in paise."""


def scale_exact(value: object, places: int, error: type[ValueError]) -> int:
    """Return `value * 10**places` as an int, or raise `error` if it is not exactly an integer.

    Pure integer arithmetic on the Decimal's digit tuple, so the result never depends on the
    ambient decimal context (precision, traps, rounding).
    Accepts: plain decimal strings (`-?[0-9]+(\\.[0-9]+)?`), ints, finite Decimals.
    Rejects: float, bool, other types, exponent/whitespace/`+`/inf/nan strings, non-finite Decimals.
    """
    if isinstance(value, float):
        raise error("pass str, int or Decimal, not float")
    if isinstance(value, bool):
        raise error("pass str, int or Decimal, not bool")
    try:
        if isinstance(value, str):
            if not _PLAIN_DECIMAL.fullmatch(value):
                raise error(f"not a plain decimal number: {value!r}")
            dec = Decimal(value)
        elif isinstance(value, int):
            dec = Decimal(value)
        elif isinstance(value, Decimal):
            dec = value
        else:
            raise error(f"pass str, int or Decimal, not {type(value).__name__}")
        if not dec.is_finite():
            raise error(f"not a finite number: {value!r}")
        sign, digits, exponent = dec.as_tuple()
        assert isinstance(exponent, int)
        if abs(exponent) > _MAX_EXPONENT:
            raise error(f"exponent too large: {value!r}")
        magnitude = int("".join(map(str, digits)) or "0")
        shift = exponent + places
        if shift >= 0:
            result = magnitude * 10**shift
        else:
            result, remainder = divmod(magnitude, 10**-shift)
            if remainder:
                raise error(f"{value!r} has more than {places} decimal places")
        return -result if sign else result
    except ArithmeticError as exc:
        raise error(f"not a number: {value!r}") from exc


def to_paise(rupees: str | int | Decimal) -> int:
    """Convert rupees to integer paise, exactly.

    Accepts a plain decimal string like "62" or "-62.50" (no exponent, `+` sign, spaces,
    underscores, "inf"/"nan"), an int, or a finite Decimal. Raises MoneyError for float/bool
    (pass a str instead), non-finite or malformed input, and values with more than 2 decimal places.
    """
    return scale_exact(rupees, 2, MoneyError)


def div_round_half_even(numerator: int, denominator: int) -> int:
    """Integer division rounded half-to-even (banker's rounding), used for tax and pro-rata lines.

    Pure integer arithmetic, exact for arbitrarily large ints. Raises ZeroDivisionError on 0.
    """
    if denominator == 0:
        raise ZeroDivisionError("denominator is zero")
    negative = (numerator < 0) != (denominator < 0)
    divisor = abs(denominator)
    quotient, remainder = divmod(abs(numerator), divisor)
    twice = 2 * remainder
    if twice > divisor or (twice == divisor and quotient % 2 == 1):
        quotient += 1
    return -quotient if negative else quotient
