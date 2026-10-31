# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, constr


class Kind(Enum):
    fair = 'fair'
    market_day = 'market_day'
    local_festival = 'local_festival'
    closure = 'closure'
    other = 'other'


class CalendarAddLocalEvent(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    kind: Kind
    start: date
    end: date
