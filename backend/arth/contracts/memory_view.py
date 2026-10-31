# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr


class Status(Enum):
    active = 'active'
    unverified = 'unverified'
    retracted = 'retracted'
    forgotten = 'forgotten'


class Fact(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    subject: constr(min_length=1, max_length=200)
    predicate: constr(min_length=1, max_length=200)
    value: constr(min_length=1, max_length=200)
    evidence: list[constr(min_length=1, max_length=200)]
    source: constr(min_length=1, max_length=200)
    status: Status
    created_at: AwareDatetime


class MemoryView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    facts: list[Fact]
    invalidate_on: list[constr(min_length=1, max_length=200)]
