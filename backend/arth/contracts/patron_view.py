# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Consent(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    marketing: bool
    reminders: bool
    receipts: bool


class HouseholdMember(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    display_name: str


class Rewards(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    stamps: int
    available_rewards: conint(ge=0)
    available_value_paise: conint(ge=0)


class PatronView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    display_name: str
    lang: str
    consent: Consent
    household_members: list[HouseholdMember]
    rewards: Rewards
    invalidate_on: list[str]
