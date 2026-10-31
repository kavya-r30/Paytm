import ast
import math
from datetime import datetime, timedelta

import pytest

from arth.core.clock import IST, UTC, ClockError, SimClock, iso_utc, next_daily, parse_iso
from arth.core.paths import BACKEND_DIR

START = datetime(2026, 10, 29, 7, 45, tzinfo=IST)
NAIVE = datetime(2026, 10, 29, 7, 45)  # noqa: DTZ001


class FakeMonotonic:
    """A hand-driven stand-in for time.monotonic, so clock tests never sleep."""

    def __init__(self) -> None:
        self.value = 1000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


@pytest.fixture
def mono() -> FakeMonotonic:
    return FakeMonotonic()


def test_frozen_clock_does_not_move(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    mono.advance(3600)
    assert clock.now() == START.astimezone(UTC)
    assert clock.running is False


def test_now_is_utc_aware_and_ist_view_matches() -> None:
    clock = SimClock(START)
    assert clock.now().tzinfo is UTC
    assert clock.now_ist().hour == 7 and clock.now_ist().minute == 45


def test_set_forward_and_refuse_backwards() -> None:
    clock = SimClock(START)
    clock.set(START + timedelta(hours=2))
    assert clock.now_ist().hour == 9
    with pytest.raises(ClockError):
        clock.set(START)


def test_set_backwards_message_names_both_times() -> None:
    clock = SimClock(START + timedelta(hours=2))
    with pytest.raises(ClockError) as info:
        clock.set(START)
    message = str(info.value)
    assert START.astimezone(UTC).isoformat() in message
    assert (START + timedelta(hours=2)).astimezone(UTC).isoformat() in message


def test_set_to_exactly_now_is_allowed(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.set(clock.now())
    assert clock.now() == START.astimezone(UTC)
    clock.run(rate=60.0)
    mono.advance(1)
    clock.set(clock.now())
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=60)


def test_reset_may_go_backwards_for_snapshot_restore() -> None:
    clock = SimClock(START + timedelta(days=1))
    clock.reset(START)
    assert clock.now() == START.astimezone(UTC)


def test_reset_while_running_continues_at_same_rate(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=60.0)
    mono.advance(1)
    target = START - timedelta(days=3)
    clock.reset(target)
    assert clock.now() == target.astimezone(UTC)
    mono.advance(2)
    assert clock.now() == target.astimezone(UTC) + timedelta(seconds=120)
    assert clock.running is True
    assert clock.rate == 60.0


def test_running_clock_advances_at_rate(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=3600.0)  # one real second = one sim hour
    mono.advance(0.5)
    assert clock.now() == START.astimezone(UTC) + timedelta(minutes=30)
    clock.freeze()
    frozen = clock.now()
    mono.advance(10)
    assert clock.now() == frozen == START.astimezone(UTC) + timedelta(minutes=30)
    assert clock.running is False


def test_rate_continuity_across_run_freeze_run(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=10.0)
    mono.advance(1)
    clock.freeze()
    mono.advance(5)
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=10)
    clock.run(rate=10.0)
    mono.advance(1)
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=20)


def test_multi_day_running_jump(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=86400.0)  # one real second = one sim day
    mono.advance(8)
    assert clock.now() == START.astimezone(UTC) + timedelta(days=8)


def test_rate_property_defaults_and_follows_run(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    assert clock.rate == 1.0
    clock.run(rate=5.0)
    assert clock.rate == 5.0


@pytest.mark.parametrize("bad", [0, -1, -0.5, math.nan, math.inf, -math.inf])
def test_constructor_rejects_bad_rate(bad: float) -> None:
    with pytest.raises(ClockError, match="rate must be a positive finite number"):
        SimClock(START, rate=bad)


@pytest.mark.parametrize("bad", [0, -1, -0.5, math.nan, math.inf, -math.inf])
def test_run_rejects_bad_rate_and_leaves_state_unchanged(bad: float, mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=10.0)
    mono.advance(1)
    with pytest.raises(ClockError, match="rate must be a positive finite number"):
        clock.run(rate=bad)
    assert clock.running is True
    assert clock.rate == 10.0
    mono.advance(1)
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=20)


