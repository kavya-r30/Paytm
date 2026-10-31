# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date as date_aliased
from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr


class Payload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    date: date_aliased


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


class PaymentDailyClosed(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    event_id: constr(pattern=r'^evt_[0-9A-HJKMNP-TV-Z]{26}$')
    type: Literal['payment.daily_closed']
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
