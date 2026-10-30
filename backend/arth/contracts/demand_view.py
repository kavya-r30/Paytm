# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class UnmetItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    text: constr(min_length=1, max_length=200)
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    occurred_at: AwareDatetime


class Cluster(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    label: constr(min_length=1, max_length=200)
    count: conint(ge=1)


class Status(Enum):
    needs_more_data = 'needs_more_data'
    ready = 'ready'


class DemandView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    unmet: list[UnmetItem]
    clusters: list[Cluster]
    status: Status
    invalidate_on: list[constr(min_length=1, max_length=200)]
