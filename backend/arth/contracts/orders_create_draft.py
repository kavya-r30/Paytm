# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Channel(Enum):
    whatsapp = 'whatsapp'
    storefront = 'storefront'
    device = 'device'
    preorder = 'preorder'


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    text: constr(min_length=1, max_length=200)
    qty_milli: conint(ge=1)
    confidence_bp: conint(ge=0, le=10000)


class OrdersCreateDraft(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    channel: Channel
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        Field(
            None,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    message_ref: constr(min_length=1, max_length=200) | None = None
    lines: list[Line] = Field(..., max_length=50, min_length=1)
