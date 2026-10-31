# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, constr


class StaffSetSkills(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    staff_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    skills: list[constr(min_length=1, max_length=200)] = Field(
        ..., max_length=20, min_length=0
    )
