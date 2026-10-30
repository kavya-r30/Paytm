# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, confloat, constr


class Customer(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    display_name: str
    confidence: confloat(ge=0.0, le=1.0)


class RecentItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    display_name: str
    phone_masked: str | None
    khata_balance_paise: int | None
    reward_stamps: int


class CustomerSearchView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    customers: list[Customer]
    needs_clarification: bool
    invalidate_on: list[str]
    recent: list[RecentItem]
