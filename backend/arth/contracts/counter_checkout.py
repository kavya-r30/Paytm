# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Mode(Enum):
    cash = 'cash'
    card = 'card'


class Payment(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    mode: Mode
    amount_paise: conint(ge=1)
    tendered_paise: conint(ge=1) | None = None


class CounterCheckout(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    bill_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    payments: list[Payment] = Field(..., max_length=4, min_length=1)
    coupon_code: constr(min_length=1, max_length=200) | None = None
