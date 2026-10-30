# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Hours(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    start: constr(pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')
    end: constr(pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')


class Item(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    names: dict[str, str]
    unit: constr(min_length=1, max_length=200)
    price_paise: conint(ge=0)
    in_stock: bool
    category: constr(min_length=1, max_length=200)


class Terms(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    amount_paise: conint(ge=1)
    min_spend_paise: conint(ge=0)
    expiry_days: conint(ge=0)


class Offer(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    program_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    terms: Terms
    type: constr(min_length=1, max_length=200)


class PublicStorefront(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    slug: constr(pattern=r'^[a-z0-9][a-z0-9-]{2,40}$')
    hours: Hours
    items: list[Item]
    offers: list[Offer]
    invalidate_on: list[constr(min_length=1, max_length=200)]
