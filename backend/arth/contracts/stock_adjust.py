# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, constr


class StockAdjust(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    batch_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        None
    )
    delta_qty_milli: int
    reason: constr(pattern=r'^[a-z_]+(\.[a-z_]+)+$') = Field(
        ...,
        description='A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours).',
    )
