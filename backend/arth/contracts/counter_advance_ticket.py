# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, constr


class To(Enum):
    preparing = 'preparing'
    ready = 'ready'
    served = 'served'


class CounterAdvanceTicket(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    ticket_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    to: To
