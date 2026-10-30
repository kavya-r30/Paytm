# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


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
    lines: conint(ge=0)


class OrdersView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    orders: list[Order]
    by_status: dict[str, int]
    invalidate_on: list[constr(min_length=1, max_length=200)]
