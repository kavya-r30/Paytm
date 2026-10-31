# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date
from enum import Enum, StrEnum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Status(Enum):
    open = 'open'
    disputed = 'disputed'
    acknowledged = 'acknowledged'
    resolved = 'resolved'


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    description_key: str | None
    qty_milli: int
    unit_price_paise: conint(ge=0)
    amount_paise: int


class Entry(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    account_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    amount_paise: int
    source: str
    ref_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    member_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    reversal_of: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    occurred_at: AwareDatetime
    status: Status
    allocated_paise: conint(ge=0)
    lines: list[Line]


class Payment(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    payment_ref: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    amount_paise: conint(ge=0)
    mode: str
    occurred_at: AwareDatetime


class Status18(StrEnum):
    active = 'active'
    kept = 'kept'
    broken = 'broken'


class Promise(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    amount_paise: conint(ge=0)
    due_on: date
    occurred_at: AwareDatetime
    status: Status18


class KhataAccountView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    account_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    as_of: AwareDatetime
    entries: list[Entry]
    payments: list[Payment]
    entries_paise: int
    allocated_paise: conint(ge=0)
    balance_paise: conint(ge=0)
    advance_paise: conint(ge=0)
    invalidate_on: list[str]
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    display_name: str
    limit_paise: conint(ge=0)
    promises: list[Promise]
    pay_link_ref: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
