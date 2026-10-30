# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr


class StockLogUnmetDemand(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    text: constr(min_length=1, max_length=500)
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        None
    )
