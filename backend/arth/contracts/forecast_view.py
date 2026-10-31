# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date as date_aliased
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Metric(Enum):
    sales = 'sales'
    items = 'items'


class Status(Enum):
    ready = 'ready'
    needs_more_data = 'needs_more_data'


class Actual(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    date: date_aliased
    sales_paise: conint(ge=0)


class Day(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    date: date_aliased
    p10_paise: conint(ge=0)
    p50_paise: conint(ge=0)
    p90_paise: conint(ge=0)
    festive: bool


class Accuracy(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    wape_bp: conint(ge=0) | None
    coverage_bp: conint(ge=0) | None
    window_days: conint(ge=1)
    within_band: conint(ge=0)


class Driver(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    contribution_paise: int


class Item(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    name: constr(min_length=1, max_length=200)
    daily_qty_milli: conint(ge=0)
    horizon_qty_milli: conint(ge=0)


class ForecastView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    metric: Metric
    status: Status
    actuals: list[Actual]
    days: list[Day]
    accuracy: Accuracy
    drivers: list[Driver]
    items: list[Item]
    invalidate_on: list[constr(min_length=1, max_length=200)]
