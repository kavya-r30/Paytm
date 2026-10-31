# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, conint, constr


class StorefrontView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    slug: constr(pattern=r'^[a-z0-9][a-z0-9-]{2,40}$') | None
    published: bool
    show_offers: bool
    items: conint(ge=0)
    url: constr(min_length=1, max_length=200) | None
    invalidate_on: list[constr(min_length=1, max_length=200)]
