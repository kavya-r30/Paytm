# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Details(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    salt: constr(min_length=1, max_length=200) | None = None
    strength: constr(min_length=1, max_length=200) | None = None
    form: constr(min_length=1, max_length=200) | None = None
    pack_size: constr(min_length=1, max_length=200) | None = None
    schedule: constr(min_length=1, max_length=200) | None = None
    rx_required: bool | None = None
    duration_minutes: conint(ge=1) | None = None
    required_skill: constr(min_length=1, max_length=200) | None = None


class Item(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1)
    sku: str
    names: dict[str, constr(min_length=1)] = Field(..., min_length=1)
    unit: str | None = None
    category: str | None = None
    mrp_paise: int | None = None
    price_paise: int
    cost_paise: int | None = None
    details: Details | None = None
    frequency: int | None = None


class CatalogSearchView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    items: list[Item] = Field(..., max_length=5)
    invalidate_on: list[str]
