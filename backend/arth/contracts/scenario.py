# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Pack(Enum):
    kirana = 'kirana'
    cafe = 'cafe'
    pharmacy = 'pharmacy'
    salon = 'salon'


class Size(Enum):
    micro = 'micro'
    small = 'small'
    medium = 'medium'


class World(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    days: conint(ge=1, le=120) | None = None
    seed: int | None = None
    size: Size | None = None
    patrons: conint(ge=4) | None = None
    cold_start: bool | None = None


class Locale(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    screen: constr(min_length=1) | None = None
    speech: constr(min_length=1) | None = None


class Edition(Enum):
    display = 'display'
    voice = 'voice'


class Surface(Enum):
    device = 'device'
    console = 'console'
    whatsapp = 'whatsapp'
    voice = 'voice'


class Command(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: constr(min_length=1)
    payload: dict[str, Any] | None = None
    approve: bool | None = None
    key: constr(min_length=1, max_length=200) | None = Field(
        None,
        description='Fixed Idempotency-Key, to replay a queued (offline) command; default is a fresh key per command.',
    )


class Action(Enum):
    pay_qr = 'pay_qr'
    pay_static = 'pay_static'
    message = 'message'
    stop = 'stop'
    pay_pending = 'pay_pending'
    complete = 'complete'


class PersonaAction(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    persona: constr(min_length=1)
    action: Action
    bill: constr(min_length=1) | None = None
    text: constr(min_length=1) | None = None
    amount_paise: int | None = None
    outcome: constr(min_length=1) | None = None
    utr: constr(min_length=1) | None = None


class Clock(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    advance_minutes: conint(ge=0) | None = None
    jump_days: conint(ge=0) | None = None


class Rails(Enum):
    duplicate = 'duplicate'
    drop = 'drop'
    delay = 'delay'
    wrong_amount = 'wrong_amount'


class Fault(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    rails: Rails | None = None
    providers_down: bool | None = None


class InputItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    say_for_me: constr(min_length=1) | None = None
    surface: Surface | None = None
    command: Command | None = None
    approve_all: bool | None = None
    persona_action: PersonaAction | None = None
    clock: Clock | None = None
    fault: Fault | None = None
    locale: Locale | None = None
    settle: bool | None = None
    tick: bool | None = None
    read: constr(min_length=1) | None = None


class ExpectTurn(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    intent: constr(min_length=1) | None = None
    speech_contains: constr(min_length=1) | None = None
    presence: constr(min_length=1) | None = None
    nav: constr(min_length=1) | None = None
    tier: constr(min_length=1) | None = None


class ExpectItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    view: constr(min_length=1) | None = None
    path: str | None = None
    equals: Any | None = None
    gte: float | None = None
    lte: float | None = None
    len: conint(ge=0) | None = None
    contains: Any | None = None
    absent: bool | None = None
    invariants: bool | None = None
    sim_thread: constr(min_length=1) | None = None
    outbound_template: constr(min_length=1) | None = None
    present: bool | None = None
    result: str | None = None


class Focus(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    device_screen: constr(min_length=1) | None = None
    phone: constr(min_length=1) | None = None
    customer_display: constr(min_length=1) | None = None
    evidence: constr(min_length=1) | None = None
    table: constr(min_length=1) | None = None
    playbook: constr(min_length=1) | None = None


class Beat(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[0-9a-z.]+$')
    who: constr(min_length=1) | None = None
    cue: constr(min_length=1)
    input: list[InputItem] | None = None
    save: dict[str, str] | None = None
    expect_turn: ExpectTurn | None = None
    expect: list[ExpectItem] | None = None
    within_ms: conint(ge=1) | None = None
    focus: Focus | None = None


class Scene(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[0-9a-z]+$')
    title: constr(min_length=1)
    edition: Edition | None = None
    beats: list[Beat] = Field(..., min_length=1)


class Invariants(Enum):
    default = 'default'
    none = 'none'


class Scenario(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    scenario: constr(pattern=r'^[a-z0-9_]+$')
    title: constr(min_length=1)
    pack: Pack
    world: World
    locale: Locale | None = None
    edition: Edition | None = None
    cut: dict[str, list[str]] | None = None
    scenes: list[Scene] = Field(..., min_length=1)
    invariants: Invariants | None = None
