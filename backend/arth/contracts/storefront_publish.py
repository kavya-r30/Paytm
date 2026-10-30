# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr


class StorefrontPublish(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    slug: constr(pattern=r'^[a-z0-9][a-z0-9-]{2,40}$')
    published: bool
    show_offers: bool
