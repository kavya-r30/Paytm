# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Type(Enum):
    next_txn_cashback = 'next_txn_cashback'
    instant_cashback = 'instant_cashback'
    first_time_coupon = 'first_time_coupon'
    payment_count = 'payment_count'
    item_coupon = 'item_coupon'


class Rules(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    reward_paise: conint(ge=1)
    min_spend_paise: conint(ge=0) | None = None
    validity_days: conint(ge=0, le=365) | None = None
    count: conint(ge=1, le=100) | None = None
    combine_minutes: conint(ge=1, le=60) | None = None
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        Field(
            None,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )


class Terms(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    amount_paise: conint(ge=1)
    min_spend_paise: conint(ge=0)
    expiry_days: conint(ge=0, le=365)


class Funding(Enum):
    merchant = 'merchant'
    platform = 'platform'


class OffersCreateProgram(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Type
    rules: Rules
    terms: Terms
    budget_paise: conint(ge=1)
    daily_budget_paise: conint(ge=1) | None = None
    funding: Funding
    holdout_bp: conint(ge=0, le=5000)
    include_regulars: bool | None = None
    valid_from: AwareDatetime
    valid_until: AwareDatetime
