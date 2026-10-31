# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Label(Enum):
    measured = 'measured'
    direct = 'direct'
    estimated = 'estimated'


class Entry(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    campaign_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    lever: constr(min_length=1, max_length=200)
    treated_n: conint(ge=0)
    holdout_n: conint(ge=0)
    measured: dict[str, Any]
    direct_paise: conint(ge=0)
    reward_cost_paise: conint(ge=0)
    label: Label


class Impact(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    measured_paise: int
    direct_paise: conint(ge=0)
    estimated_paise: conint(ge=0)


class GrowthLedgerView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    entries: list[Entry]
    impact: Impact
    invalidate_on: list[constr(min_length=1, max_length=200)]