def test_rejected_run_leaves_frozen_clock_frozen(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    with pytest.raises(ClockError):
        clock.run(rate=0)
    assert clock.running is False
    mono.advance(100)
    assert clock.now() == START.astimezone(UTC)


def test_rejects_naive_datetimes() -> None:
    with pytest.raises(ClockError):
        SimClock(NAIVE)


def test_set_and_reset_reject_naive_datetimes() -> None:
    clock = SimClock(START)
    with pytest.raises(ClockError):
        clock.set(NAIVE)
    with pytest.raises(ClockError):
        clock.reset(NAIVE)


def test_iso_round_trip_and_fixed_width() -> None:
    value = iso_utc(START)
    assert value == "2026-10-29T02:15:00.000000Z"
    assert parse_iso(value) == START


def test_parse_iso_rejects_naive_strings() -> None:
    with pytest.raises(ClockError):
        parse_iso("2026-10-29T02:15:00")


def test_next_daily_is_strictly_after() -> None:
    at_2200 = next_daily(START, "22:00")
    assert at_2200.astimezone(IST) == datetime(2026, 10, 29, 22, 0, tzinfo=IST)
    assert next_daily(at_2200, "22:00").astimezone(IST) == datetime(2026, 10, 30, 22, 0, tzinfo=IST)


def test_next_daily_from_exact_boundary_goes_to_next_day() -> None:
    boundary = datetime(2026, 10, 29, 8, 0, tzinfo=IST)
    assert next_daily(boundary, "08:00").astimezone(IST) == datetime(2026, 10, 30, 8, 0, tzinfo=IST)


@pytest.mark.parametrize("bad", ["8", "25:00", "08:00:00", "ab", "08:60", "8:00", ""])
def test_next_daily_rejects_bad_time(bad: str) -> None:
    with pytest.raises(ClockError, match="expected HH:MM"):
        next_daily(START, bad)


# --- wall-clock ban (AST based, so comments and docstrings never trigger it) ---

_BANNED_CALLS = (
    ("datetime", "now"),
    ("datetime", "utcnow"),
    ("date", "today"),
    ("time", "time"),
    ("time", "time_ns"),
)


def _attribute_chain(node: ast.expr) -> tuple[str, ...]:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return tuple(reversed(parts))


def wall_clock_violations(source: str) -> list[str]:
    """Describe every wall-clock read in `source` (empty list when clean)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            chain = _attribute_chain(node.func)
            if any(chain[-2:] == banned for banned in _BANNED_CALLS):
                found.append(f"line {node.lineno}: {'.'.join(chain)}()")
        elif isinstance(node, ast.ImportFrom) and node.module == "time":
            found.extend(
                f"line {node.lineno}: from time import {alias.name}"
                for alias in node.names
                if alias.name in {"time", "time_ns"}
            )
    return found


def test_wall_clock_scanner_flags_violations_only() -> None:
    dirty = (
        "import time\n"
        "from datetime import datetime\n"
        "from time import time_ns\n"
        "a = datetime.now()\n"
        "b = time.time()\n"
    )
    assert len(wall_clock_violations(dirty)) == 3
    clean = (
        '"""Mentions datetime.now() and time.time() in a docstring only."""\n'
        "# datetime.utcnow() in a comment\n"
        "import time\n"
        "x = time.monotonic()\n"
        "y = clock.now()\n"
    )
    assert wall_clock_violations(clean) == []


def test_no_wall_clock_outside_clock_module() -> None:
    clock_module = (BACKEND_DIR / "arth" / "core" / "clock.py").resolve()
    offenders = {
        str(path.relative_to(BACKEND_DIR)): hits
        for path in (BACKEND_DIR / "arth").rglob("*.py")
        if path.resolve() != clock_module
        and (hits := wall_clock_violations(path.read_text(encoding="utf-8")))
    }
    assert offenders == {}, f"use SimClock instead of the wall clock in: {offenders}"
