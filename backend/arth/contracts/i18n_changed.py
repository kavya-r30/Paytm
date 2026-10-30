# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum, StrEnum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr


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


class Payload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    screen_lang: ScreenLang
    speech_lang: SpeechLang
    customer_lang: CustomerLang


class Kind(StrEnum):
    owner = 'owner'
    staff = 'staff'
    customer = 'customer'
    supplier = 'supplier'
    agent = 'agent'
    system = 'system'
    simulator = 'simulator'


class Actor(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: Kind
    id: constr(min_length=1) | None = None


class LanguageChanged(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    event_id: constr(pattern=r'^evt_[0-9A-HJKMNP-TV-Z]{26}$')
    type: Literal['i18n.changed']
    merchant_id: constr(min_length=1)
    occurred_at: AwareDatetime
    actor: Actor
    causation_id: (
        constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    ) = Field(
        ...,
        description='Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).',
    )
    payload: Payload
