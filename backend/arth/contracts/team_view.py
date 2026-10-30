# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr

from . import common


class Status(Enum):
    idle = 'idle'
    working = 'working'
    waiting = 'waiting'
    paused = 'paused'


class Helper(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1, max_length=200)
    name_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    agents: list[constr(min_length=1, max_length=200)]
    status: Status
    tier: common.Tier
    pending_gates: conint(ge=0)
    open_work: conint(ge=0)
    line: constr(min_length=1, max_length=200) | None


class Run(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    playbook: constr(min_length=1, max_length=200)
    agent: constr(min_length=1, max_length=200)
    subject: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    step: constr(min_length=1, max_length=200)
    created_at: AwareDatetime
    updated_at: AwareDatetime


class WorkItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    kind: constr(min_length=1, max_length=200)
    agent: constr(min_length=1, max_length=200)
    title_key: constr(min_length=1, max_length=200)
    params: dict[str, Any]
    urgency: conint(ge=0)
    status: constr(min_length=1, max_length=200)
    created_at: AwareDatetime


class Summary(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    done_since_night: conint(ge=0)
    waiting_for_you: conint(ge=0)


class TeamView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    helpers: list[Helper]
    runs: list[Run]
    work: list[WorkItem]
    kill_switch: bool
    summary: Summary
    invalidate_on: list[constr(min_length=1, max_length=200)]
