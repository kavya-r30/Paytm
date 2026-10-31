# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Type(Enum):
    chart = 'chart'


class ChartCard(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Type
    chart_no: conint(ge=1, le=12)
    kind: constr(min_length=1, max_length=200)
    title_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    x: dict[str, Any]
    series: list[dict[str, Any]]
    data: list[dict[str, Any]]
    data_ref: constr(min_length=1, max_length=200)
    as_of: AwareDatetime
    takeaway: dict[str, Any]
    invalidate_on: list[constr(min_length=1, max_length=200)]
