"""The Sim Clock: the only source of "now" in Arth (spec v5.1 D6).

Stored times are UTC; the shop sees IST. A frozen clock never moves; a running clock advances at
`rate` x real time. `set` only moves forward; `reset` (used by snapshot restore) may go back.
"""

from __future__ import annotations

import math
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
__all__ = ["IST", "UTC", "ClockError", "SimClock", "iso_utc", "parse_iso", "next_daily"]

_HH_MM = re.compile(r"([01][0-9]|2[0-3]):([0-5][0-9])")


class ClockError(ValueError):
    """Invalid clock input: naive datetime, backwards `set`, bad `rate`, or malformed "HH:MM"."""


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ClockError("datetimes must be timezone-aware")


def _require_rate(rate: float) -> None:
    valid = isinstance(rate, int | float) and not isinstance(rate, bool) and math.isfinite(rate) and rate > 0
    if not valid:
        raise ClockError("rate must be a positive finite number")


def iso_utc(value: datetime) -> str:
    """Fixed-width UTC ISO string; sorts lexically in time order (used in SQLite columns)."""
    _require_aware(value)
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    _require_aware(parsed)
    return parsed.astimezone(UTC)


def next_daily(after: datetime, at_ist: str) -> datetime:
    """The first moment strictly after `after` whose IST wall time is `at_ist` ("HH:MM")."""
    _require_aware(after)
    match = _HH_MM.fullmatch(at_ist)
    if match is None:
        raise ClockError(f"bad time {at_ist!r}; expected HH:MM")
    hour, minute = int(match.group(1)), int(match.group(2))
    local = after.astimezone(IST)
    candidate = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= local:
        candidate += timedelta(days=1)
    return candidate.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class _State:
    anchor_sim: datetime
    anchor_real: float
    running: bool
    rate: float


class SimClock:
    """The simulated clock.

    Safe to read (`now`, `now_ist`, `running`, `rate`) from any thread: all state lives in one
    immutable snapshot that is swapped in a single assignment. Mutate (`set`, `reset`, `freeze`,
    `run`) only from the event-loop thread.
    """

    def __init__(
        self,
        start: datetime,
        *,
        running: bool = False,
        rate: float = 1.0,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        _require_aware(start)
        _require_rate(rate)
        self._monotonic = monotonic
        self._state = _State(start.astimezone(UTC), monotonic(), running, rate)

    @property
    def running(self) -> bool:
        return self._state.running

    @property
    def rate(self) -> float:
        return self._state.rate

    def now(self) -> datetime:
        return self._at(self._state, self._monotonic())

    def now_ist(self) -> datetime:
        return self.now().astimezone(IST)

    def set(self, value: datetime) -> None:
        _require_aware(value)
        current = self.now()
        if value < current:
            raise ClockError(
                "sim time cannot go backwards; restore a snapshot instead "
                f"(requested {value.astimezone(UTC).isoformat()}, "
                f"current {current.isoformat()})"
            )
        self._rebase(value, self._state.running, self._state.rate)

    def reset(self, value: datetime) -> None:
        """Move to any time. Only snapshot restore may call this."""
        _require_aware(value)
        self._rebase(value, self._state.running, self._state.rate)

    def freeze(self) -> None:
        self._rebase(self.now(), False, self._state.rate)

    def run(self, rate: float = 1.0) -> None:
        _require_rate(rate)
        self._rebase(self.now(), True, rate)

    @staticmethod
    def _at(state: _State, real: float) -> datetime:
        if not state.running:
            return state.anchor_sim
        return state.anchor_sim + timedelta(seconds=(real - state.anchor_real) * state.rate)

    def _rebase(self, value: datetime, running: bool, rate: float) -> None:
        self._state = _State(value.astimezone(UTC), self._monotonic(), running, rate)
