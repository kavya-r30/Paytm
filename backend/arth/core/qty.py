"""Quantities are integer milli-units (0.5 kg = 500)."""

from __future__ import annotations

from decimal import Decimal

from arth.core.money import div_round_half_even, scale_exact

MILLI = 1000


class QtyError(ValueError):
    """A quantity cannot be represented exactly in milli-units."""


def to_milli(qty: str | int | Decimal) -> int:
    """Convert a quantity in units to integer milli-units, exactly.

    Accepts a plain decimal string like "0.5" or "-1.250" (no exponent, `+` sign, spaces,
    "inf"/"nan"), an int, or a finite Decimal. Raises QtyError for float/bool, non-finite or
    malformed input, and values with more than 3 decimal places.
    """
    return scale_exact(qty, 3, QtyError)


def line_amount(unit_price_paise: int, qty_milli: int) -> int:
    """Price of `qty_milli` units at `unit_price_paise` per unit, rounded half-even to the paisa."""
    return div_round_half_even(unit_price_paise * qty_milli, MILLI)
