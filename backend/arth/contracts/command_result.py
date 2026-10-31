# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr

from . import common
from . import envelope as envelope_1


class Scope(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: str
    payload: dict[str, Any]
    conditions: dict[str, Any]


class Status(Enum):
    executed = 'executed'
    needs_approval = 'needs_approval'
    queued = 'queued'
    snoozed = 'snoozed'


class CommandResult(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    scope: Scope | None = None
    expires_at: AwareDatetime | None = None
    command_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    status: Status
    tier: common.Tier | None = None
    data: dict[str, Any] | None = None
    envelope: envelope_1.Envelope | None = None
    gate_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        Field(
            None,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    thread_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        Field(
            None,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    due_at: AwareDatetime | None = None
