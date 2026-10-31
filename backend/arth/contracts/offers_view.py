# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Terms(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    amount_paise: conint(ge=1)
    min_spend_paise: conint(ge=0)
    expiry_days: conint(ge=0, le=365)


class Liability(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    issued_paise: conint(ge=0)
    redeemed_paise: conint(ge=0)
    expired_paise: conint(ge=0)
    outstanding_paise: int


class Program(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    type: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    funding: constr(min_length=1, max_length=200)
    terms: Terms
    budget_paise: conint(ge=1)
    spent_paise: int
    liability: Liability
    treated: conint(ge=0)
    holdout: conint(ge=0)
    issued: conint(ge=0)
    valid_until: AwareDatetime


class OffersView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    programs: list[Program]
    liability: Liability
    invalidate_on: list[constr(min_length=1, max_length=200)]
