# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Current(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    customers: conint(ge=0)
    visits: conint(ge=0)
    sales_paise: conint(ge=0)


class Previous(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    customers: conint(ge=0)
    visits: conint(ge=0)
    sales_paise: conint(ge=0)


class Parts(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    customers_paise: int
    frequency_paise: int
    basket_paise: int


class Diagnostics(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    current: Current
    previous: Previous
    change_paise: int
    parts: Parts


class Label(Enum):
    estimate = 'estimate'


class Lever(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    enabled: bool
    eligible: conint(ge=0)
    estimate_paise: conint(ge=0)
    label: Label
    gate: constr(min_length=1, max_length=200)


class Plan(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    goal_key: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    budget_paise: conint(ge=0)
    levers: list[constr(min_length=1, max_length=200)]


class AdvisorItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    account_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    current_limit_paise: conint(ge=0)
    suggested_limit_paise: conint(ge=0)
    reason_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )


class GrowView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    diagnostics: Diagnostics
    peers: dict[str, Any]
    levers: list[Lever]
    plans: list[Plan]
    advisor: list[AdvisorItem]
    invalidate_on: list[constr(min_length=1, max_length=200)]
