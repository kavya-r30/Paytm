# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, conint, constr

from . import common


class SupplyAddSupplier(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    phone: constr(min_length=1, max_length=200) | None = None
    lang: common.Locale
    lead_days: conint(ge=0, le=60)
