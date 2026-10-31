# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Offer(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    lender: constr(min_length=1, max_length=200)
    amount_paise: conint(ge=1)
    tenor_days: conint(ge=1)
    apr_bp: conint(ge=0)
    edi_paise: conint(ge=1)
    processing_fee_paise: conint(ge=0)
    total_repayment_paise: conint(ge=1)
    kfs_url: constr(min_length=1, max_length=200)
    cooling_off_days: conint(ge=0)
    expires_at: AwareDatetime
    affordable: bool


class ConsolePointer(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    route: constr(min_length=1, max_length=200)
    message_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )


class CapitalView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    profile: dict[str, Any]
    need: dict[str, Any] | None
    affordability: dict[str, Any]
    offers: list[Offer]
    recommended_offer_id: (
        constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    )
    console_pointer: ConsolePointer
    invalidate_on: list[constr(min_length=1, max_length=200)]
