# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    qty_milli: conint(ge=1)
    unit_price_paise: conint(ge=0)
    description_key: (
        constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) | None
    ) = Field(
        None,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )


class Source(Enum):
    counter = 'counter'
    voice = 'voice'
    order = 'order'
    import_ = 'import'


class LedgerAddEntry(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    account_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    amount_paise: conint(ge=1)
    lines: list[Line] = Field(..., min_length=1)
    source: Source
    ref_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = None
    occurred_at: AwareDatetime | None = None
    member_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        None
    )
    limit_override: bool | None = None
    reason_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) | None = (
        Field(
            None,
            description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
        )
    )
