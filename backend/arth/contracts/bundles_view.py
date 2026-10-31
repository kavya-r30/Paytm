# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Bundle(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    items: list[constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$')]
    names: list[constr(min_length=1, max_length=200)]
    price_paise: conint(ge=0)
    margin_bp: int
    support: conint(ge=0)


class Preorder(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    total_paise: conint(ge=0)
    deposit_paise: conint(ge=0)
    status: constr(min_length=1, max_length=200)


class BundlesView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    bundles: list[Bundle]
    preorders: list[Preorder]
    invalidate_on: list[constr(min_length=1, max_length=200)]
