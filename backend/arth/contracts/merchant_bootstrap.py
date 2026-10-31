# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr


class MerchantBootstrap(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1)
    pack: constr(min_length=1)
    owner_id: constr(min_length=1)
    owner_name: constr(min_length=1)
    device_id: constr(min_length=1)
