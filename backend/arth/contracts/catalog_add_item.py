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


class ModifierGroup(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    required: bool
    options: list[Option] = Field(..., min_length=1)


class RecipeItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    item_id: constr(min_length=1)
    qty_milli: conint(ge=1)


class CatalogAddItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    sku: constr(min_length=1, max_length=200)
    names: dict[str, constr(min_length=1)] = Field(..., min_length=1)
    unit: constr(min_length=1, max_length=200)
    mrp_paise: conint(ge=0)
    price_paise: conint(ge=0)
    cost_paise: conint(ge=0)
    category: constr(min_length=1, max_length=200)
    aliases: list[constr(min_length=1, max_length=200)] | None = None
    barcodes: list[constr(pattern=r'^[0-9]{8,14}$')] | None = None
    hsn: constr(pattern=r'^[0-9]{4,8}$') | None = None
    gst_rate_bp: conint(ge=0, le=10000) | None = None
    details: Details | None = None
    modifier_groups: list[ModifierGroup] | None = None
    recipe: list[RecipeItem] | None = None
