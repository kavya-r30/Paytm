# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr


class Payload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    campaign_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    template: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )


class Kind(StrEnum):
    owner = 'owner'
    staff = 'staff'
    customer = 'customer'
    supplier = 'supplier'
    agent = 'agent'
    system = 'system'
    simulator = 'simulator'


class Actor(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: Kind
    id: constr(min_length=1) | None = None


class GrowthOutreachRequested(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    event_id: constr(pattern=r'^evt_[0-9A-HJKMNP-TV-Z]{26}$')
    type: Literal['growth.outreach_requested']
    merchant_id: constr(min_length=1)
    occurred_at: AwareDatetime
    actor: Actor
    causation_id: (
        constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    ) = Field(
        ...,
        description='Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).',
    )
    payload: Payload
