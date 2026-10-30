# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date as date_aliased

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Appointment(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    service_item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = (
        Field(
            ...,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    staff_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    start_at: AwareDatetime | None
    end_at: AwareDatetime | None
    status: constr(min_length=1, max_length=200)
    source: constr(min_length=1, max_length=200)


class StaffItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    name: constr(min_length=1, max_length=200)
    skills: list[constr(min_length=1, max_length=200)]
    appointments: list[Appointment]


class WalkIn(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    service_item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = (
        Field(
            ...,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    staff_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    start_at: AwareDatetime | None
    end_at: AwareDatetime | None
    status: constr(min_length=1, max_length=200)
    source: constr(min_length=1, max_length=200)


class AppointmentsView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    date: date_aliased
    staff: list[StaffItem]
    walk_ins: list[WalkIn]
    no_shows: conint(ge=0)
    invalidate_on: list[constr(min_length=1, max_length=200)]
