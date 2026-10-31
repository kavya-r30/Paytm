# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Supplier(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    name: constr(min_length=1, max_length=200)
    lang: constr(min_length=1, max_length=200)
    lead_days: conint(ge=0)
    open_pos: conint(ge=0)
    payable_paise: conint(ge=0)


class SuppliersView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    suppliers: list[Supplier]
    invalidate_on: list[constr(min_length=1, max_length=200)]
