# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date as date_aliased
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Today(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    sales_paise: conint(ge=0)
    by_mode: dict[str, int]
    expenses_paise: conint(ge=0)
    refunds_paise: conint(ge=0)
    khata_given_paise: conint(ge=0)


class Suggestion(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    bill_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    total_paise: conint(ge=0)
    score_bp: conint(ge=0)


class UnmatchedItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    payment_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    amount_paise: conint(ge=1)
    received_at: AwareDatetime
    khata_patron_id: (
        constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    )
    suggestions: list[Suggestion]


class Exception(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    kind: constr(min_length=1, max_length=200)
    payment_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    bill_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    status: constr(min_length=1, max_length=200)
    opened_at: AwareDatetime


class Deduction(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: constr(min_length=1, max_length=200)
    amount_paise: conint(ge=0)


class Settlement(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    date: date_aliased
    gross_paise: conint(ge=0)
    net_paise: int
    deductions: list[Deduction]
    explained: bool


class Shift(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    staff_id: constr(min_length=1, max_length=200)
    opened_at: AwareDatetime
    closed_at: AwareDatetime | None
    float_paise: conint(ge=0)
    expected_paise: int
    counted_paise: int | None
    variance_paise: int | None


class Expense(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    category: constr(min_length=1, max_length=200)
    amount_paise: conint(ge=1)
    paid_from: constr(min_length=1, max_length=200)
    occurred_at: AwareDatetime


class HisaabView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    date: date_aliased
    close: dict[str, Any] | None
    today: Today
    unmatched: list[UnmatchedItem]
    exceptions: list[Exception]
    settlements: list[Settlement]
    shifts: list[Shift]
    expenses: list[Expense]
    invalidate_on: list[constr(min_length=1, max_length=200)]
