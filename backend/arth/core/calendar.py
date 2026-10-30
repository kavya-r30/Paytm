"""India-wide calendar (spec Part D3): events scoped national, by state (ISO 3166-2:IN) or by city.

Each event carries a confidence label and a source; states may override the date. `CalendarIndex` answers
"what applies to this shop's city between these dates" (CAL-1).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from arth.core.yamlconf import ConfigError, Strict, validate

EventType = Literal["festival", "public_holiday", "observance", "season", "local", "sale_event"]
Confidence = Literal["published", "panchang", "regional_variant", "moon_sighting", "tentative"]
Closure = Literal["none", "partial", "full"]
Name = Annotated[str, Field(min_length=1)]
CALENDAR_FILE = re.compile(r"^(regions|events-.+|seasons-.+)\.yaml$")


class Scope(Strict):
    national: bool = False
    states: list[str] = []
    cities: list[str] = []

    @model_validator(mode="after")
    def _not_empty(self) -> Scope:
        if not (self.national or self.states or self.cities):
            raise ValueError("scope needs national: true or a list of states/cities")
        return self

    def applies(self, state: str, city: str) -> bool:
        return self.national or state in self.states or city in self.cities


class CalEvent(Strict):
    id: str
    kind: str
    type: EventType
    names: dict[str, Name]
    start: date
    end: date | None = None
    scope: Scope
    date_overrides: dict[str, date] = {}
    confidence: Confidence
    lead_days: int = Field(default=0, ge=0)
    tail_days: int = Field(default=0, ge=0)
    closure: Closure = "none"
    priors: dict[str, dict[str, float]] = {}
    source: str = Field(min_length=1)
    note: str | None = None

    @model_validator(mode="after")
    def _end_after_start(self) -> CalEvent:
        if self.end is not None and self.end < self.start:
            raise ValueError(f"{self.id}: end is before start")
        return self


class RecurringEvent(Strict):
    id: str
    kind: str
    names: dict[str, Name]
    rule: Literal["monthly_days"]
    days: list[int]
    scope: Scope
    confidence: Confidence = "published"
    priors: dict[str, dict[str, float]] = {}
    source: str = Field(min_length=1)

    @field_validator("days")
    @classmethod
    def _valid_days(cls, days: list[int]) -> list[int]:
        # Days absent from a short month (e.g. 31 in April) are skipped at query time, not rejected here.
        if not days:
            raise ValueError("days must not be empty")
        if any(not 1 <= d <= 31 for d in days):
            raise ValueError(f"days must each be 1..31, got {days}")
        if len(set(days)) != len(days):
            raise ValueError(f"days must be unique, got {days}")
        return days


class CalendarFile(Strict):
    events: list[CalEvent] = []
    recurring: list[RecurringEvent] = []


class StateInfo(Strict):
    code: str = Field(pattern=r"^IN-[A-Z]{2}$")
    name: str
    ui_locale: str
    cities: list[str]


class Regions(Strict):
    states: list[StateInfo]

    @model_validator(mode="after")
    def _unique_places(self) -> Regions:
        seen: dict[str, str] = {}
        for state in self.states:
            for city in state.cities:
                if city in seen:
                    raise ValueError(f"city {city!r} is listed under both {seen[city]} and {state.code}")
                seen[city] = state.code
        codes = [s.code for s in self.states]
        dupes = sorted({c for c in codes if codes.count(c) > 1})
        if dupes:
            raise ValueError(f"duplicate state codes {dupes}")
        return self


@dataclass(frozen=True)
class Calendar:
    events: list[CalEvent]
    recurring: list[RecurringEvent]
    regions: Regions
    origins: dict[str, str] = field(default_factory=dict)  # event id -> file name, for error messages


@dataclass(frozen=True)
class Occurrence:
    id: str
    kind: str
    start: date
    end: date
    confidence: str
    source: str
    type: str = "observance"
    names: dict[str, str] = field(default_factory=dict)
    closure: str = "none"
    note: str | None = None
    lead_days: int = 0
    tail_days: int = 0
    priors: dict[str, dict[str, float]] = field(default_factory=dict)


def _months(start: date, end: date) -> Iterator[tuple[int, int]]:
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


class CalendarIndex:
    """Resolves which events apply to a shop's city, with state date overrides (CAL-1)."""

    def __init__(self, calendar: Calendar) -> None:
        self._calendar = calendar
        self._state_of_city = {city: s.code for s in calendar.regions.states for city in s.cities}
        states = {s.code for s in calendar.regions.states}
        items: list[CalEvent | RecurringEvent] = [*calendar.events, *calendar.recurring]
        for item in items:
            unknown = (set(item.scope.states) - states) | (
                set(item.scope.cities) - self._state_of_city.keys()
            )
            if isinstance(item, CalEvent):
                unknown |= set(item.date_overrides) - states
            if unknown:
                origin = calendar.origins.get(item.id, "calendar")
                raise ConfigError(f"{origin}: event {item.id!r} uses unknown places: {sorted(unknown)}")

    def state_of(self, city: str) -> str:
        try:
            return self._state_of_city[city]
        except KeyError:
            raise ConfigError(f"unknown city {city!r}; add it to config/calendar/regions.yaml") from None

    def between(self, city: str, start: date, end: date) -> list[Occurrence]:
        """Occurrences whose own dates (start..end, after state overrides) overlap [start, end].

        `lead_days` / `tail_days` are NOT applied: the query is by event dates. They are carried on each
        Occurrence so consumers (nudges, stock prep) widen their own windows.
        """
        state = self.state_of(city)
        found: list[Occurrence] = []
        for event in self._calendar.events:
            if not event.scope.applies(state, city):
                continue
            begin = event.date_overrides.get(state, event.start)
            finish = begin + ((event.end - event.start) if event.end else timedelta(0))
            if finish >= start and begin <= end:
                found.append(
                    Occurrence(
                        id=event.id,
                        kind=event.kind,
                        start=begin,
                        end=finish,
                        confidence=event.confidence,
                        source=event.source,
                        type=event.type,
                        names=dict(event.names),
                        closure=event.closure,
                        note=event.note,
                        lead_days=event.lead_days,
                        tail_days=event.tail_days,
                        priors={k: dict(v) for k, v in event.priors.items()},
                    )
                )
        for rec in self._calendar.recurring:
            if not rec.scope.applies(state, city):
                continue
            for year, month in _months(start, end):
                for day in rec.days:
                    try:
                        on = date(year, month, day)
                    except ValueError:  # e.g. day 31 in a 30-day month
                        continue
                    if start <= on <= end:
                        found.append(
                            Occurrence(
                                id=f"{rec.id}_{on:%Y%m%d}",
                                kind=rec.kind,
                                start=on,
                                end=on,
                                confidence=rec.confidence,
                                source=rec.source,
                                type="observance",
                                names=dict(rec.names),
                                priors={k: dict(v) for k, v in rec.priors.items()},
                            )
                        )
        return sorted(found, key=lambda o: (o.start, o.id))

    def upcoming(self, city: str, today: date, *, within_days: int) -> list[Occurrence]:
        return self.between(city, today, today + timedelta(days=within_days))

    def days_until(self, kind: str, today: date, *, city: str) -> int:
        for occurrence in self.between(city, today, today + timedelta(days=400)):
            if occurrence.kind == kind and occurrence.start >= today:
                return (occurrence.start - today).days
        raise KeyError(f"no upcoming {kind!r} for {city} after {today}")


def load_calendar(directory: Path) -> Calendar:
    for path in sorted(directory.glob("*.yaml")):
        if not CALENDAR_FILE.match(path.name):
            raise ConfigError(
                f"{path.name}: unexpected file in calendar dir; "
                "expected regions.yaml, events-*.yaml or seasons-*.yaml"
            )
    regions = validate(Regions, directory / "regions.yaml")
    events: list[CalEvent] = []
    recurring: list[RecurringEvent] = []
    origins: dict[str, str] = {}
    for path in sorted([*directory.glob("events-*.yaml"), *directory.glob("seasons-*.yaml")]):
        parsed = validate(CalendarFile, path)
        items: list[CalEvent | RecurringEvent] = [*parsed.events, *parsed.recurring]
        for item in items:
            if item.id in origins:
                raise ConfigError(
                    f"{path.name}: duplicate id {item.id!r} (first defined in {origins[item.id]})"
                )
            origins[item.id] = path.name
        events.extend(parsed.events)
        recurring.extend(parsed.recurring)
    return Calendar(events=events, recurring=recurring, regions=regions, origins=origins)
