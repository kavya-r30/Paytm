# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date as date_aliased
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Kind(Enum):
    fee = 'fee'
    edi = 'edi'
    refund = 'refund'
    other = 'other'


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: Kind
    amount_paise: conint(ge=0)


class TreasuryRecordSettlement(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    external_ref: constr(min_length=1, max_length=200)
    date: date_aliased
    gross_paise: conint(ge=0)
    net_paise: int
    lines: list[Line] = Field(..., max_length=20, min_length=0)
    utrs: list[constr(min_length=1, max_length=200)] = Field(
        ..., max_length=5000, min_length=0
    )
