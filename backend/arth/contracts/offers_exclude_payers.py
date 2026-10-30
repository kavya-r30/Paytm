# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, constr


class OffersExcludePayers(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    payer_refs: list[constr(min_length=1, max_length=200)] = Field(
        ..., max_length=50, min_length=1
    )
