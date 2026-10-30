# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Price(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(min_length=1)
    price_paise: conint(ge=0)


class CatalogBulkPrice(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    prices: list[Price] = Field(..., max_length=500, min_length=1)
