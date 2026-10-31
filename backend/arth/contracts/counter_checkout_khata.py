# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Mode(Enum):
    cash = 'cash'
    card = 'card'


class Payment(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    mode: Mode
    amount_paise: conint(ge=1)
    tendered_paise: conint(ge=1) | None = None


class CounterCheckoutKhata(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    bill_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    account_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    khata_paise: conint(ge=1)
    payments: list[Payment] = Field(..., max_length=3, min_length=0)
    member_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        Field(
            None,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    limit_override: bool | None = None
    reason_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) | None = (
        Field(
            None,
            description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
        )
    )
