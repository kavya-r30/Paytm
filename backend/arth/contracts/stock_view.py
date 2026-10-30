# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Batch(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    batch_no: str
    expires_on: date | None
    mrp_paise: conint(ge=0)
    cost_paise: conint(ge=0)
    recalled: bool
    qty_milli: int


class Item(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    on_hand_qty_milli: int
    sellable_qty_milli: int
    batches: list[Batch]


class StockView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    items: list[Item]
    invalidate_on: list[str]
