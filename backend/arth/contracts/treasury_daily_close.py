# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date as date_aliased

from pydantic import BaseModel, ConfigDict


class TreasuryDailyClose(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    date: date_aliased
