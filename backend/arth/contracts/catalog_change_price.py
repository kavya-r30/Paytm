# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, conint, constr


class CatalogChangePrice(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(min_length=1)
    price_paise: conint(ge=0)
