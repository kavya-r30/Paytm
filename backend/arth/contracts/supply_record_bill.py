# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    qty_milli: conint(ge=1)
    unit_price_paise: conint(ge=0)


class SupplyRecordBill(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    po_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    bill_ref: constr(min_length=1, max_length=200)
    lines: list[Line] = Field(..., max_length=100, min_length=1)
    due_on: date
