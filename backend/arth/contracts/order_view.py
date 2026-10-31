# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    text: constr(min_length=1, max_length=200)
    qty_milli: conint(ge=1)
    unit_price_paise: conint(ge=0)
    amount_paise: conint(ge=0)
    check: bool


class Order(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    status: constr(min_length=1, max_length=200)
    channel: constr(min_length=1, max_length=200)
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    total_paise: conint(ge=0)
    created_at: AwareDatetime
    lines: list[Line]
    patron_name: str | None


class HistoryItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    from_state: constr(min_length=1, max_length=200) | None
    to_state: constr(min_length=1, max_length=200)
    actor_id: constr(min_length=1, max_length=200)
    occurred_at: AwareDatetime


class PickListItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    name: constr(min_length=1, max_length=200)
    qty_milli: conint(ge=1)


class OrderView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    order: Order
    history: list[HistoryItem]
    pick_list: list[PickListItem]
    allowed: list[constr(min_length=1, max_length=200)]
    invalidate_on: list[constr(min_length=1, max_length=200)]
