# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class AddedVia(Enum):
    scan = 'scan'
    tap = 'tap'
    voice = 'voice'
    search = 'search'
    hint = 'hint'


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    qty_milli: conint(ge=1) | None = None
    amount_paise: conint(ge=1) | None = None
    modifier_ids: (
        list[constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$')] | None
    ) = Field(None, max_length=10, min_length=0)
    added_via: AddedVia
    unit_price_paise: conint(ge=0) | None = None
    reason_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) | None = (
        Field(
            None,
            description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
        )
    )
    rx_seen: bool | None = None


class CounterAddLines(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    bill_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    lines: list[Line] = Field(..., max_length=50, min_length=1)
