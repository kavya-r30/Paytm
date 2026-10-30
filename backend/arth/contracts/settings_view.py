# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, constr


class ScreenLang(Enum):
    hi = 'hi'
    en = 'en'
    hi_Latn = 'hi-Latn'
    mr = 'mr'
    ta = 'ta'
    bn = 'bn'
    gu = 'gu'
    te = 'te'


class SpeechLang(Enum):
    hi_IN = 'hi-IN'
    en_IN = 'en-IN'
    mr_IN = 'mr-IN'
    ta_IN = 'ta-IN'
    bn_IN = 'bn-IN'
    gu_IN = 'gu-IN'
    te_IN = 'te-IN'


class CustomerLang(Enum):
    hi = 'hi'
    en = 'en'
    hi_Latn = 'hi-Latn'
    mr = 'mr'
    ta = 'ta'
    bn = 'bn'
    gu = 'gu'
    te = 'te'


class TaxProfile(Enum):
    unregistered = 'unregistered'
    composition = 'composition'
    regular = 'regular'


class Hours(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    start: constr(pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')
    end: constr(pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')


class QuietHours(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    start: constr(pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')
    end: constr(pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')


class SettingsView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    screen_lang: ScreenLang
    speech_lang: SpeechLang
    customer_lang: CustomerLang
    name: str
    vpa: constr(min_length=1, max_length=200) | None = None
    address: constr(min_length=1, max_length=200) | None = None
    gstin: constr(max_length=15) | None = None
    tax_profile: TaxProfile
    hours: Hours | None = None
    quiet_hours: QuietHours | None = None
    pack: str
    marketing_consent_default: Literal[False]
    receipts_consent_default: Literal[False]
    invalidate_on: list[str] | None = None
