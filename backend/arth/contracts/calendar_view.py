# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class UpcomingItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1, max_length=200)
    kind: constr(min_length=1, max_length=200)
    name: constr(min_length=1, max_length=200)
    start: date
    end: date
    days_until: int
    confidence: constr(min_length=1, max_length=200)
    source: constr(min_length=1, max_length=200)


class LocalEvent(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    name: constr(min_length=1, max_length=200)
    kind: constr(min_length=1, max_length=200)
    start: date
    end: date


class CalendarView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    city: constr(min_length=1, max_length=200)
    upcoming: list[UpcomingItem]
    local_events: list[LocalEvent]
    tentative_within_60_days: conint(ge=0)
    invalidate_on: list[constr(min_length=1, max_length=200)]
