# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from . import catalog_add_item


class CatalogImportItems(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    confirmed: Literal[True]
    items: list[catalog_add_item.CatalogAddItem] = Field(
        ..., max_length=500, min_length=1
    )
