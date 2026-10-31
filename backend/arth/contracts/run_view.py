# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr


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
    context: dict[str, Any]
    wait: dict[str, Any] | None


class Step(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    step: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    detail: dict[str, Any]
    occurred_at: AwareDatetime


class RunView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    run: Run
    steps: list[Step]
    invalidate_on: list[constr(min_length=1, max_length=200)]
