# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Campaign(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    plan_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    lever: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    stop_reason: constr(min_length=1, max_length=200) | None
    treated: conint(ge=0)
    holdout: conint(ge=0)
    sent: conint(ge=0)
    result: dict[str, Any]


class CampaignView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    campaign: Campaign
    invalidate_on: list[constr(min_length=1, max_length=200)]
