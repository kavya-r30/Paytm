# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Identity(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: constr(min_length=1, max_length=200)
    value: constr(min_length=1, max_length=200)


class Consent(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    purpose: constr(min_length=1, max_length=200)
    granted: bool
    occurred_at: AwareDatetime


class Bill(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    total_paise: conint(ge=0)
    closed_at: AwareDatetime | None


class PatronExport(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    patron: dict[str, Any]
    identities: list[Identity]
    consents: list[Consent]
    khata: dict[str, Any] | None
    bills: list[Bill]
    invalidate_on: list[constr(min_length=1, max_length=200)]
