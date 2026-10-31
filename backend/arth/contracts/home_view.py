# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr

from . import common


class PartOfDay(Enum):
    morning = 'morning'
    midday = 'midday'
    evening = 'evening'
    night = 'night'


class Greeting(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    owner_name: constr(min_length=1, max_length=200)
    shop_name: constr(min_length=1, max_length=200)
    now: AwareDatetime
    part_of_day: PartOfDay


class Today(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    sales_paise: conint(ge=0)
    bills: conint(ge=0)
    customers: conint(ge=0)
    new_customers: conint(ge=0)
    by_mode: dict[str, int]


class Khata(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    outstanding_paise: int
    change_today_paise: int


class Gate(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    gate_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    thread_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    tier: common.Tier
    type: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    expires_at: AwareDatetime
    title_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    summary_params: dict[str, str | int | None]


class Status(Enum):
    cold_start = 'cold_start'
    learning = 'learning'
    ready = 'ready'


class DataSufficiency(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    status: Status
    days_of_history: conint(ge=0)
    reason_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )


class HomeView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    greeting: Greeting
    today: Today
    khata: Khata
    gates: list[Gate]
    brief: dict[str, Any] | None
    data_sufficiency: DataSufficiency
    invalidate_on: list[constr(min_length=1, max_length=200)]
