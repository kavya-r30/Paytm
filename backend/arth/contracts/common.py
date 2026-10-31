# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field, RootModel, constr


class Common(RootModel[Any]):
    root: Any = Field(
        ...,
        description='Shared definitions referenced by every other contract (spec Part C1). Reference them as `common.schema.json#/definitions/<Name>`.',
        title='Common',
    )


class Locale(StrEnum):
    hi = 'hi'
    en = 'en'
    hi_Latn = 'hi-Latn'
    mr = 'mr'
    ta = 'ta'
    bn = 'bn'
    gu = 'gu'
    te = 'te'


class SpeechLocale(StrEnum):
    hi_IN = 'hi-IN'
    en_IN = 'en-IN'
    mr_IN = 'mr-IN'
    ta_IN = 'ta-IN'
    bn_IN = 'bn-IN'
    gu_IN = 'gu-IN'
    te_IN = 'te-IN'


class Audience(StrEnum):
    all = 'all'
    owner = 'owner'
    customer = 'customer'


class Tier(StrEnum):
    R0 = 'R0'
    R1 = 'R1'
    R2 = 'R2'
    R3 = 'R3'
    R4 = 'R4'


class Ulid(RootModel[constr(pattern=r'^[0-9A-HJKMNP-TV-Z]{26}$')]):
    root: constr(pattern=r'^[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ..., description='A bare ULID (Crockford base32, 26 characters).'
    )
