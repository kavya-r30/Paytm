# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import StrEnum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr

from . import common


class Sensitivity(StrEnum):
    normal = 'normal'
    discreet = 'discreet'


class Lang(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    screen: common.Locale
    speech: common.SpeechLocale


class Speech(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    text: constr(min_length=1)
    voice: str | None = None
    ssml_ready: bool | None = None


class Caption(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    heard: str | None = None
    said: str | None = None


class Type(StrEnum):
    bill = 'bill'
    hint = 'hint'
    approval = 'approval'
    batch = 'batch'
    verdict = 'verdict'
    chart = 'chart'
    forecast = 'forecast'
    brief = 'brief'
    offer = 'offer'
    plan = 'plan'
    campaign = 'campaign'
    patron = 'patron'
    stock = 'stock'
    po = 'po'
    quote_compare = 'quote_compare'
    claim = 'claim'
    memory = 'memory'
    draft = 'draft'
    capital = 'capital'
    nudge = 'nudge'
    pipeline = 'pipeline'
    receipt = 'receipt'
    health = 'health'


class Card(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    type: Type
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = Field(
        None,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    audience: common.Audience | None = None
    note: str | None = Field(
        None, description="Arth's annotation; grounded before it is sent"
    )


class Nav(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    screen: constr(min_length=1)
    params: dict[str, str] | None = None


class Followup(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    label_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    turn_text: constr(min_length=1)


class Provenance(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: constr(min_length=1)
    count: conint(ge=0) | None = None


class State(StrEnum):
    idle = 'idle'
    listening = 'listening'
    thinking = 'thinking'
    speaking = 'speaking'
    needs_you = 'needs_you'
    done = 'done'
    alert = 'alert'


class Presence(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    state: State
    gaze: str | None = None


class Led(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    pattern: str
    color: str


class Undo(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    command_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    until: AwareDatetime


class Fallback(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    channel: str
    thread: str | None = None


class Envelope(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    turn_id: constr(pattern=r'^turn_[0-9A-HJKMNP-TV-Z]{26}$')
    lang: Lang
    speech: Speech | None = None
    caption: Caption | None = None
    audience: common.Audience
    cards: list[Card]
    nav: Nav | None = None
    followups: list[Followup] = Field(
        ...,
        description='v6: at most 3; UI shows 2–3 chips including screen defaults.',
        max_length=3,
    )
    provenance: list[Provenance]
    presence: Presence
    led: Led | None = None
    tier: common.Tier | None = None
    undo: Undo | None = None
    sensitivity: Sensitivity
    fallback: Fallback | None = None
