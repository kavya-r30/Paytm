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


class Option(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    delta_paise: int
    id: constr(min_length=1)


class ModifierGroup(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    required: bool
    options: list[Option] = Field(..., min_length=1)
    id: constr(min_length=1)


class RecipeItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(min_length=1)
    qty_milli: conint(ge=1)


class CatalogItemView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    invalidate_on: list[str] | None = None
    id: constr(min_length=1)
    sku: str
    names: dict[str, constr(min_length=1)] = Field(..., min_length=1)
    unit: str
    category: str | None = None
    mrp_paise: int | None = None
    price_paise: int
    cost_paise: int | None = None
    details: Details | None = None
    frequency: int | None = None
    aliases: list[str] | None = None
    barcodes: list[str] | None = None
    hsn: str | None = None
    gst_rate_bp: int | None = None
    modifier_groups: list[ModifierGroup]
    recipe: list[RecipeItem]
