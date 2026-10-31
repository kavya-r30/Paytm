# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Status(Enum):
    new = 'new'
    preparing = 'preparing'
    ready = 'ready'
    served = 'served'


class Item(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    qty_milli: conint(ge=1)
    modifiers: list[constr(min_length=1, max_length=200)]


class Ticket(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    bill_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    token: conint(ge=1)
    status: Status
    age_seconds: conint(ge=0)
    items: list[Item]


class KotView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    tickets: list[Ticket]
    invalidate_on: list[constr(min_length=1, max_length=200)]
