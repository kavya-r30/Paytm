# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, constr

from . import common


class Kind(Enum):
    vpa = 'vpa'
    phone = 'phone'
    spoken_name = 'spoken_name'
    payer_name = 'payer_name'


class Identity(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: Kind
    value: constr(min_length=1, max_length=200)


class PatronsAdd(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    display_name: constr(min_length=1, max_length=200)
    lang: common.Locale
    identities: list[Identity] | None = None
